# `docrawify` -- rawify and de-rawify docstrings

<hr>

## Summary
Rawify or derawify docstrings in `.py` and `.ipynb` files, either through command line or programatically. The term "docstring" refers to strings at the very top of module, class, method, coroutine, and function definitions. Strings that become docstrings during runtime, such as through dynamic class creation, are not modified by tools in library.

## Usage
CLI usage (after `pip` install) for rawifying or derawifying a single file or sets of files:

```shell
$ # single file usage
$ pydocrawify path/to/file.py
$ pydocrawify -r path/to/file.py
$
$ # all notebooks in cwd
$ pydocrawify *.ipynb
$ pydocrawify -r *.ipynb
$
$ # does nothing (no .py(i) or .ipynb extension)
$ pydocrawify ~/.ssh/*
$
$ # # all .py(i) and .ipynb files in cwd
$ pydocrawify *
$ pydocrawify -r *
```

CLI usage for rawifying then derawifying a package/tree (based on `os.walk`):

```shell
$ # all .py(i) and .ipynb files in entire tree rooted at src
$ pydocrawify src/
$ pydocrawify -r src/
$
$ # only .py files in entire tree rooted at src
$ pydocrawify py src/
$ pydocrawify -r py src/
$
$ # only .py files in entire tree rooted at src
$ pydocrawify pyi src/
$ pydocrawify -r pyi src/
$
$ # only .ipynb in files entire tree rooted at src
$ pydocrawify ipynb src/
$ pydocrawify -r ipynb src/
```

Programmatic usage is based on `pathlib.Path` objects. Here are two usage examples:

```python
import pathlib

import docrawify


# high level patterns
# ===================

# rawify/de-rawify single file
file_obj = pathlib.Path("path/to/mypymod.py")
docrawify.rawify(file_obj)
docrawify.rawify(file_obj, remove=True)

# rawify/de-rawify .py(i) and .ipynb files in a tree of files
file_obj = pathlib.Path("path/to/mypackage")
docrawify.rawify(file_obj)
docrawify.rawify(file_obj, remove=True)


# low level pattern
# =================

file_obj = pathlib.Path("path/to/mypymod.py")

# low-level "transfer encoding" of ast tree and source lines
ast_tree, source_lines = docrawify.load_python_module(file_obj)

# rawify (produce new source lines with docstrings rawified)
rawified_source_lines = docrawify.handle_rawify(ast_tree, source_lines)

# overwrite the file with rawified source lines
docrawify.dump_python_module(file_obj, rawified_source_lines)

```

See [reference documentation]() for more information on the programmatic API.

## More information
Some Python programs have embedded languages in their docstrings, such as \\\\LaTeX. These may introduce illegal escape sequences and trigger warnings or exceptions, depending on the Python version. Rawifying docstrings (i.e. converting `"this"` to `r"that"`) is a quick and effective solution to avoid the illegal escape character issue. This library provides a programmatic interface to rawify and de-rawify docstrings of modules, coroutine and function definitions, and class and method definitions that exist in Python source files (`.py` or `.pyi`), and Jupyter Notebooks (`.ipynb`).

PIP-installing this library also provides a command line utility, `pydocrawify`, which accepts file paths, glob patterns, and directories as arguments. The utility modifies the target files in place, rawifying or de-rawifying their docstrings depending on the presence of the `--remove` flag.

## Install
PIP-installable from GitHub repository.

## Contribute
Yes, please. All contributions are welcome and encouraged.

## License
MIT
