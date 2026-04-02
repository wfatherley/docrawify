"""docrawify's unit tests"""
import ast
import unittest

import nbformat

import docrawify

from . import PathDouble, test_files_map


class TestDocstringableTypes(unittest.TestCase):
    """unit tests against ast's docstringable types"""

    def test_has_four_docstringable_ast_types(self):
        """verify there are four docstringable ast types"""
        self.assertEqual(
            docrawify.docstringable_types,
            (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)
        )


class TestLoadPythonModule(unittest.TestCase):
    """unit tests against docrawify.load_python_module"""

    def test_source_lines_are_returned(self):
        """verify source lines are returned without modification"""
        path_obj = PathDouble("not_raw.py")
        _, source = docrawify.load_python_module(path_obj)
        self.assertEqual(test_files_map["not_raw.py"], "".join(source))

    def test_asts_are_returned(self):
        """verify module ast is returned without modification"""
        path_obj = PathDouble(test_files_map["not_raw.py"])
        tree, _ = docrawify.load_python_module(path_obj)
        true_tree = ast.parse(test_files_map["not_raw.py"])
        for n1, n2 in zip(ast.walk(tree), ast.walk(true_tree)):
            self.assertEqual(type(n1), type(n2)) 


class TestLoadJupyterNotebook(unittest.TestCase):
    """unit tests against docrawify.load_jupyter_notebook"""
    
    def test_source_lines_are_returned(self):
        """verify source lines are returned without modification"""
        path_obj = PathDouble("not_raw.ipynb")
        _, sources = docrawify.load_jupyter_notebook(path_obj)
        nb = nbformat.reads(test_files_map["not_raw.ipynb"], nbformat.NO_CONVERT)
        for cell, source in zip([c for c in nb.cells if c["cell_type"] == "code"], sources):
            self.assertEqual(cell["source"], "\n".join(source))

    def test_asts_are_returned(self):
        """verify module ast is returned without modification"""
        path_obj = PathDouble("not_raw.ipynb")
        trees, _ = docrawify.load_jupyter_notebook(path_obj)
        nb = nbformat.reads(test_files_map["not_raw.ipynb"], nbformat.NO_CONVERT)
        for true_tree, tree in zip(
            [ast.parse(c["source"]) for c in nb.cells if c["cell_type"] == "code"],
            trees
        ):
            for n1, n2 in zip(ast.walk(true_tree), ast.walk(tree)):
                self.assertEqual(type(n1), type(n2))


class TestDumpPythonModule(unittest.TestCase):
    """unit tests against docrawify.dump_python_module"""
    
    def test_source_round_trips(self):
        """verify source lines are written without modification"""
        path_obj = PathDouble("not_raw.py")
        _, source = docrawify.load_python_module(path_obj)
        docrawify.dump_python_module(path_obj, source)
        self.assertEqual(path_obj.out_data, test_files_map["not_raw.py"])


class TestDumpJupyterNotebook(unittest.TestCase):
    """unit tests against docrawify.dump_jupyter_notebook"""

    def test_notebook_round_trips(self):
        """verify source lines are written without modification"""
        path_obj = PathDouble("not_raw.ipynb")
        _, sources = docrawify.load_jupyter_notebook(path_obj)
        docrawify.dump_jupyter_notebook(path_obj, sources)
        self.assertEqual(path_obj.out_data, test_files_map["not_raw.ipynb"])


class TestRawifyStack(unittest.TestCase):
    """unit tests against docrawify.(rawify, _rawify, handle_rawify)"""
    
    def test_single_module_is_rawified(self):
        """verify a single module is rawified"""
        path_obj = PathDouble("not_raw.py")
        docrawify.rawify(path_obj)
        self.assertEqual(path_obj.out_data, test_files_map["raw.py"])

    def test_single_notebook_is_rawified(self):
        """verify a single notebook is rawified"""
        path_obj = PathDouble("not_raw.ipynb")
        docrawify.rawify(path_obj)
        self.assertEqual(path_obj.out_data, test_files_map["raw.ipynb"])

    def test_single_module_is_derawified(self):
        """verify a single module is de-rawified"""
        path_obj = PathDouble("raw.py")
        docrawify.rawify(path_obj, remove=True)
        self.assertEqual(path_obj.out_data, test_files_map["not_raw.py"])

    def test_single_notebook_is_derawified(self):
        """verify a single notebook is de-rawified"""
        path_obj = PathDouble("raw.ipynb")
        docrawify.rawify(path_obj, remove=True)
        self.assertEqual(path_obj.out_data, test_files_map["not_raw.ipynb"])

    def test_single_incompatible_file_is_skipped(self):
        """verify a single incompatible file is skipped"""
        path_obj = PathDouble("fake_data.json")
        docrawify.rawify(path_obj)
        self.assertEqual(path_obj.out_data, None)

    def test_directory_is_walked_and_files_are_rawified_or_derawified(self):
        """verify a directory is walked and files are rawified or derawified"""
        path_obj = PathDouble("fakedir")
        docrawify.rawify(path_obj)
        for po in path_obj.dir_files:
            if po.name == "fake_data.json":
                self.assertEqual(po.out_data, None)
            elif po.name == "not_raw.py":
                self.assertEqual(po.out_data, test_files_map["raw.py"])
            elif po.name == "raw.py":
                self.assertEqual(po.out_data, test_files_map["not_raw.py"])
            elif po.name == "not_raw.ipynb":
                self.assertEqual(po.out_data, test_files_map["raw.ipynb"])
            elif po.name == "raw.ipynb":
                self.assertEqual(po.out_data, test_files_map["not_raw.ipynb"])
            else:
                self.fail(f"unexpected file {po.name} found in directory walk")

    def test_skip_hook_skips(self):
        """verify the skip hook is called and respected"""
        path_obj = PathDouble("not_raw.py")
        docrawify.rawify(path_obj, skip_hook=lambda _: True)
        self.assertEqual(path_obj.out_data, test_files_map["not_raw.py"])

    def test_file_ext_skips_rawify(self):
        """verify file extensions are respected when rawifying"""
        path_obj = PathDouble("fakedir")
        docrawify.rawify(path_obj, file_ext="ipynb")
        for po in path_obj.dir_files:
            if po.name.ednswith(".py"):
                self.assertEqual(po.out_data, None)
            elif po.name == "not_raw.ipynb":
                self.assertEqual(po.out_data, test_files_map["raw.ipynb"])
            elif po.name == "fake_data.json":
                self.assertEqual(po.out_data, None)


class TestGetDocstringNode(unittest.TestCase):
    """unit tests against docrawify.get_docstring_node"""
    
    def test_raises_when_no_docstring_node_is_found(self):
        """verify an error is raised when no docstring node is found"""
        with self.assertRaises(TypeError):
            docrawify.get_docstring_node(ast.If("1 == 1"))

    def test_return_none_when_ast_node_has_no_docstring(self):
        """verify None is returned when an ast node has no docstring"""
        is_none = docrawify.get_docstring_node(
            ast.Module(body=[ast.Expr(value=ast.If("1 == 1"))])
        )
        self.assertEqual(is_none, None)
