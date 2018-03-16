import random

from source import *
from source.parsing import ScriptStructure
from source.ctypes import CPrimitive

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}

FIELD = [33, 123, 90]


def obfuscate_str(handler: CPrimitive, s_full: str, s_const: str):
    handle_str_obfuscation(handler.struct())

    key_size = random.randrange(3, 6)
    key = [random.randrange(2, 10) for _idx in range(key_size)]

    s_const = s_const.replace('|', '\\')
    s_const = s_const.replace('~', '"')

    crypto = ""
    for idx in range(len(s_const)):
        lel = ord(s_const[idx]) + key[idx % len(key)] - FIELD[0]
        lel %= FIELD[2]
        lel += FIELD[0]
        crypto += chr(lel) if s_const[idx] != ' ' else ' '

    crypto = crypto.replace('\\', '|')
    crypto = crypto.replace('"', '~')

    # Костыль (нужен const char *)
    cast = '.c_str()' if 'scanf' in s_full or 'printf' in s_full else ''
    calling = '{}("{}", "{}"){}'.format(OBFUSCATIONS['str'], crypto, ''.join(map(str, key)), cast)

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
        int a = key[i % key.size()] - '0';
        int z = (int)crypto[i];
        if (crypto[i] == '|')
            z = 92;
        if (crypto[i] == ' ')
        {{
            result = result + ' ';
            continue;
        }}
        if (crypto[i] == '~')
            z = 34;
        int meh = (int)z;
        meh = meh - 33 - a + 90;
        meh = meh % 90;           
        meh += 33;
        result = result + (char)meh;
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


def obfuscate_int(struct: ScriptStructure, s_const: str):
    handle_int_obfuscation(struct)

    m = int(s_const)
    m_len = max(len(bin(m)) - 2, 5)

    len1 = random.randint(1, m_len - 1)
    len2 = m_len - len1
    # Старшие
    b2 = random.randint(len1 + len2, 15)
    a2 = b2 - len2
    # Младшие
    b1 = random.randint(len1 - 1, a2 - 1)
    a1 = b1 - len1

    print(s_const, m_len, a1, b1, a2, b2)

    return s_const


def handle_int_obfuscation(structure: ScriptStructure):
    if OBFUSCATIONS['int']:
        return

    pattern = """
int obfuscate_int(int crypto, int a1, int b1, int a2, int b2)
{
    int result = 0;
    
    return crypto;
}
"""
    # Обработка паттерна (пустые строки и т.п.)
    script = ScriptStructure.handle_inner_script(pattern)
    # Создание и вставка функции в основной скрипт
    int_obfuscator = structure.insert_func(script, 0)
    # Занесём messed имя обфускатора в словарь обфускаторов
    OBFUSCATIONS['int'] = int_obfuscator.name_messed
