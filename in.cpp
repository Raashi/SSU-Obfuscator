#include<iostream>
#include<vector>

using namespace std;

int main()
{
	int n;
	int m;

	cin >> n;

	vector<int> vec(n, 0);
	for (int i = 0; i < n; i++)
		cin >> vec[i];

	for (int i = 0; i < n; ++i)
		cout << vec[i] << ' ';
}