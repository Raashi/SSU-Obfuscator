from source.cinstructions import *


class ScriptStructure(CPrimitive):
    def __init__(self, script: list):
        self.code = []
        super().__init__(None, self.code, script)
        self.defines = []
        self.includes = set()
        self.typedefs = []

        script = ScriptStructure.handle_inner_script(script)

        idx = 0
        while idx < len(script):
            line = script[idx]
            idx += 1

            if line[:7] == '#define':
                self.parse_define(line)
            elif line[:8] == '#include':
                self.parse_include(line)
            elif line[:8] == '#typedef':
                self.parse_typedef(line)
            elif CFunction.is_func(line):
                idx_func_end = separate_func(script, idx - 1)
                self.parse_func(script[idx - 1:idx_func_end])
                idx = idx_func_end
            elif CVariable.is_var(line):
                self.parse_global_variable(line)
            else:
                continue

        # Костыль для g++
        self.includes.add('cstdio')

    def parse_define(self, line: str):
        self.defines.append(line)

    def parse_include(self, line: str):
        if len(line.split()) > 2:
            raise Exception('Странный include: ' + line)
        self.includes.add(subline_between(line, BRACKETS_ANGLE))

    def parse_typedef(self, line: str):
        self.typedefs.append(line)

    def parse_global_variable(self, line: str):
        CVariable(self, line)

    def parse_func(self, lines: list):
        CFunction(self, list(map(str.rstrip, lines)))

    def __str__(self):
        result = ''
        for define in self.defines:
            result += define + '\n'
        for include in self.includes:
            result += '#include <{}>\n'.format(include)
        result += '\nusing namespace std;\n\n'
        result += super().__str__()
        return result

    def get_var(self, name: str, asker: CPrimitive):
        result = super().get_var(name, asker)
        if not result:
            raise Exception('Не нашла запрошенную переменную')
        return result

    def insert_func(self, script: list, idx: int):
        # Создаем функцию и пихаем её в начало скрипта
        self.code.insert(idx, CFunction(self, script))
        # Так как конструктор функции запихнул её еще и в конец .code -> удалим её оттуда
        str_obfuscator = self.code.pop()
        # Возвращаем ссылку на созданную функцию
        return str_obfuscator

    @staticmethod
    def delete_comments(script: list):
        for idx in range(len(script)):
            script[idx] = re.sub(r'//.+&', '', script[idx])

    @staticmethod
    def handle_inner_script(script) -> list:
        script_local = script if isinstance(script, list) else script.split('\n')
        # удаление комментариев
        ScriptStructure.delete_comments(script_local)
        # обрезание строк
        script_local = list(map(lambda s: s.strip(), script_local))
        # удаление пустых строк
        script_local = list(filter(lambda s: s, script_local))
        return script_local
