import functools

from source.ctypes import *


class CVariable(CPrimitive):
    def __init__(self, handler: CPrimitive, line: str, arguments: list = None):
        super().__init__(handler, arguments if arguments is not None else handler.struct().vars, line)
        line = line.replace(';', '').strip(CHARS_STRIP)
        # Оставлю для отладки
        self.line = line

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
        if '[' in line:
            self.arguments = '[' + subline_between(line, BRACKETS_SQUARE) + ']'
            line = line[:line.index('[')].strip(CHARS_STRIP)

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
        elif var.is_arr and hasattr(var, 'arguments') and var.arguments[0] != '[':
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


class CLabel(CPrimitive):
    def __init__(self, handler: CBlock, line: str):
        super().__init__(handler.func(), handler.labels, line)

        # ВАЖНО
        self.name = CLabel.extract_label_name(line)
        self.name_messed = CNames.mess_name(self)
        # ВАЖНО

    class CLabelCall(CPrimitive):
        def __init__(self, handler: CPrimitive, label, line: str, list_to_insert: list):
            super().__init__(handler, list_to_insert, line)

            self.line = line.replace(label.name, label.name_messed)
            self.label = label

        def __str__(self):
            return self.line

    @staticmethod
    def extract_label_name(line: str):
        if line[:4] == 'goto':
            name = line.split(' ')[1][:-1]  # убираем точку с запятой
        elif line[-1] == ':':
            name = line[:-1]
        else:
            raise Exception('Данная строка не относится к goto: {}'.format(line))
        return name.strip()

    @staticmethod
    def is_label(line: str):
        return line[:4] == 'goto' or line[-1] == ':'

    @staticmethod
    def parse(handler, line: str):
        name = CLabel.extract_label_name(line)
        label = handler.get_label(name)
        if label is None:
            label = CLabel(handler, line)
        CLabel.CLabelCall(handler, label, line, handler.code)


class CExpression:
    SEPARATORS = ('+', '-', '/', '*', '==', '!=', '&&', '||', '=', ',', ';', '[', ']', '<<', '>>')

    @staticmethod
    def refactor(handler: CPrimitive, line: str):
        result = line
        # Проверка на goto (костыль)
        if line[:4] == 'goto':
            goto_name = line[4:][:-1].strip()
            goto_name_messed = handler.get_label(goto_name).name_messed
            return 'goto {}'.format(goto_name_messed)
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
        # return re.sub(r'\b' + func.name + r'\b', func.name_messed, line)
        return check_and_replace(r'\b' + func.name + r'\b', line, func.name, func.name_messed)

    @staticmethod
    def find_var(line: str, var_name: str):
        return [m.start() for m in re.finditer(r'\b' + var_name + r'\b', line)]

    @staticmethod
    def replace_var(line: str, var: CVariable):
        return check_and_replace(r'\b' + var.name + r'\b', line, var.name, var.name_messed)

    @staticmethod
    def get_string_const(line: str):
        matches = check_and_get(line, r'\"([^\"]*)\"')
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
    if CLabel.is_label(line):
        CLabel.parse(handler, line)
    elif CVariable.is_var(line):
        parsed = CVariable.parse(handler, line) + ';'
        if len(parsed) > 1:
            handler.code.append(parsed)
    else:
        handler.code.append(CExpression.refactor(handler, line))


def separate_func(script, idx_func_start: int):
    # поиск открывающей скобки
    idx = idx_func_start
    line = script[idx]
    count_brackets = symbol_count(line, r'{')

    if symbol_count(line, r'}') or count_brackets > 1:
        raise Exception('Не пойму как парсить такое определение функции: ' + line)
    if not count_brackets:
        idx += 1
        line = script[idx]
        count_brackets = symbol_count(line, r'{')
    # поиск закрывающей скобки
    while count_brackets:
        idx += 1
        line = script[idx]
        # count_brackets += line.count('{') - line.count('}')
        count_brackets += symbol_count(line, r'{') - symbol_count(line, r'}')

    return idx + 1


def automat(script: list, start: int):
    blocks = ['if', 'for', 'while', 'else']

    if start >= len(script) - 1:
        raise Exception('Неверный вызов автомата')

    idx = start + 1
    line = script[idx]
    brackets = line.count('{')

    while brackets or any(block in line for block in blocks):
        idx += 1
        line = script[idx]
        brackets += line.count('{') - line.count('}')

    idx += 1
    # Скрипт закончился
    if idx == len(script) or 'else' not in script[idx]:
        return idx
    else:  # Обработка else
        return automat(script, idx)


def parse_block(handler, lines: list):
    idx = 0

    while idx < len(lines):
        line = lines[idx]

        if line[-1] == ';' or line[-1] == ':':
            parse_instruction(handler, line)
            idx += 1
        elif 'if' in line and 'else' not in line:
            idx_block_end = automat(lines, idx)
            CIf(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'for' in line:
            idx_block_end = automat(lines, idx)
            CFor(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'while' in line:
            idx_block_end = automat(lines, idx)
            CWhile(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        elif 'else' in line:
            idx_block_end = automat(lines, idx)
            CIf.CElse(handler, lines[idx:idx_block_end])
            idx = idx_block_end
        else:
            idx += 1
