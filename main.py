import os
import sys
import argparse

import source.parsing
from source.messing import *

rsrc = os.path.normpath(os.path.dirname(__file__))
rsrc_astyle = os.path.join(rsrc, 'astyle.exe')
_convert_func = {'indent': 2, 'sort_keys': True}


def init_from_file(filename):
    filename_actual = filename if os.path.isabs(filename) else os.path.join(rsrc, filename)
    with open(filename_actual) as file:
        script = file.readlines()
    return script


def init_vars():
    parser = argparse.ArgumentParser()
    parser.add_argument('fin', nargs='?', default='')
    parser.add_argument('fout', nargs='?', default=rsrc + '\\out.cpp')
    namespace = parser.parse_args(sys.argv[1:])

    script = init_from_file(namespace.fin) if namespace.fin else init_from_file(input('Введите имя файла: '))
    return script, namespace.fout


def main():
    script, filename_out = init_vars()
    structure = source.parsing.ScriptStructure(script)
    # костыль
    structure.includes.add('cstdio')

    # (;,,,,,,,,,,,,;)
    deep_search_consts(structure)
    deep_search_blocks(structure)

    with open(filename_out, 'w') as f:
        f.write(str(structure))

    str_run = '"' + rsrc_astyle + '" "' + filename_out + '"'
    os.popen(str_run)


if __name__ == '__main__':
    main()
