import os
import sys
import argparse

import source.parsing
from source.messing import *

os.chdir(os.path.normpath(os.path.dirname(__file__)))

FILENAME_IN = 'in.cpp'
FILENAME_OUT = 'out.cpp'
FILENAME_EXE = 'out.exe'


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


def main():
    # Парсинг аргументов
    namespace = init_vars()
    # Считывание из файла
    script = init_from_file(namespace.fin)
    # Парсинг скрипта
    structure = source.parsing.ScriptStructure(script)
    # (;,,,,,,,,,,,,;)
    deep_search_consts(structure)
    # deep_search_blocks(structure)

    # Записываем в файл, тестируем, убираем мусор
    with open(namespace.fout, 'w') as f:
        f.write(str(structure))

    # Бьютифаер
    os.popen('astyle.exe "{}"'.format(namespace.fout))


if __name__ == '__main__':
    main()
