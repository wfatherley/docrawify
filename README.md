# `docrawify` -- rawify and de-rawify docstrings

<hr>

## Summary
Rawify or derawify docstrings in `.py` and `.ipynb` files, either through command line or programatically. The term "docstring" here refers to strings at the very top of module, class, coroutine, and function definitions. Strings that become docstrings during runtime, such as through dynamic class creation, are not modified by tools in library.

## More information
Some Python programs have embedded languages in their docstrings, such as \\\\LaTeX. These may introduce illegal escape sequences and trigger warnings or exceptions, depending on the Python version. Rawifying docstrings (i.e. converting `"this"` to `r"that"`) is a quick and effective solution to avoid the illegal escape character issue. This library provides a programmatic interface to rawify and de-rawify docstrings of modules, coroutine and function definitions, and class and method definitions that exist in Python source files (`.py` or `.pyi`), and Jupyter Notebooks (`.ipynb`).

PIP-installing this library also provides a command line utility, `pydocrawify`, which accepts file paths, glob patterns, and directories as arguments. The utility modifies the target files in place, rawifying or de-rawifying their docstrings depending on the presence of the `--remove` flag.

## Usage
CLI usage for rawifying or derawifying a single file:

```shell
$ pydocrawify path/to/file.py
$ pydocrawify -r path/to/file.ipynb
```

CLI usage for rawifying then derawifying a package:

```shell
$ pydocrawify src/
$ pydocrawify -r src/
$
$ # just .py files, no .ipynb
$ pydocrawify *.py
```

Programmatic usage is based on `pathlib.Path` objects:

```python
import pathlib

import docrawify


my_pymod_file = pathlib.Path("path/to/mypymod.py)

# rawify docstrings
docrawify.rawify(my_pymod_file)

# derawify docstring
docrawify.rawify(my_pymod_file, remove=True)
```

See [reference documentation]() for more information on the programmatic API.

## Install
PIP-installable from GitHub repository.

## Contribute
Yes, please. All contributions are welcome and encouraged.

## License
MIT
