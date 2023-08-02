r"""
Reverse engineer Latex structogram code from a Python function definition.

Latex conventions according to struktex package
https://ctan.org/pkg/struktex

Requires Python >= 3.10

--------------------------------------------------------------------------

Supported statements: while, if-else, assignments, print, pass, match-case
                      x = input(...), x = eval(input(...))

Not supported: if-elif-else, while-else, for, def, return, class, ...

--------------------------------------------------------------------------

# DO-WHILE in structograms

For Python while-loops of shape

   while True:
     ...
     if not cond: break

a structogram will be generated of shape / semantics

   DO
     ...
   WHILE cond

  ___________________
  | |_______________|
  | |_______________|
  | |_______________|
  |     cond        |
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
Note that the Latex package provides a repeat-until markup which
is slighty misused by the do-while semantics used here

See example 2

--------------------------------------------------------------------------

# Input


Python input statements

     x = input(...), x = eval(input(...))

are transformed to Latex code

     Input(x)

See example 3

--------------------------------------------------------------------------

# Match-case

Multiple branches in structograms can be generated using the match-case 
feature of Python >= 3.10. 

While Python's match-case offers powerful pattern matching in general, only
simple case expressions are supported by grampy, e.g. similar to switch-case 
in C++. Conretely, test expressions must be either literals/constants or the 
wildcard pattern '_'.

    match <cond>:
      case <literal1>:
        ...
      case <literal2>:
        ...
      ...
      case _:
        ...

See example 4

--------------------------------------------------------------------------

# Usage

    from grampy import make_structogram

    def fn42():
        ...

    make_structogram(fn42) # auto-generate filename -> structogram_fn42.tex
    # make_structogram(fn42, 'structogram.tex')  # explicit filename

Then, input the generated .tex file into your Latex file:
\input{structogram_fn42.tex}

The main Latex document needs struktex: \usepackage{struktex}

------- minimal example main Latex document
\documentclass[a4paper]{article}
\usepackage[T1]{fontenc}  % \textquotedbl - straight quotation marks
\usepackage{struktex}
\begin{document}
\input{structogram_fn42}
\end{document}
-------

--------------------------------------------------------------------------

# Advanced usage

>>> help(make_structogram)

Help on function make_structogram in module grampy:

make_structogram(func: Callable[[], NoneType], tex_file_name: str = ':auto_gen:'
, dry_run=True, verbose=True) -> None
    Generates a Latex structogram for the function passed as arg.
    
    Parameters:
    -----------
    
    func: function
        A Latex structogram will be generated for func's body.
        func has no arguments and returns None.
    
    tex_file_name: str
        Output file name. If it does not end with '.tex',
        a suitable file name will be auto-generated.
    
    dry_run: bool
        Whether or not to perform a dry run and include its results in the
        Latex document. Not recommended for functions/structograms with
        interactive input (may cause QtConsole, Spyder to crash; execution
        in other shells may be tricky)
 
    verbose: bool

        
    Returns:
    --------
        None

--------------------------------------------------------------------------

# Dry run

The generated Latex file also contains the output resulting from a dry run
execution of the structogram. This output is commented out in the Latex file,
so that it can only be seen in the Latex source but not the compiled document.

Dry runs of structograms with interactive input may not be possible in 
certain Python runtime environments (e.g., Qt console, Spyder).
To disable dry runs:

    make_structogram(fn, dry_run=False)

--------------------------------------------------------------------------    

# Dry run - security issue in library code

The dry run functionality is implemented by temporally redirecting sys.stdout, 
using contextlib.redirect_stdout(new_target)

From the Python doc:
'Note that the global side effect on sys.stdout means that this context
manager is not suitable for use in library code and most threaded
applications. It also has no effect on the output of subprocesses.
However, it is still a useful approach for many utility scripts.'
https://docs.python.org/3/library/contextlib.html

"""

import ast
import contextlib
import inspect
import io

from functools import singledispatch
from typing import Callable, Optional


#
# example 1: while, if-else
#
# make_structogram(fn_while_do)
#


