import os
import sys
import argparse

import source.parsing
from source.messing import *

os.chdir(os.path.normpath(os.path.dirname(__file__)))

FILENAME_IN = 'in.cpp'
FILENAME_OUT = 'out.cpp'
FILENAME_TEMP = 'temp.cpp.tmp'

ASTYLE = 'astyle {} -j -e -y -xe --style=allman'


def init_from_file(filename):
    assert os.path.exists(filename), 'Файла {} не существует'.format(filename)
    with open(filename) as file:
        script = file.readlines()
    return script


def init_vars():
    parser = argparse.ArgumentParser()
    parser.add_argument('fin', nargs='?', default=FILENAME_IN)
    parser.add_argument('fout', nargs='?', default=FILENAME_OUT)

    return parser.parse_args(sys.argv[1:])


def beautify_file_in(filename):
    with open(filename) as fin:
        script = fin.read()
    with open(FILENAME_TEMP, 'w') as fout:
        fout.write(script)
    os.popen(ASTYLE.format(FILENAME_TEMP))


def main():
    # Парсинг аргументов
    namespace = init_vars()

    # Считывание из файла (+ бьютифай)
    beautify_file_in(namespace.fin)
    script = init_from_file(FILENAME_TEMP)

    # Парсинг скрипта
    structure = source.parsing.ScriptStructure(script)

    # (;,,,,,,,,,,,,;)
    # deep_search_consts(structure)
    # deep_search_blocks(structure)
    # deep_search_gotos(structure)

    # Записываем в файл, тестируем, убираем мусор
    with open(namespace.fout, 'w', encoding='utf-8') as f:
        f.write(str(structure))

    # Бьютифаер
    os.popen(ASTYLE.format(namespace.fout))


if __name__ == '__main__':
    main()
