"""docstring automated tests"""
import contextlib
import io

import nbformat


dummy_module_source = """
'''dummy module'''
import this

def f():
    pass

async def async_f():
    pass

async def async_f_with_args(x, y):
    ''''''
    await async_f()

'''dummy constant'''

def g():
    '''g, a function'''
    return 3

class MyClass:
    '''my class'''

    def h(self, i):
        pass

    @staticmethod
    def p(q):
        '''return q'''
        return q

    async def async_m(self):
        '''doc'''
        await async_f()
""".strip()


rawified_dummy_module_source = """
r'''dummy module'''
import this

def f():
    pass

async def async_f():
    pass

async def async_f_with_args(x, y):
    r''''''
    await async_f()

'''dummy constant'''

def g():
    r'''g, a function'''
    return 3

class MyClass:
    r'''my class'''

    def h(self, i):
        pass

    @staticmethod
    def p(q):
        r'''return q'''
        return q

    async def async_m(self):
        r'''doc'''
        await async_f()
""".strip()


dummy_notebook_source = nbformat.v4.new_notebook(cells=[
    nbformat.v4.new_code_cell(
        id="0",
        source="'''dummy module'''\nimport this\n\n\ndef f():\n    pass"
    ),
    nbformat.v4.new_code_cell(
        id="1",
        source="\n".join(
            [
                "'''another dummy module'''",
                "import this",
                "",
                "def f():",
                "    pass",
                "",
                "async def async_f():",
                "    pass",
                "",
                "async def async_f_with_args(x, y):",
                "    ''''''",
                "    await async_f()",
                "",
                "'''dummy constant'''",
                "",
                "def g():",
                "    '''g, a function'''",
                "    return 3",
                "",
                "class MyClass:",
                "    '''my class'''",
                "",
                "    def h(self, i):",
                "        pass",
                "",
                "    @staticmethod",
                "    def p(q):",
                "        '''return q'''",
                "        return q",
                "",
                "    async def async_m(self):",
                "        '''doc'''",
                "        await async_f()"
            ]
        )
    )
])
dummy_notebook_source = nbformat.writes(dummy_notebook_source)


rawified_dummy_notebook_source = nbformat.v4.new_notebook(cells=[
    nbformat.v4.new_code_cell(
        id="0",
        source="r'''dummy module'''\nimport this\n\n\ndef f():\n    pass"
    ),
    nbformat.v4.new_code_cell(
        id="1",
        source="\n".join(
            [
                "r'''another dummy module'''",
                "import this",
                "",
                "def f():",
                "    pass",
                "",
                "async def async_f():",
                "    pass",
                "",
                "async def async_f_with_args(x, y):",
                "    r''''''",
                "    await async_f()",
                "",
                "'''dummy constant'''",
                "",
                "def g():",
                "    r'''g, a function'''",
                "    return 3",
                "",
                "class MyClass:",
                "    r'''my class'''",
                "",
                "    def h(self, i):",
                "        pass",
                "",
                "    @staticmethod",
                "    def p(q):",
                "        r'''return q'''",
                "        return q",
                "",
                "    async def async_m(self):",
                "        r'''doc'''",
                "        await async_f()"
            ]
        )
    )
])
rawified_dummy_notebook_source = nbformat.writes(rawified_dummy_notebook_source)


json_file = '[{"obj_id": 1}]'


test_files_map = {
    "not_raw.py": dummy_module_source,
    "raw.py": rawified_dummy_module_source,
    "not_raw.ipynb": dummy_notebook_source,
    "raw.ipynb": rawified_dummy_notebook_source,
    "fake_data.json": json_file
}


class PathDouble:
    """pathlib.Path test double"""

    def __truediv__(self, other):
        self.dir_files.append(PathDouble(other))
        return self.dir_files[-1]

    def __init__(self, filename, *args, **kwargs):
        self.name = filename
        self.data = test_files_map.get(filename)
        self.out_data = None
        self._is_file = False
        if filename in test_files_map:
            self._is_file = True
        self.dir_files = []

    def is_file(self):
        return self._is_file

    @contextlib.contextmanager
    def open(self, *args, **kwargs):
        yield io.StringIO(self.data)

    def read(self, *args, **kwargs):
        return self.data
    
    def walk(self):
        if self._is_file:
            return (_ for _ in [])
        for k in test_files_map:
            yield (PathDouble("fakedir"), [], [k])

    def write_text(self, text: str, *args, **kwargs):
        self.out_data = text

    def write(self, text: str, *args, **kwargs):
        if text != "\n":
            self.out_data = text
