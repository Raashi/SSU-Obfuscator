import re

from source import *
from source.ctypes import CNames
from source.cinstructions import *


def may_mess(exp: str):
    s = exp.strip()
    if check_for_consts_around(s, r'^return (.+)') or check_for_consts_around(s.strip(CHARS_STRIP), r'^break') or \
            check_for_consts_around(s, r'^goto \b(\w+)\b$') or check_for_consts_around(s, r'^\b(\w+)\b:&'):
        return None, None, None
    if check_for_consts_around(s, r'[\+\*\\\-\b ]\=[^\=]'):
        splitted, sign = split_by_equality(s)
        return 'ass', splitted[0].strip(), splitted[1].strip()
    return 'full', exp, exp


def var_replace_name_and_args(var_declaration: str, name_new: str):
    res = re.sub(r'(\(*\))', '', var_declaration)
    idx = res.rfind(' ')
    return res[:idx + 1] + name_new


def insert_dog(exp: str):
    if '>' in exp:
        return exp[:exp.index('>') + 2] + '& ' + exp[exp.index('>') + 2:]
    else:
        return exp[:exp.index(' ') + 1] + '& ' + exp[exp.index(' ') + 1:]


def get_vars_make_params(exp: str):
    vars_in_line = []
    for name_messed, var in CNames.NAMES_MESSED.items():
        if CExpression.find_var(exp, name_messed) and var.handler.handler is not None:
            vars_in_line.append(var)

    params = []
    params_to_call = []
    for idx, var in enumerate(vars_in_line):
        new_name = CNames.gen_name()
        # делаем параметр
        params.append(insert_dog(var_replace_name_and_args(str(var), new_name)))
        # делаем вызов
        params_to_call.append(var.name_messed)
        # заменяем в выражении старые переменные на новые переменные новой функции
        exp = re.sub(r'\b' + var.name_messed + r'\b', new_name, exp)

    return ', '.join(params), ','.join(params_to_call), exp


def gather_code_with_labels(handler: CBlock, code: list):
    if len(code) == 1:
        return [code]

    res = []
    next_call = None

    for idx in range(len(code)):
        start = idx
        while idx < len(code) and isinstance(code[idx], CLabel):
            idx += 1
        idx += 1

        next_block = code[start:idx]
        if next_call:
            next_block.insert(0, next_call)

        rand_name = CNames.gen_name()
        new_label = CLabel(handler, 'goto {};'.format(rand_name))
        CLabel.CLabelCall(handler, new_label, 'goto {};'.format(rand_name), next_block)

        costyl = []
        next_call = CLabel.CLabelCall(handler, new_label, '{}:'.format(rand_name), costyl)

        res.append(next_block)

    return res
