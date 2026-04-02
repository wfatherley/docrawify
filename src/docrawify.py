"""A simple docstring (de)rawify utility.

Some Python programs have embedded languages in their docstrings, such
as \\\\LaTeX. These may introduce illegal escape sequences and trigger
warnings or exceptions, depending on the Python version. Rawifying
docstrings (i.e. converting ``"this"`` to ``r"that"``) is a quick and
effective solution to avoid the illegal escape character issue. This
library provides a programmatic interface to rawify and de-rawify
docstrings of modules, coroutine and function definitions, and class
and method definitions that exist in Python source files
(``.py`` or ``.pyi``), and Jupyter Notebooks (``.ipynb``).

.. note:: Docstrings bound to objects in specialized ways, such as
    through dynamic class creation with ``builtins.type``, may not be
    (de)rawified.

PIP-installing this library also provides a command line utility,
``pydocrawify``, which accepts file paths, glob patterns, and
directories as arguments. The utility modifies the target files in
place, rawifying or de-rawifying their docstrings depending on the
presence of the ``--remove`` flag.

CLI usage example for rawifying and derawifying a single file:

.. code-block:: console

    $ pydocrawify path/to/file.py
    $ pydocrawify -r path/to/file.ipynb


CLI usage example for rawifying then derawifying a package:

.. code-block:: console

    $ pydocrawify src/
    $ pydocrawify -r src/

"""
import argparse
import ast
import pathlib
import typing

import nbformat


docstringable_types = (
    ast.AsyncFunctionDef,
    ast.FunctionDef,
    ast.ClassDef,
    ast.Module,
)


def load_python_module(path_obj: pathlib.Path) -> tuple[ast.Module, list]:
    """Parse a source file and return its AST and source lines.

    Accept a ``pathlib.Path`` instance representing a Python source
    file, and return a tuple whose first entry is the AST module for
    the source, and whose second entry is a list of source lines. This
    tuple is the basic data structure/media type used by the core
    rawify/derawify logic in the :func:`docrawify.handle_rawify`.

    :param path_obj: a path object representing a source file

    :return tuple[ast.Module, list]:
    """
    with path_obj.open() as f:
        source_lines = f.readlines()
    return ast.parse("".join(s for s in source_lines)), source_lines


def dump_python_module(path_obj: pathlib.Path, source_lines: list) -> None:
    """Write source lines to a Python source file.
    
    Accept a ``pathlib.Path`` instance representing a Python source
    file, and a list of source lines. Write the source lines to the
    file, overwriting the file's previous content.
    
    :param path_obj: a path object representing a source file
    :param source_lines: a list of source lines to write to the file
    
    :return None:
    """
    path_obj.write_text("".join(source_lines))


def load_jupyter_notebook(
    path_obj: pathlib.Path,
) -> tuple[list[ast.Module], list[list]]:
    """Parse a Jupyter Notebook and return its ASTs and sources lines.

    Accept a ``pathlib.Path`` instance representing a Jupyter Notebook
    file, and return a tuple whose first entry is a list of AST modules
    (one for each code cell), and whose second entry is a list of
    source lines lists (one for each code cell). If the tuple is
    zipped, each pair represents a code cell's AST and source lines,
    which tuple is the basic data structure/media type used by the core
    rawify/derawify logic in the :func:`docrawify.handle_rawify`.

    :param path_obj: a path object representing a Jupyter Notebook file

    :return tuple[list[ast.Module], list[list]]:
    """
    notebook = nbformat.read(path_obj, nbformat.NO_CONVERT)
    trees = []
    sources = []
    for cell in notebook.cells:
        if cell["cell_type"] != "code":
            continue
        trees.append(ast.parse(cell["source"]))
        sources.append(cell["source"].split("\n"))
    return trees, sources


def dump_jupyter_notebook(path_obj: pathlib.Path, sources: list[list]) -> None:
    """Write source lines to a Jupyter Notebook file.
    
    Accept a ``pathlib.Path`` instance representing a Jupyter Notebook
    file, and a list of source lines lists. Serially write each source
    lines list to the file's code cells, overwriting the previous
    content.
    
    :param path_obj: a path object representing a source file
    :param source_lines: a list of source lines lists to write
    
    :return None:
    """
    notebook = nbformat.read(path_obj, nbformat.NO_CONVERT)
    for cell in notebook.cells:
        if cell["cell_type"] != "code":
            continue
        cell["source"] = "\n".join(sources.pop(0))
    nbformat.write(notebook, path_obj)


def rawify(
    path_obj: pathlib.Path,
    file_ext: str = None,
    remove: bool = False,
    skip_hook: callable = None
) -> None:
    """Rawify or de-rawify docstrings in a file or directory.

    Accept a ``pathlib.Path`` instance representing a source file (i.e.
    containing valid python) or directory (e.g. a package), and rawify
    or de-rawify all encountered docstrings depending on the value of
    the ``remove`` flag (default ``False``). Modify the files in place.
    When walking a directory, ignore files not having one of ``.py``,
    ``.pyi``, or ``.ipynb`` as its extension. Further, if ``file_ext``
    is provided, ignore files not having it as the extension during the
    walk.

    :param path_obj: source file/directory to modify
    :param file_ext: file extension to filter by when walking
    :param remove: flag to indicate de-rawify
    :param skip_hook: callable evaluating to skip a given docstring

    :return None:
    """
    if path_obj.is_file():
        _rawify(path_obj, remove=remove, skip_hook=skip_hook)
        return
    file_ext = "." + file_ext.lstrip(".") if file_ext is not None else None
    for dir_path, _, file_names in path_obj.walk():
        for file_name in file_names:
            if file_ext is not None and not file_name.endswith(file_ext):
                continue
            sub_path_obj = dir_path / file_name
            _rawify(sub_path_obj, remove=remove, skip_hook=skip_hook)


