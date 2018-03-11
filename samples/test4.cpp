#include<iostream>
#include<vector>

using namespace std;

int counter;

void heapify(vector<long>& h, int pos, int n, bool b)
{
	while (pos < n)
	{
		if (((2 * pos + 1 < n) && (2 * pos + 2 < n)))
		{
			int i;

			if (h[2 * pos + 1] <= h[2 * pos + 2]) 
				i = 2 * pos + 2;
			else
				i = 2 * pos + 1;

			if (h[i] > h[pos])
			{
				swap(h[pos], h[i]);
				pos = i;
			}
			else
				break;
		}
		else { 
			if (2 * pos + 1 < n)
			{
				if (h[pos] < h[2 * pos + 1])
				{
					swap(h[pos], h[2 * pos + 1]);
					pos = 2 * pos + 1;
				}
				else
					break;
			}
			else
				break;
		}
		
		counter++;
	}
}

void pyramyd_sort(vector<long>& h, int n)
{
	for (int i = n - 1; i >= 0; i--)
		heapify(h, i, n, false);

	int size = n;
	while (size > 1) 
	{
		swap(h[0], h[size - 1]);
		size--;
		heapify(h, 0, size, true);
	}
}

int main()
{
	counter = 0;

	long n;
	cin >> n;
	
	vector<long> h;

	for (int i = 0; i < n; i++)
	{
		long a;
		cin >> a;
		h.push_back(a);	
	}

	pyramyd_sort(h, n);

	cout << counter << endl;
}