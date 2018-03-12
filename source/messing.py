from functools import reduce

import source.parsing

from source.messing_utils import *
from source.cinstructions import *

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}


# НАДО БЫТЬ ОЧЕНЬ АККУРАТНЫМ СО ВСТАВКОЙ КОДА
# ВСТАВКА В ТЕКУЩИЙ БЛОК КОДА - ОЧЕНЬ ОПАСНОЕ ДЕЛО
def deep_search_consts(handler: CPrimitive):
    code = handler.code.copy()
    for idx in range(len(code)):
        c_code = code[idx]
        if isinstance(c_code, str):
            consts = CExpression.get_string_const(c_code)
            for str_const in consts:
                c_const = c_code[str_const[0] + 1: str_const[1]]
                c_code = c_code.replace('"' + c_const + '"', obfuscate_str(handler.struct(), c_const, c_code))
            handler.code[idx] = c_code
        elif isinstance(c_code, CBlock):
            deep_search_consts(c_code)
        else:
            raise Exception('Непонятный участок кода')


# ЭТУ ФИГНЮ В ПОСЛЕДНЮЮ ОЧЕРЕДЬ ЗАПУСКАТЬ
def deep_search_blocks(handler: CPrimitive):
    code = handler.code.copy()
    for idx in range(len(code)):
        c_code = code[idx]
        if isinstance(c_code, str):
            handler.code[idx] = obfuscate_single_exp(handler, c_code)
        elif isinstance(c_code, CBlock):
            deep_search_blocks(c_code)
        else:
            raise Exception('Непонятный участок кода')


def get_rand_s(length: int):
    result = ''
    for idx in range(length):
        result += random.choice(ALPHABET)
    return result


def obfuscate_str(structure: source.parsing.ScriptStructure, s_source: str, s_full: str):
    if 'vector' not in structure.includes:
        structure.includes.add('vector')
    s_gen = get_rand_s(len(s_source))
    s_sorted = ''.join(sorted(s_gen))
    arr = [ord(s_source[idx]) ^ ord(s_sorted[idx]) for idx in range(len(s_source))]

    pattern = """
string get_str(string v, string s) 
{
    for (int i = 0; i < v.size(); ++i)
        for (int j = i + 1; j < s.length(); ++j)
            if ((int)s[i] > (int)s[j]) 
            {
                char c = s[i];
                s[i] = s[j];
                s[j] = c;
            }
    string result;
    for (int i = 0; i < v.size(); ++i)
        result += string(1, (char)((int)s[i] ^ (int)v[i]));
    return result;
}
    """.split('\n')[1:-1]

    pattern = list(map(lambda s: s.strip(CHARS_STRIP), pattern))

    if not OBFUSCATIONS['str']:
        structure.code.insert(0, CFunction(structure, pattern))
        str_obfuscator = structure.code.pop()
        OBFUSCATIONS['str'] = str_obfuscator.name_messed

    # Костыль (нужен const char *)
    cast = '.c_str()' if 'scanf' in s_full or 'printf' in s_full else ''

    return OBFUSCATIONS['str'] + '("' + reduce(str.__add__, map(chr, arr)) + '", "{}"){}'.format(s_gen, cast)


def get_name(name: str):
    if '[' in name:
        return name[:name.index('[')]
    return name


def obfuscate_single_exp(handler: CPrimitive, exp: str):
    how, left, right = may_mess(exp)
    if how is None:
        return exp

    new_function_name = CNames.gen_name()
    if how == 'ass':
        assert get_name(left.strip()) in CNames.NAMES_MESSED, '{} имени нет в словаре'.format(left.strip())
        left = left.strip(CHARS_STRIP)

        variable = CNames.NAMES_MESSED[get_name(left.strip())]
        return_type = get_container_type(variable.type) if '[' in left else variable.type

        params, params_to_call, new_exp = get_vars_make_params(right)
        new_exp = 'return ' + new_exp

        kek, sign = split_by_equality(exp)
        func_exp = left + ' ' + sign + ' ' + new_function_name + '(' + params_to_call + ')'
    elif how == 'full':
        params, params_to_call, new_exp = get_vars_make_params(exp)
        func_exp = new_function_name + '(' + params_to_call + ')'
        return_type = 'void'

    pattern = """
{} {}({}) 
{{
    {}
}}
    """.format(return_type, new_function_name, params, new_exp)
    pattern = pattern.split('\n')[1:-1]

    struct = handler.struct()
    idx = struct.code.index(handler.func())
    struct.code.insert(idx, CFunction(struct, pattern))
    func = struct.code.pop()
    new_name_func = func.name_messed

    result = func_exp.replace(new_function_name, new_name_func) + ';'

    return result
