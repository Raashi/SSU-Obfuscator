import random

from functools import reduce
from source import *

from source.parsing import ScriptStructure
from source.cinstructions import CFunction

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}


def obfuscate_str(structure: ScriptStructure, s_source: str, s_full: str):
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


def get_rand_s(length: int):
    result = ''
    for idx in range(length):
        result += random.choice(ALPHABET)
    return result
