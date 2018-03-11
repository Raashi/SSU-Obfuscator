import functools

from source.ctypes import *


class CVariable(CPrimitive):
    def __init__(self, handler: CPrimitive, line: str, arguments: list = None):
        super().__init__(handler, arguments if arguments is not None else handler.struct().vars, line)
        line = line.replace(';', '').strip(CHARS_STRIP)
        # Оставлю для отладки
        self.line = line

        if '*' in line:
            raise Exception('НЕ ХОЧУ ЗВЕЗДОЧКИ')
        if '&' in line:
            self.dogged = True
            line = line.replace('&', '')
        if '=' in line:
            self.value = line[line.index('=') + 1:].strip(CHARS_STRIP)
            line = line[:line.index('=')].strip(CHARS_STRIP)
        if '(' in line:
            # для vector<> - инициализация размера
            self.arguments = '(' + subline_between(line, PARENTHESES) + ')'
            line = line[:line.index('(')].strip(CHARS_STRIP)

        # ВАЖНО
        self.name = line[line.rfind(' ') + 1:]
        CNames.NAMES.add(self.name)
        self.name_messed = CNames.mess_name(self)
        # ВАЖНО

        line_type = line[:line.rfind(' ')].strip(CHARS_STRIP)
        self.type = line_type
        self.is_arr = find_type_matches(self.type, C_CONTAINERS_POSSIBLE)

        if hasattr(self, 'value'):
            self.value = CExpression.refactor(self, self.value)
        if hasattr(self, 'arguments'):
            self.arguments = CExpression.refactor(self, self.arguments)

    def __str__(self):
        result = self.type + ' '
        if hasattr(self, 'dogged'):
            result += '& '
        result += self.name_messed
        return result

    @staticmethod
    def is_var(line: str):
        return ' ' in line and get_type(line.split(' ')[0])

    @staticmethod
    def parse(handler: CPrimitive, line: str):
        var = CVariable(handler, line)
        if hasattr(var, 'value'):
            return '{} = {}'.format(var.name_messed, var.value)
        elif var.is_arr and hasattr(var, 'arguments'):
            return '{}{}'.format(var.name_messed, generic_arguments_str(var.arguments))
        else:
            return ''


class CFunction(CBlock):
    FUNCS_ALL = {}

    def __init__(self, handler: CPrimitive, lines: list):
        super().__init__(handler, handler.code, lines)
        # выясняем где открывающая скобка: в конце первой или на второй строке
        idx_start = 0 if lines[0][-1] == '{' else 1
        if idx_start:
            line_definition = lines[0].rstrip(CHARS_STRIP)
            idx_start = 2
        else:
            line_definition = lines[0][:-1].rstrip(CHARS_STRIP)
            idx_start = 1

        self.arguments = []
        self.parse_arguments(subline_between(line_definition, ('(', ')')))

        # ВАЖНО
        type_and_name = line_definition[:line_definition.index('(')].split()
        self.type = functools.reduce(str.__add__, type_and_name[:-1])
        self.name = type_and_name[-1]
        self.FUNCS_ALL[self.name] = self
        self.name_messed = CNames.mess_name(self) if self.name != 'main' else 'main'
        # ВАЖНО

        parse_block(self, lines[idx_start:-1])

    def parse_arguments(self, line_arguments: str):
        result = ''
        if not line_arguments:
            return []
        arguments = line_arguments.split(',')
        for argument in arguments:
            CVariable(self, argument, self.arguments)
        return result[:-1]  # без последней точки с запятой

    def arguments_to_str(self):
        result = ''
        for argument in self.arguments:
            result += str(argument) + ','
        return result[:-1]

    def __str__(self):
        return '{0} {1}({2})\n{3}'.format(self.type, self.name_messed, self.arguments_to_str(), super().__str__())

    def get_var(self, name: str, asker):
        # сначала проверить аргументы функции
        matches = [var for var in self.arguments if var.name == name]
        result = matches[0] if matches else None
        # иначе поиск на уровень выше
        return result if result else super().get_var(name, asker)

    @staticmethod
    def is_func(line: str):
        # проверка случая vector<int> v(n) - отличие от функции в том, что у n нет типа. иначе это была бы функция
        # однако такие проверки крашнутся при неучтённом типе
        if '(' in line and ')' in line:
            definition = line[line.index('(') + 1: line.index(')')].replace(CHARS_STRIP, '')
            # функция без аргументов тоже учитывается
            return not definition or get_type(definition)
        return False


