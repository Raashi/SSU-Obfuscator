import random

C_TYPES_POSSIBLE = {'void': False, 'int': int, 'long': int, 'long long': int, 'float': float, 'double': float,
                    'string': str, 'bool': bool}

C_TYPES_DEFAULT = {int: 0, float: 0.0, bool: False, str: ''}

C_CONTAINERS_POSSIBLE = {'vector': list, '[': list, 'set': set, 'map': dict, 'queue': list, 'pair': tuple}

BRACKETS = ('(', ')')


def find_type_matches(line: str, types: dict):
    if types == C_TYPES_POSSIBLE:
        for c_type in types:
            if c_type in line:
                return c_type
    elif types == C_CONTAINERS_POSSIBLE:
        for c_type in types:
            if c_type in line and any(c_simple_type in line for c_simple_type in C_TYPES_POSSIBLE):
                return c_type
    return None


def get_type(line: str):
    # специальный случай  с парами
    c_pair = 'pair' if 'pair' in line else None
    if c_pair:
        raise Exception('Не работаю с двойными генериками')

    c_container = find_type_matches(line, C_CONTAINERS_POSSIBLE)
    # костыль
    c_type = find_type_matches(line, C_TYPES_POSSIBLE)
    result = c_pair or c_container or c_type
    # if not result:
    #     print('Не смогла распарсить тип: {}'.format(line))
    return result


def parse_generic(line: str):
    c_type_vector = get_type(line[line.index('<') + 1:line.rfind('>')])
    if not c_type_vector:
        raise Exception('Не смогла распарсить генерик')
    return c_type_vector


def parse_array(line: str):
    c_type_array = get_type(line[:line.index('[')])
    if not c_type_array:
        print('Не смогла распарсить массив ' + line)
    return c_type_array


def parse_double_generic(line: str):
    """
    type_definition = line[line.index('<') + 1:line.rfind('>')].split(',')
    if len(type_definition) != 2:
        raise Exception('Не смогла распарсить двойной генерик')
    return get_type(type_definition[0]), get_type(type_definition[1])
    """
    raise Exception('Не работаю с двойными генериками')


C_CONTAINERS_PARSERS = {'vector': parse_generic, '[': parse_array, 'set': parse_generic, 'map': parse_double_generic,
                        'pair': parse_double_generic, 'queue': parse_generic}


def array_to_str(type_array: str):
    return type_array + '[]'


def vector_to_str(type_vector: str):
    return 'vector<{}>'.format(type_vector)


def queue_to_str(type_vector: str):
    return 'queue<{}>'.format(type_vector)


C_CONTAINERS_TO_STR = {'vector': vector_to_str, '[': array_to_str, 'queue': queue_to_str}


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
            if c_var.name == name:
                # return c_var.get_link()
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
        if not all([isinstance(self.vars, list), isinstance(self.code, list)]):
            raise Exception('Что-то случилось с основными полями за время жизни функции')
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
        result = '{\n'
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
