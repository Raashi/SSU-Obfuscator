from random import shuffle

from source.messing_utils import *
from source.cinstructions import *

from source.cconsts import *


# НАДО БЫТЬ ОЧЕНЬ АККУРАТНЫМ СО ВСТАВКОЙ КОДА
# ВСТАВКА В ТЕКУЩИЙ БЛОК КОДА - ОЧЕНЬ ОПАСНОЕ ДЕЛО
def deep_search_consts(handler: CPrimitive):
    code = handler.code.copy()
    for idx in range(len(code)):
        c_code = code[idx]
        if isinstance(c_code, str):
            # строки
            strings = CExpression.get_string_const(c_code)
            for str_const in reversed(strings):
                c_string = c_code[str_const[0] + 1: str_const[1]]
                c_code = c_code[:str_const[0]] + obfuscate_str(handler.struct(), c_code, c_string) + c_code[
                                                                                                     str_const[1] + 1:]
            # инты
            ints = CExpression.get_int_const(c_code)
            for int_const in reversed(ints):
                c_int = c_code[int_const[0]: int_const[1]]
                c_code = c_code[:int_const[0]] + obfuscate_int(handler.struct(), c_int) + c_code[int_const[1]:]
            handler.code[idx] = c_code
        elif isinstance(c_code, CBlock):
            deep_search_consts(c_code)
        else:
            pass


# ЭТУ ФИГНЮ В ПОСЛЕДНЮЮ ОЧЕРЕДЬ ЗАПУСКАТЬ
def deep_search_blocks(handler: CPrimitive):
    code = handler.code.copy()

    for idx in range(len(code)):
        c_code = code[idx]
        if isinstance(c_code, str):
            handler.code[idx] = obfuscate_single_exp(handler, c_code)
        elif isinstance(c_code, CBlock):
            deep_search_blocks(c_code)
        elif not isinstance(c_code, CLabel.CLabelCall):
            raise Exception('Непонятный участок кода')


def deep_search_gotos(handler: CPrimitive):
    code = handler.code.copy()

    if isinstance(handler, CBlock):
        code = gather_code_with_labels(handler, code)
        indices = list(range(1, len(code) - 1))
        shuffle(indices)
        indices = [0] + indices + [len(code) - 1]

        if not (len(indices) == 2 and indices[0] == indices[1]):
            handler.code.clear()
            for idx in indices:
                for c_code in code[idx]:
                    handler.code.append(c_code)

    for c_code in handler.code:
        if isinstance(c_code, CBlock):
            deep_search_gotos(c_code)


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
