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


init_alph()
