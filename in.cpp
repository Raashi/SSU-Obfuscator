#include <iostream>
using namespace std;

// Check prime number
bool checkPrime(int n)
{
    int i;
    bool isPrime = true;

    for(i = 2; i <= n/2; ++i)
    {
        if(n % i == 0)
        {
            isPrime = false;
            break;
        }
    }

    return isPrime;
}

int main()
{
    int n;
    int i;
    bool flag = false;

    cout << "Enter a positive  integer: ";
    cin >> n;

    goto x;

    for(i = 2; i <= n/2; ++i)
    {
        if (checkPrime(i))
        {
            if (checkPrime(n - i))
            {
                cout << n << " = " << i << " + " << n-i << endl;
                flag = true;
            }
        }
    }

    x:

    if (!flag)
      cout << n << " can't be expressed as sum of two prime numbers.";

    return 0;
}