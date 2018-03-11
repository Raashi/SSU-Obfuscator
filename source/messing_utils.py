import re

from source.ctypes import CNames
from source.cinstructions import CExpression


def may_mess(exp: str):
    s = exp.strip()
    if list(re.finditer('^return (.+)', s)):
        return None, None, None
    if list(re.finditer('[^=]=[^=]', s)):
        return 'ass', s[:s.index('=')].strip(), s[s.index('=') + 1:].strip()
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
