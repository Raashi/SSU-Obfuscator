import re

CHARS_STRIP = '\t '
CHARS_STRIP_VARIABLE = ';*&'
STRUCTS_STRIP_VARIABLE = '(<'

PARENTHESES = ('(', ')')
BRACKETS_SQUARE = ('[', ']')
BRACKETS_ANGLE = ('<', '>')

ALPHABET = ''


def split_multiple(line: str, seps: tuple):
    regex_pattern = '|'.join(map(re.escape, seps))
    result = re.split(regex_pattern, line)
    for i in range(len(result)):
        result[i] = result[i].strip(CHARS_STRIP)
    while '' in result:
        result.remove('')
    return result


def subline_between(line: str, chars: tuple):
    if not set(chars).issubset(line):
        raise Exception('Не могу взять подстроку между чарами: ' + line)
    return line[line.index(chars[0]) + 1: line.rfind(chars[1])]


def init_alph():
    result = ''
    for idx in range(ord('a'), ord('z') + 1):
        result += chr(idx) + chr(idx).upper()
    for idx in range(9):
        result += chr(idx)
    global ALPHABET
    ALPHABET = result


def split_by_equality(line: str):
    signs = ['-', '+', '\\', '*']
    for sign in signs:
        if sign + '=' in line:
            return line.split(sign + '='), sign + '='
    return line.split('='), '='


def check_and_replace(pattern: str, line: str, line_to_replace: str, new_line: str):
    matches = [m.start() for m in re.finditer(pattern, line)]
    res = line
    for match in reversed(matches):
        count_left = res[:match].count('"')
        count_right = res[match:].count('"')
        # ЛЮТЫЙ КОСТЫЛЬ
        if (count_left % 2 == 0 and count_right % 2 == 0) or "'" in line:
            res = res[:match] + new_line + res[match + len(line_to_replace):]
    return res


def check_for_consts_around(line: str, pattern: str):
    matches = [m.start() for m in re.finditer(pattern, line)]
    if not matches:
        return None
    match = matches[0]
    count_left = line[:match].count('"')
    count_right = line[match:].count('"')
    return not (count_left % 2) and not (count_right % 2)


def check_and_get(line: str, pattern: str):
    matches = [m.start() for m in re.finditer(pattern, line)]
    res = []
    for match in matches:
        count_left = line[:match].count('"')
        count_right = line[match:].count('"')
        if count_left % 2 == 0 and count_right % 2 == 0:
            res.append(match)
    return res


def symbol_count(line: str, symbol: str):
    return len(check_and_get(line, symbol))


init_alph()
