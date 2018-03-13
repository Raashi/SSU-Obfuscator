import random

from source import *

from source.parsing import ScriptStructure
from source.cinstructions import CFunction

OBFUSCATIONS = {
    'str': '',
    'int': '',
    'bool': ''
}


def obfuscate_str(structure: ScriptStructure, s_source: str, s_full: str):
    print('Обфусцирую: {}'.format(len(s_source)))

    if 'vector' not in structure.includes:
        structure.includes.add('vector')
    key = get_rand_s(len(s_source))
    s_sorted = ''.join(sorted(key))
    cryptogram = ''.join([chr(ord(s_source[idx]) + ord(s_sorted[idx])) for idx in range(len(s_source))])

    print('Криптограмма: {}'.format(len(cryptogram)))

    pattern = """
string get_str(string key, string crypto) 
{
    if (key.size() == crypto.size())
        cout << "horosho" << endl;
    for (int i = 0; i < key.size(); ++i)
        for (int j = i + 1; j < key.size(); ++j)
            if (key[i] > key[j]) 
            {
                char c = key[i];
                key[i] = key[j];
                key[j] = c;
            }
    string result;
    for (int i = 0; i < key.size(); ++i)
        result += string(1, (char)((int)crypto[i] - (int)key[i]));
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

    return '{}("{}", "{}"){}'.format(OBFUSCATIONS['str'], key, cryptogram, cast)


def get_rand_s(length: int):
    result = ''
    for idx in range(length):
        result += random.choice(ALPHABET)
    return result
