"""
Converts a LaTeX math expression to a tex document that logs symbol
positions, then compiles it 

Requirements
- plasTeX (python)
- standalone >1.0 (latex)

"""

from plasTeX.TeX import TeX
import sys, subprocess, os, re
import skimage.io

def source_tree(node):
    if node.childNodes:
        return (node.nodeName, map(source_tree, node.childNodes))
    if node.attributes:
        if node.nodeName in ['left', 'right']:
            return node.source
        att = [map(source_tree, v) for v in node.attributes.values()]
        return tuple([node.nodeName] + att)
    else:
        return node.source

def get_tree(code):
    tex = TeX()
    tex.input('$%s$'%code)
    return source_tree(tex.parse().firstChild)

def get_code(tree):
    if type(tree) == tuple:
        parent = tree[0]
        if parent == 'math':
            return '$%s$' % ''.join(get_code(c) for c in tree[1] )
        else:
            children = ['{%s}' % ''.join(map(get_code, c)) for c in tree[1:]]
            children = ''.join(children)
            if parent.startswith('active::'):
                return parent.replace('active::','') + children
            else:
                return '\\%s' % parent + children
    else:
        return str(tree)

def savepos_symbols(command, index):
    """ Adds a LaTeX position saving command for all symbols"""

    new = [command[0]]
    for attr in command[1:]:
        new_list = []
        for node in attr:
            if type(node) == tuple:
                index, new_node = savepos_symbols(node, index)
                new_list += [("savepos", [str(index)]),  new_node]
                index += 1
            elif node.strip():
                if len(node) > 1 and not node.startswith('\\'):
                    for symbol in node:
                        new_list += [("savepos", [str(index)]), symbol]
                        index += 1
                else:
                    new_list += [("savepos", [str(index)]), node]
                    index += 1
        new.append( new_list )
    return index, tuple(new)

def render_positions(code):
    nodes, new_command = savepos_symbols(get_tree(code), 0)

    tex = r"""
    \documentclass{standalone}
    \newcommand*{\savepos}[1]{
      \pdfsavepos\write-1{SAVED POSITION: #1 \the\pdflastxpos,\the\pdflastypos}
    }
    \begin{document}
    """ + get_code(new_command) + """
    \end{document}
    """

    # FILE HANDLING
    tmp_name = str( cmp(hash(code), 0) * hash(code) )
    with open('%s.tex'%tmp_name, 'w') as f:
        f.write(tex)
    DEVNULL = open(os.devnull, 'wb')
    subprocess.call(["pdflatex", '%s.tex'%tmp_name], stdout=DEVNULL)
    with open('%s.log'%tmp_name) as o:
        lines = o.readlines()
    density, quality = 300, 90
    subprocess.call(['convert', 
        '-density', str(density), '%s.pdf'%tmp_name, 
        '-quality', str(quality), '%s.png'%tmp_name
    ])
    im = skimage.io.imread('%s.png'%tmp_name)
    exts = ['log', 'tex', 'aux', 'pdf', 'png']
    subprocess.call(['rm'] + ['%s.%s'%(tmp_name,ext) for ext in exts])

    # POSITION EXTRACTION
    pos = r'SAVED POSITION: (\d+) (\d+),(\d+)'
    positions = [m.groups() for l in lines for m in [re.match(pos, l)] if m]
    # 2^{16}sp = 1pt, 72.27pt=1in, 300 dpi => 2**16 / 72 / 300
    scale = 2**16  / (300 / 72.)
    positions = {int(n): (int(x)/scale,int(y)/scale) for n,x,y in positions}

    return new_command, im, positions

if __name__ == '__main__':
    code = sys.argv[1]
    new_command, im, positions = render_positions(code)
    print new_command
    print positions