import random

from source import *
from source.parsing import ScriptStructure
from source.ctypes import CPrimitive

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}


def obfuscate_str(handler: CPrimitive, s_full: str, s_const: str):
    handle_str_obfuscation(handler.struct())

    key_size = random.randrange(3, 6)
    key = [random.randrange(5, 10) for _idx in range(key_size)]
    key_extra = ""
    for v in key:
        v1, v2 = divide_for_2(v)
        key_extra += (str(v1))
        key_extra += (str(v2))

    crypto = ""
    for idx in range(len(s_const)):
        crypto += chr(ord(s_const[idx]) + key[idx % len(key)])

    crypto = crypto.replace('\\', ' ')

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

    if 'cstdlib' not in structure.includes:
        structure.includes.add('cstdlib')

    pattern = """
string obfuscate_str(string crypto, string key)
{{
    string result = "";
    for (int i = 0; i < crypto.size(); i++)
    {{
        int a = key[(2 * i) % key.size()] - '0';
        int b = key[(2 * i + 1) % key.size()] - '0';
        char z = crypto[i];
        if (crypto[i] == ' ')
            z = '\\\\';
        result += (char)((int)z - a - b);
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


def divide_for_2(v: int):
    v1 = random.randrange(min(v, 10))
    v2 = v - v1
    while v1 > 9 or v2 > 9:
        v1 = random.randrange(min(v, 10))
        v2 = v - v1
    return v1, v2