def fn_while_do():
    a = 1
    b = 15
    c = 3
    while c >= -1:
        b = a + b
        a = a - b
        c = c - 2
        if (a < 0) and b <= 1:
            print(' a =', a, ' b =', b)
        else:
            b = b - 2
            a = a - 3
            print(' a =', a, ' c =', c)
    print(' c =', c)


#
# example 2: structogram with 'do ... while' loop
#            generated from Python 'while' loop of a particular shape
#
# This behavior occurs if
# (1) condition for while-loop is the literal 'True'
# (2) the last statement of the while loop's body is: 'if not <cond>: break'
#
# make_structogram(fn_do_while)
#

def fn_do_while():
    limit = 12
    x = 1
    y = 1
    print(x, y)
    while True:
        z = x + y
        print(z)
        x = y
        y = z
        if not y < limit:
            break


#
# example 3: input, structogram with 'do ... while' loop
#
# Note: dry runs of function/structograms with interactive input may not work
# in every environment (e.g., QtConsole, Spyder),
# and may be a bit tricky in others.
#
# # make_structogram(fn_input)
#

def fn_input():
    limit = eval(
        input("What is the upper limit?"))
    x = 1
    y = 1
    print(x, y)
    while True:
        z = x + y
        print(z)
        x = y
        y = z
        if not y < limit:
            break


#
# example 4: match-case (switch-case/multi-branch)
#
# make_structogram(fn_switch_case)
#

def fn_switch_case():
    n = 6
    m = 2
    k = 2
    while n < 10:
        match n % 3:
            case 0:
                n = n - m
                k = k + m
                print('n =', n)
                print('k =', k)
            case 1:
                n = n + k
                m = m + 1
                print('n =', n)
                print('m =', m)
            case _:  # default case
                n = k + 10
                m = m + k
                print('n =', n)
                print('m =', m)
    n = n + m
    n = 2 * n
    print('n =', n)

############################################################


def _to_latex(raw: str) -> str:
    res = raw

    res = res.replace('%', '\\%')
    res = res.replace('{', '\\{')
    res = res.replace('}', '\\}')
    res = res.replace('_', '\\_')
    res = res.replace('&', '\\&')
    res = res.replace('$', '\\$')

    res = res.replace('<=', '$\\leq$')
    res = res.replace('>=', '$\\geq$')
    res = res.replace('<', '\\textless\\ ')
    res = res.replace('>', '\\textgreater\\ ')
    res = res.replace(' not ', ' \\pKey{not} ')
    res = res.replace(' and ', ' \\pKey{and} ')
    res = res.replace(' or ', ' \\pKey{or} ')

    # res = res.replace("'", "\'\'")  # double quotes
    # res = res.replace('"', "\'\'")  # double quotes
    res = res.replace("'", "\\textquotedbl ")  # (straight) double quotes
    res = res.replace('"', "\\textquotedbl ")  # straight) double quotes

    return res


def _while_as_do_while(while_node: ast.AST, source_code) -> Optional[str]:
    """if while-loop has condition 'True'
    and last body statement has shape 'if not <cond>: break'
    then return cond (as source code)
    otherwise return None
    """

    if (
            not isinstance(while_node, ast.While)
            or not isinstance(while_node.test, ast.Constant)
            or while_node.test.value is not True
    ):
        return None

    # is last statement of shape 'if not <cond>: break' ?
    last = while_node.body[-1]  # last statement in while loop's body
    if not isinstance(last, ast.If):
        return None
    if not isinstance(last.body[0], ast.Break):
        return None
    # test must be a unary 'not'
    if not isinstance(last.test, ast.UnaryOp):
        return None
    cond = ast.get_source_segment(source_code, last.test)
    cond = cond.strip()
    if cond[0:3] != 'not':
        return None
    cond = cond[3:]
    cond = cond.strip()
    cond = _to_latex(cond)
    return cond


