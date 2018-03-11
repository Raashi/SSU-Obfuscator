#include <cstdio>
#include <iostream>

using namespace std;

int N6105865;
bool N8333933;
int N5580966;
int N0035591;
bool N5351357;

bool N9575033(int N8781480)

{
    N8333933 = true;
    for (N6105865 = 2; N6105865 <= N8781480/2; ++N6105865)
    {
        if (N8781480 % N6105865 == 0)
        {
            N8333933 = false;
            break;
        }
    }
    return N8333933;
};
int main()

{
    N5351357 = false;
    cout << "Enter a positive  integer: ";
    cin >> N5580966;
    for (N0035591 = 2; N0035591 <= N5580966/2; ++N0035591)
    {
        if (N9575033(N0035591))
        {
            if (N9575033(N5580966 - N0035591))
            {
                cout << N5580966 << " = " << N0035591 << " + " << N5580966-N0035591 << endl;
                N5351357 = true;
            }
        }
    }
    if (!N5351357)
    {
        cout << N5580966 << " can't be expressed as sum of two prime numbers.";
    }
    return 0;
};
