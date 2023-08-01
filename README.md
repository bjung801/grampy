# grampy
Reverse engineer Latex structogram code from a Python function definition.

Latex conventions according to struktex package
https://ctan.org/pkg/struktex

Requires Python >= 3.10.

Do not use as library code. See security note below.

> *Example 1: while-do*

![image](https://github.com/bjung801/grampy/assets/129518187/4232f66d-9d8a-4967-9118-16c950cabc0e)



--------------------------------------------------------------------------

##### Supported Python statements: 

    while, if-else, assignments, print, pass, match-case
    x = input(...), x = eval(input(...))

##### Not supported: 

    if-elif-else, while-else, for, def, return, class, ...
               
--------------------------------------------------------------------------

### DO-WHILE in structograms

Python does not feature a do-while loop. However, 
for Python while-loops of shape

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

Note that the Struktex Latex package provides a repeat-until markup which
is used with the different do-while semantics here.

See example 2

--------------------------------------------------------------------------

### Input


Python input statements

     x = input(...), x = eval(input(...))

are transformed to Latex code

     Input(x)

See example 3

--------------------------------------------------------------------------

### Match-case

Multiple branches in structograms can be generated using the match-case 
feature of Python >= 3.10. 

While Python's match-case offers powerful pattern matching in general, only
simple case expressions are supported by grampy, e.g. similar to switch-case 
in C++. Concretely, test expressions must be either literals/constants or the 
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

Then, input the generated .tex file into your Latex file:
\input{structogram_fn42.tex}

The main Latex document needs struktex: \usepackage{struktex}

##### minimal example main Latex document

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
        Latex document. Not recommended for functions/structograms with
        interactive input (may cause QtConsole, Spyder to crash; execution
        in other shells may be tricky)
 
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

Dry runs of structograms with interactive input may not be possible in 
certain Python runtime environments (e.g., Qt console, Spyder).
To disable dry runs:

    make_structogram(fn, dry_run=False)

--------------------------------------------------------------------------    

### Dry run - security issue in library code

The dry run functionality is implemented by temporally redirecting sys.stdout, 
using contextlib.redirect_stdout(new_target)

From the Python doc:

*'Note that the global side effect on sys.stdout means that this context
manager is not suitable for use in library code and most threaded
applications. It also has no effect on the output of subprocesses.
However, it is still a useful approach for many utility scripts.'*

https://docs.python.org/3/library/contextlib.html

--------------------------------------------------------------------------    

### More examples

> *Example 2: do-while*

![image](https://github.com/bjung801/grampy/assets/129518187/f4ea3860-f9be-496f-b7e5-b2ad3b0177d2)

> *Example 3: input*

![image](https://github.com/bjung801/grampy/assets/129518187/3c9aa266-4d79-423d-88a2-5cff204b316d)

> *Example 4: switch-case*

![image](https://github.com/bjung801/grampy/assets/129518187/d202105f-2263-4eab-b0c6-8b53527a11e0)



