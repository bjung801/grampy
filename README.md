# grampy
Reverse engineer Latex structograms (a.ka. Nassi–Shneiderman diagrams) from a Python function definition.

Latex markup according to struktex package
https://ctan.org/pkg/struktex

Requires Python >= 3.10.

Limitations: Grampy can generate structograms from reasonably simple Python code. 
Like other programming languages, Python offers many features that cannot be represented in structograms 
(e.g., elements of object-oriented, functional and aspect-oriented programming; 
or simply long code that does not fit into one diagram).
Grampy is therefore not intended to and cannot reverse engineer structograms from arbitrary Python programs. 
Use with having the resulting structogram's complexity in mind.

Recommended use: Write your Python function first. Tweak and test until the desired behavior is achieved. 
Then have grampy reverse engineer the structogram. 
Check if the structogram looks nice. If not, consider modifying the Python code. 
E.g., long descriptive variable names may be advantageous in production Python code 
whereas in structograms short names may better fit the sometimes narrow boxes.
You may also consider to modify the generated Latex file directly to adapt the structogram's layout.

Do not include grampy in library code, unless removing the dry run functionality. See security note below.

> *Example 1: while-do*

![image](https://github.com/bjung801/grampy/assets/129518187/376531b7-1441-4886-b8f3-89c54b7029d2)




--------------------------------------------------------------------------

##### Supported Python statements: 

    while, if-else, simple assignments, print, pass, match-case
    x = input(...), x = eval(input(...))

##### Not supported: 

    if-elif-else, while-else, for, def, return
    class, import, assert, try-catch, with, async, type annotations, decorators, ...
               
--------------------------------------------------------------------------

### DO-WHILE in structograms

Python does not feature a do-while loop. However, 
for Python while-loops of shape ...

    while True:
      ...
      if not cond: break

... a structogram will be generated of shape / semantics:

    DO
      ...
    WHILE cond

    ___________________
    | |_______________|
    | |_______________|
    | |_______________|
    |     cond        |
    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

Note that the Struktex Latex package provides a repeat-until markup which
is used here with the different do-while semantics.

See example 2

--------------------------------------------------------------------------

### Input


Python input statements

     x = input(...)
     x = eval(input(...))

are transformed to Latex code

     Input(x)

See example 3

--------------------------------------------------------------------------

### Match-case

Multiple branches in structograms can be generated using the match-case 
feature of Python >= 3.10. 

While Python's match-case offers powerful pattern matching, only
simple case expressions are supported by grampy, similar, e.g., to switch-case 
in C++/Java. Concretely, test expressions must be either literals/constants or the 
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

### Usage

    from grampy import make_structogram

    def fn42():
        ...

    make_structogram(fn42) # auto-generate filename -> structogram_fn42.tex
    
    # make_structogram(fn42, 'structogram.tex')  # explicit filename

Then, include the generated .tex file into your main Latex file:
`\input{structogram_fn42}`

The main Latex document needs struktex `\usepackage{struktex}` 
and fontenc `\usepackage[T1]{fontenc}`

> *minimal example main Latex document*

    \documentclass[a4paper]{article}
    \usepackage[T1]{fontenc}  % \textquotedbl - straight quotation marks
    \usepackage{struktex}
    \begin{document}
    \input{structogram_fn42}
    \end{document}


--------------------------------------------------------------------------

### Advanced usage

    >>> help(make_structogram)

    Help on function make_structogram in module grampy:

    make_structogram(func: Callable[[], NoneType], tex_file_name: str = ':auto_gen:', dry_run=True, verbose=True) -> None
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
        Latex document. Dry run results are commented out in the Latex
        source file, so that they are not shown in the compiled document.
        Dry run functionality may not work in some Python shells for
        structograms/functions with interactive input.
        
    verbose: bool

        
    Returns:
    --------
        None

--------------------------------------------------------------------------

### Dry run

The generated Latex file also contains the output resulting from a dry run
execution of the structogram. This output is commented out in the Latex file,
so that it can only be seen in the Latex source but not the compiled document.

    % Output of structogram fn_while_do (4 lines)
    % [01]  a = -18  c = 1
    % [02]  a = -14  b = -4
    % [03]  a = 1  c = -3
    % [04]  c = -3

Dry runs of structograms with interactive input may not work in 
some Python runtime environments, particularly when multiple
structograms are generated.
In this case, disable dry runs:

    make_structogram(fn, dry_run=False)

--------------------------------------------------------------------------    

### Dry run - security issue in library code

The dry run functionality is implemented by temporally redirecting sys.stdout, 
using `contextlib.redirect_stdout(new_target)`

From the Python documentation:

*'Note that the global side effect on sys.stdout means that this context
manager is not suitable for use in library code and most threaded
applications. It also has no effect on the output of subprocesses.
However, it is still a useful approach for many utility scripts.'*

https://docs.python.org/3/library/contextlib.html

--------------------------------------------------------------------------    

### More examples

> *Example 2: do-while*

![image](https://github.com/bjung801/grampy/assets/129518187/f4ea3860-f9be-496f-b7e5-b2ad3b0177d2)

    % Output of structogram fn_do_while (6 lines)
    % [01] 1 1
    % [02] 2
    % [03] 3
    % [04] 5
    % [05] 8
    % [06] 13


> *Example 3: input*

![image](https://github.com/bjung801/grampy/assets/129518187/dbeb456a-f199-4687-81eb-b49ec52c9ea0)


    % No structogram output generated (dry_run=False)

or with `dry_run=True` (default)

    % Output of structogram fn_input (7 lines)
    % [01] limit = 13
    % [02] 1 1
    % [03] 2
    % [04] 3
    % [05] 5
    % [06] 8
    % [07] 13

> *Example 4: switch-case*

![image](https://github.com/bjung801/grampy/assets/129518187/d202105f-2263-4eab-b0c6-8b53527a11e0)

    % Output of structogram fn_switch_case (7 lines)
    % [01] n = 4
    % [02] k = 4
    % [03] n = 8
    % [04] m = 3
    % [05] n = 14
    % [06] m = 7
    % [07] n = 42


