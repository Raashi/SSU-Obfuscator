#include <iostream>
#include <cstdio>
using namespace std;

int calculatePower(int base, int powerRaised)
{
    if (powerRaised != 1)
        return (base*calculatePower(base, powerRaised-1));
    else
        return 1;
}

int main()
{
    int base;
    int powerRaised;
    int result;

    cout << "Enter base number: ";
    cin >> base;

    cout << "Enter power number(positive integer): ";
    cin >> powerRaised;

    result = calculatePower(base, powerRaised);
    cout << base << "^" << powerRaised << " = " << result;

    return 0;
}