def _rawify(
    path_obj: pathlib.Path, remove: bool = False, skip_hook: callable = None
) -> None:
    """Resolve a path object's content encoding and (de)rawify.
    
    Determine if the path object represents a Python source file or a
    Jupyter Notebook, and execute the corresponding load pattern (note
    Jupyter Notebooks are lists of modules of ``ast``'s perspective).
    Perform (de)rawify and and dump the modified sources back to the
    file.

    :param path_obj: a path object representing a source file
    :param remove: a flag to indicate rawify or de-rawify
    :param skip_hook: a callable used to skip a docstringable type

    :return None:
    """
    if path_obj.name.endswith((".py", ".pyi")):
        ast_tree, source_lines = load_python_module(path_obj)
        source_lines = handle_rawify(
            ast_tree, source_lines, remove=remove, skip_hook=skip_hook
        )
        dump_python_module(path_obj, source_lines)
    elif path_obj.name.endswith(".ipynb"):
        ast_trees, sources_lines = load_jupyter_notebook(path_obj)
        for k, (tree, source) in enumerate(zip(ast_trees, sources_lines)):
            sources_lines[k] = handle_rawify(
                tree, source, remove=remove, skip_hook=skip_hook
            )
        dump_jupyter_notebook(path_obj, sources_lines)


def handle_rawify(
    ast_tree: ast.Module,
    source_lines: list,
    remove: bool = False,
    skip_hook: callable = None,
) -> list:
    """(De)rawify docstrings in a module and return modified sources.

    Accept and ``ast.Module`` instance and a list of its corresponding
    source lines, and prepend the character ``r`` onto each docstring
    without one, in place. If parameter ``remove`` is set to ``True``
    (default ``False``), remove any ``r`` found prepended to a
    docstring, in place. Return the possibly modified source lines
    list.

    If provided, call parameter ``skip_hook`` with each docstringable
    AST node found in the AST module. If the return value is truthy,
    skip the (de)rawify steps for that node, else do not skip.

    :param ast_tree: an AST module instance
    :param source_lines: a list of source lines
    :param remove: a flag to indicate rawify or de-rawify
    :param skip_hook: a callable used to skip a docstringable type

    :return list:
    """

    # walk the module's tree and accumulate docstrings
    docstring_nodes = []
    for node in ast.walk(ast_tree):
        if not isinstance(node, docstringable_types):
            continue
        if skip_hook is not None and skip_hook(node):
            continue
        docstring_node = get_docstring_node(node)
        if docstring_node is None:
            continue
        docstring_nodes.append(docstring_node)

    # possibly rawify each accumulated docstring
    for docstring_node in docstring_nodes:
        i = docstring_node.lineno - 1
        j = docstring_node.col_offset
        if source_lines[i][j] != "r" and remove is False:
            source_lines[i] = source_lines[i][:j] + "r" + source_lines[i][j:]
        elif source_lines[i][j] == "r" and remove is True:
            source_lines[i] = source_lines[i][:j] + source_lines[i][j + 1:]

    # return possibly modified source list
    return source_lines


def get_docstring_node(node: ast.AST) -> typing.Union[ast.Constant, None]:
    """Return a docstring node if the given node has a docstring.

    Accept an ``ast.AST`` instance, and return the node for its
    docstring if it has one, or return ``None``. Raise ``TypeError`` if
    the given node is not of a type that can have docstrings (e.g. a
    statement node like ``ast.If``).

    :param node: an ``ast.AST`` object to handle

    :return typing.Union(ast.Constant, None):
    """

    # escalate if node doesn't support docstrings
    if not isinstance(node, docstringable_types):
        raise TypeError(f"{node.__class__.__name__} can't have docstrings")

    # otherwise return its docstring node or None
    docstring_node = None
    if not (node.body and isinstance(node.body[0], ast.Expr)):
        return docstring_node
    node = node.body[0].value
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        docstring_node = node
    return docstring_node


# ===== cli ===========================================================
# =====================================================================

args_parser = argparse.ArgumentParser(
    prog="pydocrawify",
    description=(
        'Rawify or de-rawify (using remove flag) docstrings in Python '
        'source files (files with ".py" or ".pyi" extensions) and Jupyter '
        'notebooks (files with ".ipynb" extensions). Specifying a '
        'file or, e.g., *.py glob to has the effect of (de)rawifying the '
        'matching file(s). Specifying a directory has the effect of '
        '(de)rawifying all files in the directory and its subdirectories. '
        'The (de)rawified files are modified in place.'
    ),
)
args_parser.add_argument(
    "-r",
    "--remove",
    action="store_true",
    help="flag indicating that docstrings should be de-rawifyed",
)
args_parser.add_argument(
    "extension",
    nargs="?",
    help=(
        'handle only files with this extension when walking a directory, '
        'one of py, pyi, or ipynb (optional)'
    )
)
args_parser.add_argument(
    "locations", nargs="+", help="file, glob, or directory to (de)rawify"
)


def main() -> None:
    """:return None:"""
    args = args_parser.parse_args()

    for location in args.locations:
        for path_obj in pathlib.Path().glob(location):
            rawify(path_obj, file_ext=args.extension, remove=args.remove)


if __name__ == "__main__":
    main()