def _is_input_stmt(assign_node: ast.AST) -> Optional[str]:
    """Test if assign is of shape 'x = input(...)' or 'x = eval(input(...))'.
    If so, return 'Input(x)'. Otherwise return None.
    """
    # assignment? Exactly one assignment?
    if (    not isinstance(assign_node, ast.Assign)
            or len(assign_node.targets) > 1
    ):
        return None

    var_name = assign_node.targets[0].id

    # check that right hand side of the assignment is a function call
    if (    not isinstance(assign_node.value, ast.Call)
            or not isinstance(assign_node.value.func, ast.Name)
    ):
        return None

    # case 'x = input(...)'
    if assign_node.value.func.id == 'input':
        return 'Input(' + var_name + ') \n'
    # case 'x = eval(input(...))'
    if assign_node.value.func.id == 'eval':
        if ( not isinstance(assign_node.value.args[0], ast.Call) \
             or not isinstance(assign_node.value.args[0].func, ast.Name) ):
            return None
        if assign_node.value.args[0].func.id == 'input':
            return 'Input(' + var_name + ')'
    return None


########################################################################

# The abstract syntax tree (ast) of a Python function is recursively traversed
# in order to generate a Latex structogram of the Python function.

# single-dispatch generic function, overloaded on first argument
# https://docs.python.org/3/library/functools.html#functools.singledispatch

@singledispatch
def _traverse(arg: object, _source: str, _level=0) -> str:
    """Generate the Latex structogramm code for an abstract syntax tree
    of a function body. Recursive traversal of the ast.
    """
    if not isinstance(arg, (ast.AST, list)):
        msg = f'Expected ast.AST or list but {arg} has type {type(arg)}'
        raise TypeError(msg)
    return ''


@_traverse.register
def _(children: list, source: str, level=0):
    snippets = [_traverse(item, source, level+1) for item in children]
    return ''.join(snippets)


@_traverse.register
def _(node: ast.Module, source: str, _level=0):
    return _traverse(node.body, source)


@_traverse.register
def _(node: ast.FunctionDef, source: str, level=0):
    # fields: name, args, body, decorator_list, returns
    latex = '% Structogram ' + node.name + ' \n'
    latex += '\\begin{centernss} \n'
    latex += '  \\begin{struktogramm}(120,100) \n'
    latex += _traverse(node.body, source, level)
    latex += '  \\end{struktogramm} \n'
    latex += '\\end{centernss}'
    return latex


@_traverse.register
def _(node: ast.Expr, source: str, level=0):
    rep = ast.get_source_segment(source, node)
    if isinstance(node.value, ast.Call) and node.value.func.id == 'print':
        rep = 'Output' + rep[5:]  # print(...) -> Output(...)
    rep = _to_latex(rep)
    latex = '  ' * level + '\\assign[6]{' + rep + '}\n'
    return latex


@_traverse.register
def _(node: ast.Assign, source: str, level=0):
    # fields: targets, value, type_comment

    # x = input(), x = eval(input())  -> Input(x)
    if _is_input_stmt(node):
        rep = _is_input_stmt(node)
    else:
        rep = ast.get_source_segment(source, node)
    # rep = rep.replace('=', '$\\gets$')  # '<-' instead of '=' ?
    latex = '  ' * level + '\\assign[6]{' + rep + '}\n'
    return latex


@_traverse.register
def _(node: ast.While, source: str, level=0):
    # fields: test, body, orelse
    rep = ast.get_source_segment(source, node.test)

    if _while_as_do_while(node, source):
        # print('-' * 60)
        # print("Generating structogram with DoWhile instead of While!")
        # Note: Struktex provides 'Repeat-Until'-markup
        #       which may be used for either repeat-until or do-while loops.
        #       Grampy's choice is the do-while semantic
        cond = _while_as_do_while(node, source)
        latex = '  ' * level + '\\until[8]{' + cond + '} \n'
        # do not process last body statement 'if not cond: break'
        latex += _traverse(node.body[:-1], source, level+1)
        latex += '  ' * level + '\\untilend \n'

    else:  # 'normal' while
        rep = _to_latex(rep)
        latex = '  ' * level + '\\while[8]{' + rep + '} \n'
        latex += _traverse(node.body, source, level+1)
        latex += '  ' * level + '\\whileend \n'
    return latex


