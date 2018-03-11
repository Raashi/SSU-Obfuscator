import random
from source import *

C_TYPES_POSSIBLE = {'void': False, 'int': int, 'long': int, 'long long': int, 'float': float, 'double': float,
                    'string': str, 'bool': bool, 'char': 'char'}

C_TYPES_DEFAULT = {int: 0, float: 0.0, bool: False, str: '""', 'char': "''"}

C_CONTAINERS_POSSIBLE = {'vector', 'set', 'map', 'queue', 'pair'}


def find_type_matches(line, types):
    line_stripped = line.strip(CHARS_STRIP).split(' ')[0]
    if '<' in line_stripped:
        line_stripped = line_stripped[:line_stripped.index('<')].strip(CHARS_STRIP)
    for c_type in types:
        if c_type == line_stripped:
            return c_type
    return None


def get_type(line: str):
    c_container = find_type_matches(line, C_CONTAINERS_POSSIBLE)
    c_type = find_type_matches(line, C_TYPES_POSSIBLE)
    return c_container or c_type


def parse_generic(line: str):
    c_type_vector = get_type(subline_between(line, BRACKETS_ANGLE))
    if not c_type_vector:
        raise Exception('Не смогла распарсить генерик')
    return c_type_vector


def generic_arguments_str(arguments):
    return '.assign{}'.format(arguments)


class CPrimitive:
    def __init__(self, handler, cont: list, block):
        if not all([isinstance(handler, CPrimitive) or not handler,
                    isinstance(cont, list) or not cont,
                    isinstance(block, str) or isinstance(block, list)]):
            raise Exception('Неверные параметры')
        self.handler = handler
        self.vars = []
        self.code = []
        if handler:
            cont.append(self)

    def get_var(self, name: str, asker):
        if name not in CNames.NAMES:
            raise Exception('Нет такой переменной')
        if not isinstance(asker, CPrimitive):
            raise Exception('Не правильный вызов get_var')
        for c_var in reversed(self.vars):
            if hasattr(c_var, 'name') and c_var.name == name:
                return c_var
        if self.handler is None:
            raise Exception('Не нашла запрошенную переменную ' + name)
        return self.handler.get_var(name, asker)

    def struct(self):
        obj = self
        while obj.handler is not None:
            obj = obj.handler
        return obj

    def func(self):
        obj = self
        if obj.handler is None:
            return self
        while obj.handler.handler is not None:
            obj = obj.handler
        return obj

    def __str__(self):
        result = ''
        for c_var in self.vars:
            result += str(c_var) + ';\n'
        result += '\n'
        for c_code in self.code:
            s = str(c_code)
            result += s + (';\n' if s[-1] != ';' and s[-1] != '\n' else '')
        return result


class CBlock(CPrimitive):
    def __init__(self, handler, cont: list, block: list):
        super().__init__(handler, cont, block[0])

    def __str__(self):
        result = '\n{\n'
        for var in self.vars:
            result += str(var) + ';\n'
        for line in self.code:
            result += str(line) + '\n'
        result += '}'
        return result


class CNames:
    NAMES = set()
    NAMES_MESSED = {}
    NAMES_MESSED_LENGTH = 7

    @staticmethod
    def mess_name(handler: CPrimitive):
        name_messed = CNames.gen_name()
        CNames.NAMES_MESSED[name_messed] = handler
        return name_messed

    @staticmethod
    def gen_name():
        while True:
            result = 'N'
            for idx in range(CNames.NAMES_MESSED_LENGTH):
                result += str(random.randint(0, 9))
            if result not in CNames.NAMES_MESSED and result not in CNames.NAMES:
                return result
