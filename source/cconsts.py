import random
import functools

from source import *

from source.parsing import ScriptStructure
from source.cinstructions import CFunction
from source.ctypes import CPrimitive

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}


def obfuscate_str(handler: CPrimitive, s_const: str, s_full: str):
    handle_str_obfuscation(handler.struct())

    key = [random.randrange(5, 19) for _idx in range(len(s_const) * 2)]
    key_extra = ""
    for v in key:
        v1 = random.randrange(v)
        v2 = v - v1
        key_extra += (str(v1))
        key_extra += (str(v2))

    crypto = ""
    for c, k in zip(s_const, key):
        crypto += chr(ord(c) + k)

    # Костыль (нужен const char *)
    cast = '.c_str()' if 'scanf' in s_full or 'printf' in s_full else ''
    calling = '{}("{}", "{}"){}'.format(OBFUSCATIONS['str'], crypto, key_extra, cast)
    return calling


def get_rand_s(length: int):
    result = ''
    for idx in range(length):
        result += random.choice(ALPHABET)
    return result


def handle_str_obfuscation(structure: ScriptStructure):
    if OBFUSCATIONS['str']:
        return

    pattern = """
void obfuscate_str(string crypto, string key)
{{
    string result = "";
    for (int i = 0; i < key.size(); i+=2)
    {{
        char a = key[i];
        char b = key[i + 1];
        string concat = "{}";
        concat[0] = a;
        concat[1] = b;
        int c = stoi(concat);
        result = result + (char)((int)crypto[i / 2] - c);
    }}
    return result;
}}
""".format(get_rand_s(2))
    # Обработка паттерна (пустые строки и т.п.)
    script = ScriptStructure.handle_inner_script(pattern)
    # Создание и вставка функции в основной скрипт
    str_obfuscator = structure.insert_func(script, 0)
    # Занесём messed имя обфускатора в словарь обфускаторов
    OBFUSCATIONS['str'] = str_obfuscator.name_messed


