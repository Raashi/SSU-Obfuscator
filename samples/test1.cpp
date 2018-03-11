#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <map>

using namespace std;

vector <pair <string, bool> > sort_params;
map <string, int> columns_m;

vector <string> split(string input)
{
    vector <string> result;
    string s;
    for (int i = 0; i < input.size(); ++i) if (input[i] == ' ') {
            result.push_back(s);
            s = "";
        }
        else
            s = s + input[i];

    result.push_back(s);

    return result;
}

void split_sort(string input)
{
    vector<string> ss = split(input);
    for (int i = 0; i < ss.size(); i += 2)
    {
        if (ss[i + 1] == "ASC" || ss[i + 1] == "ASC,")
            sort_params.push_back(make_pair(ss[i], true));
        else
            sort_params.push_back(make_pair(ss[i], false));
    }
}

bool comp(vector <string>& s1, vector <string>& s2)
{
    int i = 0;
    while (i < sort_params.size())
        if (s1[columns_m[sort_params[i].first]] != s2[columns_m[sort_params[i].first]])
            return ((s1[columns_m[sort_params[i].first]] < s2[columns_m[sort_params[i].first]]) == sort_params[i].second);
        else
            i++;
    return false;
}

int main()
{
#ifdef _DEBUG
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    string s;
    getline(cin, s);
    vector <string> columns = split(s);

    for (int i = 0; i < columns.size(); ++i)
        columns_m[columns[i]] = i;

    getline(cin, s);
    split_sort(s);

    vector <vector <string> > table;
    while (cin)
    {
        getline(cin, s);
        table.push_back(split(s));
    }
    table.pop_back();

    sort(table.begin(), table.end(), comp);

    for (int i = 0; i < table.size(); ++i)
    {
        for (int j = 0; j < table[i].size(); ++j)
            cout << table[i][j] << ' ';
        cout << endl;
    }

    return 0;
}