@_traverse.register
def _(node: ast.If, source: str, level=0):
    # fields: test, body, orelse
    rep = ast.get_source_segment(source, node.test)
    rep = _to_latex(rep)
    latex = '  ' * level + '\\ifthenelse{5}{5} \n'
    latex += '  ' * (level+1) + '{' + rep + '} {\\pTrue}{\\pFalse} \n'
    # traverse code for 'true' case
    latex += _traverse(node.body, source, level+1)
    # traverse code for optional 'else' case
    if node.orelse:
        latex += '  ' * level + '\\change \n'
        latex += _traverse(node.orelse, source, level+1)
    else:  # the structogram needs something if 'else' case is missing
        latex += '  ' * level + '\\change \n'
        rep1 = '$\\emptyset$'
        latex += '  ' * (level+2) + '\\assign[6]{' + rep1 + '}\n'

    latex += '  ' * level + '\\ifend \n'
    return latex


@_traverse.register
def _(node: ast.Match, source: str, level=0):
    # fields: subject, cases

    # node.subject contains the test expression
    matchtest = ast.get_source_segment(source, node.subject)
    matchtest = _to_latex(matchtest)
    print('MATCHTEST:', matchtest)
    num_cases = len(node.cases)

    box_height = 12  # height of the Latex box

    # check if there is a default case
    has_default_case = 0
    pattern = node.cases[-1].pattern  # pattern of last case
    if isinstance(pattern, ast.MatchAs) and pattern.name is None:
        has_default_case = 1

    # node.cases contains the multiple branches of the match (switch) statement
    for count, matchcase in enumerate(node.cases):
        pattern = matchcase.pattern

        #
        # if more complex patterns other than constants are wanted:
        # caselatex = '{' + ast.get_source_segment(source, pattern) + '}\n'

        #
        # patterns are restricted to literals/constants and
        # default/otherwise/wildcard case

        if isinstance(pattern, ast.MatchAs) and pattern.name is None:
            has_default_case = 1
            caselatex = '{otherwise}\n'

        elif (isinstance(pattern, ast.MatchValue)
              and isinstance(pattern.value, ast.Constant)):
            constvalue: ast.Constant = pattern.value
            caselatex = f'{ {constvalue.value} }\n'

        else:
            print(type(pattern))
            print('Match pattern is too complex! Please use a constant or "_"')
            return ''

        for stmt in matchcase.body:
            caselatex += _traverse(stmt, source, level+1)

        if count == 0:
            # the first case needs special translation to Latex
            latex = '  ' * level + f'\\case[{box_height}]'
            latex += f'{ {has_default_case} }{ {num_cases} }'
            latex += '{' + matchtest + '}'  # f-string can be error prone here
            latex += caselatex
        elif count == num_cases - 1 and has_default_case:
            # the last case, possibly, needs special translation to Latex
            latex += '  ' * level + '\\switch[r]'
            latex += caselatex
        else:
            # all other cases but the first and last one are handled uniformly
            latex += '  ' * level + '\\switch'
            latex += caselatex

    latex += '  ' * level + '\\caseend \n'
    return latex


@_traverse.register
def _(_node: ast.Pass, _source: str, level=0):
    rep = '$\\emptyset$'
    latex = '  ' * level + '\\assign[6]{' + rep + '}\n'
    return latex


########################################################################

# A dry run is used to include structogram output in the generated tex-file

# dry run functionality is implemented by temporally redirecting sys.stdout
# From the Python doc:
# 'Note that the global side effect on sys.stdout means that this context
# manager is not suitable for use in library code and most threaded
# applications. It also has no effect on the output of subprocesses.
# However, it is still a useful approach for many utility scripts.'

def _dry_run(func: Callable[[], None]) -> str:
    """executes the function func and returns all print outputs - that would
    usually be written to sys.stdout - in a string.
    """
    with contextlib.redirect_stdout(io.StringIO()) as tmpout:
        # execute func ... print output is now written to string stream tmpout
        func()
    return tmpout.getvalue()


# alternative dry run implementation
#
# modifies the ast of the user-defined function, effectively replacing
#   print('something')
# with
#   print('something', file='mylatexfile.tex')
#
# -- gives W0122 linter warning (use of exec), but is thread-safe

