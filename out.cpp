#define _CRT_SECURE_NO_WARNINGS
#include <algorithm>
#include <iostream>
#include <vector>
#include <cstdio>
#include <map>
#include <string>

using namespace std;

vector <pair <string, bool> > N9209020;
map <string, int> N5932750;

vector<string> N2645886(string N4239644)

{
    vector <string> N5819251;
    string N1549749;
    int N1171895;
    for (N1171895 = 0; N1171895 < N4239644.size(); ++N1171895)
    {
        if (N4239644[N1171895] == ' ')
        {
            N5819251.push_back(N1549749);
            N1549749 = "";
        }
        else
        {
            N1549749 = N1549749 + N4239644[N1171895];
        }
    }
    N5819251.push_back(N1549749);
    return N5819251;
};
void N6258392(string N6401677)

{
    vector<string> N2260273;
    int N0510639;
    N2260273 = N2645886(N6401677);
    for (N0510639 = 0; N0510639 < N2260273.size(); N0510639 += 2)
    {
        if (N2260273[N0510639 + 1] == "ASC" || N2260273[N0510639 + 1] == "ASC,")
        {
            N9209020.push_back(make_pair(N2260273[N0510639], true));
        }
        else
        {
            N9209020.push_back(make_pair(N2260273[N0510639], false));
        }
    }
};
bool N8784392(vector <string> & N8074544,vector <string> & N5003082)

{
    int N2445082;
    N2445082 = 0;
    while (N2445082 < N9209020.size())
    {
        if (N8074544[N5932750[N9209020[N2445082].first]] != N5003082[N5932750[N9209020[N2445082].first]])
        {
            return ((N8074544[N5932750[N9209020[N2445082].first]] < N5003082[N5932750[N9209020[N2445082].first]]) == N9209020[N2445082].second);
        }
        else
        {
            N2445082++;
        }
    }
    return false;
};
int main()

{
    string N2679852;
    vector <string> N7319280;
    int N7499551;
    vector <vector <string> > N4522822;
    int N4548723;
    getline(cin, N2679852);
    N7319280 = N2645886(N2679852);
    for (N7499551 = 0; N7499551 < N7319280.size(); ++N7499551)
    {
        N5932750[N7319280[N7499551]] = N7499551;
    }
    getline(cin, N2679852);
    N6258392(N2679852);
    while (cin)
    {
        getline(cin, N2679852);
        N4522822.push_back(N2645886(N2679852));
    }
    N4522822.pop_back();
    sort(N4522822.begin(), N4522822.end(), N8784392);
    for (N4548723 = 0; N4548723 < N4522822.size(); ++N4548723)
    {
        int N9013719;
        for (N9013719 = 0; N9013719 < N4522822[N4548723].size(); ++N9013719)
        {
            cout << N4522822[N4548723][N9013719] << ' ';
        }
        cout << endl;
    }
    return 0;
};