class CConstant:
    @staticmethod
    def is_constant(line: str):
        temp_line = line.strip(CHARS_STRIP + '()').lower()
        return (temp_line.count('"') == 2 or
                temp_line.count("'") == 2 or
                temp_line == 'false' or
                temp_line == 'true' or
                temp_line.isnumeric())


class CExpression:
    SEPARATORS = ('+', '-', '/', '*', '==', '!=', '&&', '||', '=', ',', ';', '[', ']', '<<', '>>')

    @staticmethod
    def refactor(handler: CPrimitive, line: str):
        result = line
        # рефакторинг известных функций
        for name in CFunction.FUNCS_ALL:
            if CExpression.find_func(result, name):
                result = CExpression.replace_func(result, CFunction.FUNCS_ALL[name])
        # рефакторинг известных переменных
        for name in CNames.NAMES:
            if CExpression.find_var(result, name):
                result = CExpression.replace_var(result, handler.get_var(name, handler))
        return result

    @staticmethod
    def find_system_calls(line: str):
        matches = []
        if '(' in line and ')' in line:
            matches = [m.start() for m in re.finditer(r'(\w+)\((.*)\)', line)]
            for match in matches:
                idx_r = line.index('(', match)
                call_name = line[match: idx_r]
                print('Вызов ' + call_name)
        return matches

    @staticmethod
    def find_func(line: str, func_name):
        return [m.start() for m in re.finditer(r'\b' + func_name + r'\b', line)]

    @staticmethod
    def replace_func(line: str, func: CFunction):
        return re.sub(r'\b' + func.name + r'\b', func.name_messed, line)

    @staticmethod
    def find_var(line: str, var_name: str):
        return [m.start() for m in re.finditer(r'\b' + var_name + r'\b', line)]

    @staticmethod
    def replace_var(line: str, var: CVariable):
        return re.sub(r'\b' + var.name + r'\b', var.name_messed, line)

    @staticmethod
    def get_string_const(line: str):
        matches = [m.start() for m in re.finditer(r'\"([^\'\"]*)\"', line)]
        return [(match, line.index('"', match + 1)) for match in matches]

    @staticmethod
    def get_constants(line: str):
        result = set()
        parts = split_multiple(line, CExpression.SEPARATORS)
        for part in parts:
            if CConstant.is_constant(part):
                result.add(part)
        return result


class CIf(CBlock):
    def __init__(self, handler: CPrimitive, lines: list):
        super().__init__(handler, handler.code, lines)
        self.exp = CExpression.refactor(self, subline_between(lines[0], ('(', ')')))
        self.has_else = []
        parse_block(self, lines[1:])

    def __str__(self):
        result = 'if ({}) {}'.format(self.exp, super().__str__())
        if self.has_else:
            result += str(self.has_else[0])
        return result

    class CElse(CBlock):
        def __init__(self, handler: CPrimitive, lines: list):
            super().__init__(handler, getattr(handler, 'has_else'), lines)
            if 'if' in lines[0]:
                statement_if = lines[0][lines[0].index(' ') + 1:]
                lines[0] = lines[0].replace(statement_if, '')
                lines.insert(1, statement_if)
            parse_block(self, lines[1:])

        def __str__(self):
            return '\nelse ' + super().__str__()

    @staticmethod
    def handle_separation(lines: list, idx: int):
        idx_block_end = separate_block(lines, idx)
        if idx_block_end >= len(lines):
            return idx_block_end
        elif 'else' not in lines[idx_block_end]:
            return idx_block_end
        else:
            idx_block_end_true = separate_block(lines, idx_block_end)
            if idx_block_end_true < len(lines) and 'else' in lines[idx_block_end_true]:
                idx_block_end_true = separate_block(lines, min(idx_block_end_true + 1, len(lines) - 1))
            return idx_block_end_true


