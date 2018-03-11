#include <iostream>
#include <cstdio>

using namespace std;

int N3698388;
bool N5975786;
int N4091257;
int N5107470;
bool N3593479;

bool N2919495(int N2199548)

{
    N5975786 = true;
    for (N3698388 = 2; N3698388 <= N2199548/2; ++N3698388)
    {
        if (N2199548 % N3698388 == 0)
        {
            N5975786 = false;
            break;
        }
    }
    return N5975786;
};
int main()

{
    N3593479 = false;
    cout << "Enter a positive  integer: ";
    cin >> N4091257;
    for (N5107470 = 2; N5107470 <= N4091257/2; ++N5107470)
    {
        if (N2919495(N5107470))
        {
            if (N2919495(N4091257 - N5107470))
            {
                cout << N4091257 << " = " << N5107470 << " + " << N4091257-N5107470 << endl;
                N3593479 = true;
            }
        }
    }
    if (!N3593479)
    {
        cout << N4091257 << " can't be expressed as sum of two prime numbers.";
    }
    return 0;
};
