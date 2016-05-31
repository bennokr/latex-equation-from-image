LaTeX Equation from Image
=========================

LaTeX equation OCR


Requirements
------------
- [tex2im](http://www.nought.de/tex2im.php) for data generation (dep: latex, imagemagick, ghostscript)
- [plastex](http://plastex.sourceforge.net/plastex/) for data generation and AST representation
- skimage: `pip install scikit-image`


##Solution
1. Segment image and find all components
2. Merge some multi-part symbols based on rules
	- Classify all symbols with "component-classifier" trained on parts from this list: `= i j  " : ; ! ?` NB: this list is not yet comprehensive
	- Merge symbols that are close, part of a symbol and are classified correctly after merging
3. Classify all symbols
4. Describe all relations between symbols with some features (size ratio, both symbols themselves, type of symbols [number, operator, punctuation mark], relative position)
5. Make merging decisions based on this, first merge all numbers (1 2 3 to 123), then relations between them (the sequential "number * number" to node "(* number number)"). Use prior knowledge about math precedence in merging decisions.
7. Think about how to deal with sums, limits, integrals etc