class CFor(CBlock):
    def __init__(self, handler, lines):
        super().__init__(handler, handler.code, lines)
        head = subline_between(lines[0], ('(', ')')).split(';')
        self.arguments = []
        # часть 1
        if CVariable.is_var(head[0]):
            self.arguments.append(CVariable.parse(handler, head[0]))
            self.var = self.struct().vars[-1]
        else:
            self.arguments.append(CExpression.refactor(self, head[0]))
        # часть 2
        self.arguments.append(CExpression.refactor(self, head[1]))
        # часть 3
        self.arguments.append(CExpression.refactor(self, head[2]))
        parse_block(self, lines[1:])

    def __str__(self):
        return 'for ({};{};{}) {}'.format(self.arguments[0], self.arguments[1], self.arguments[2], super().__str__())

    def get_var(self, name: str, asker):
        # сначала проверить переменную цикла
        if hasattr(self, 'var'):
            if self.var.name == name:
                return self.var
        return super().get_var(name, asker)


class CWhile(CBlock):
    def __init__(self, handler, lines):
        super().__init__(handler, handler.code, lines)
        self.exp = CExpression.refactor(self, subline_between(lines[0], ('(', ')')))
        parse_block(self, lines[1:])

    def __str__(self):
        return 'while ({}) {}'.format(self.exp, super().__str__())


def parse_instruction(handler, line: str):
    # парсим присвоение без заведения переменной
    if CVariable.is_var(line):
        parsed = CVariable.parse(handler, line) + ';'
        if len(parsed) > 1:
            handler.code.append(parsed)
    else:
        handler.code.append(CExpression.refactor(handler, line))


def separate_func(script, idx_func_start: int):
    # поиск открывающей скобки
    idx = idx_func_start
    line = script[idx]
    count_brackets = line.count('{')

    if line.count('}') or count_brackets > 1:
        raise Exception('Не пойму как парсить такое определение функции: ' + line)
    if not count_brackets:
        idx += 1
        line = script[idx]
        count_brackets = line.count('{')
        if not count_brackets or line.count('}'):
            raise Exception('Не могу найти начало функции ' + script[idx_func_start])
    # поиск закрывающей скобки
    while count_brackets:
        idx += 1
        line = script[idx]
        count_brackets += line.count('{') - line.count('}')

    return idx + 1


def separate_block(script: list, idx_block_start: int):
    # рекурсивный костыль
    if script[idx_block_start][-1] == ';':
        return idx_block_start + 1
    # поиск открывающей скобки
    line = script[idx_block_start]
    count_brackets = line.count('{')
    idx = idx_block_start

    if '}' in line:  # i.e. definition is for (...) {}
        return idx_block_start
    new_line = script[idx_block_start + 1]
    idx += 1
    count_brackets += new_line.count('{')

    if 'if' in new_line:
        return CIf.handle_separation(script, idx_block_start + 1)
    if not count_brackets and (new_line == '{' or
                               new_line[-1] == ';' or
                               any(pattern in new_line for pattern in ['if', 'for', 'while', 'else'])):
        return separate_block(script, idx_block_start + 1)  # рекурсия если конструкция простая (её блок - 1 строка)
    if not count_brackets:
        raise Exception('Не могу распарсить блок ' + script[idx_block_start])

    # поиск закрывающей скобки
    while count_brackets:
        idx += 1
        line = script[idx]
        count_brackets += line.count('{') - line.count('}')
        if 'else' in line and '{' in line and count_brackets == 1:
            return idx

    if idx + 1 < len(script) and 'else' in script[idx + 1]:
        return separate_block(script, idx + 1)

    return idx + 1


def parse_block(handler, lines: list):
    idx = 0

    while idx < len(lines):
        line = lines[idx]

        if line[-1] == ';':
            parse_instruction(handler, line)
            idx += 1
        elif 'if' in line and 'else' not in line:
            idx_block_end = separate_block(lines, idx)
            CIf(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'for' in line:
            idx_block_end = separate_block(lines, idx)
            CFor(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'while' in line:
            idx_block_end = separate_block(lines, idx)
            CWhile(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'else' in line:
            idx_block_end = separate_block(lines, idx)
            CIf.CElse(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        else:
            idx += 1