# def _dry_run(func: Callable[[], None]) -> str:
#     """executes the function func and returns all print outputs - that would
#     usually be written out to sys.stdout - in a string.
#     """

#     def modify_print(node):
#         if isinstance(node, ast.Call):
#             if node.func.id == 'print':
#                 name_node = ast.Name('file', ast.Load())
#                 keyword_node = ast.keyword('file', name_node)
#                 node.keywords.append(keyword_node)
#                 ast.fix_missing_locations(node)
#         for childnode in ast.iter_child_nodes(node):
#             modify_print(childnode)

#     source = inspect.getsource(func)
#     tree = ast.parse(source)
#     func_node = tree.body[0]

#     # rename the function + add 'file' arg
#     func_node.name = "_renamed"
#     file_arg = ast.arg('file')
#     func_node.args.args.append(file_arg)
#     ast.fix_missing_locations(func_node.args)

#     # add 'file' arg to all print calls in the function
#     modify_print(func_node)

#     # execute the modified function with print output redirected to a stream
#     strstream = io.StringIO()
#     call_node = ast.parse('_renamed(strstream)').body[0]
#     tree.body.append(call_node)
#     code = compile(tree, '<transformed>', 'exec')
#     exec(code)

#     res = strstream.getvalue()
#     strstream.close()

#     return res


########################################################################

def make_structogram(func: Callable[[], None],
                     tex_file_name: str = ':auto_gen:',
                     dry_run=True,
                     verbose=True) -> None:
    """Generates a Latex structogram for the function passed as arg.

    Parameters:
    -----------

    func: function
        A Latex structogram will be generated for func's body.
        func has no arguments and returns None.

    tex_file_name: str
        Output file name. If it does not end with '.tex',
        a suitable file name will be auto-generated.

    dry_run: bool
        Whether or not to perform a dry run and include its results in the
        Latex document. Not recommended for functions/structograms with
        interactive input (may cause QtConsole, Spyder to crash; execution
        in other shells may be tricky)

    verbose: bool

    Returns:
    --------
        None

   """

    # where do we write the file to?
    if not tex_file_name.endswith('.tex'):
        tex_file_name = 'structogram_' + func.__name__ + '.tex'

    # generate Latex code of the structogram;
    source = inspect.getsource(func)
    tree = ast.parse(source)
    latex = _traverse(tree, source)

    # dry run to collect print output
    lines = ''
    if dry_run:
        printoutput = _dry_run(func)
        lines = printoutput.split('\n')[:-1]

    # write Latex file

    with open(tex_file_name, 'w', encoding='utf-8') as tex_file:

        # write Python code to Latex file (commented out in Latex)
        for line in source.split('\n'):  # source code of Python function
            print('% ' + line, file=tex_file)
        print('\n', file=tex_file)

        # write Latex structogram
        print(latex, file=tex_file)
        print('\n', file=tex_file)

        # write dry-run results (commented out in Latex)
        if dry_run:
            print("% Output of structogram", func.__name__,
                  end=' ', file=tex_file)
            print(f'({len(lines)} lines)', file=tex_file)
            for line_no, line in enumerate(lines):
                print(f'% [{line_no+1:02}]', line, file=tex_file)
        else:
            print("% No structogram output generated (dry_run=False)",
                  file=tex_file)

    # +++++++++ write some infos to sys.stdout
    if verbose:
        print('-' * 60)
        print(latex)
        print('-' * 60)
        if dry_run:
            print("Output of function/structogram", func.__name__, end=' ')
            print(f'({len(lines)} lines)')
            for line in lines:
                print(line)
        else:
            print("No structogram output generated (dry_run=False)")
        print('-' * 60)

    print('Wrote', tex_file_name)


if __name__ == '__main__':
    make_structogram(fn_while_do)  # function fn_while_do defined above
    make_structogram(fn_do_while)
    make_structogram(fn_switch_case)

    # function with interactive input -> no dry run)
    fn = fn_input
    make_structogram(fn, dry_run=False, verbose=True)
