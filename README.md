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

###Merging decisions:

Merge numbers based on relative position, relative size, continue until none left

1. find opening bracket move right until matching bracket, repeat until no opening bracket
2. find square root: find all elements within its y and x range, repeat until no square root
3. Group numbers by size, perform below operations on smallest group. Then merge that group with it's base, and continue with second smallest group until 1 group left -> go to clean up
4. Group numbers by relative y position, perform 5. on all groups

5. Find multiplication operators, 
	- if no mulitiplication operator: merge whatever is there by repeating 5, but looking for + or -.
	- if 1 multiplication operator: merge left side and right side
	- if 2 or more multiplication operator: merge left side and right side of first, then merge with first multiplication operator itself and go to 5. 

6. Merge fractions

Clean up:
Take merged group, merge it with square root if exists, merge it with brackets if exist, repeat process from top.
