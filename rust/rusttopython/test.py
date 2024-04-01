from test_test import calc_something
from time import time


def python_calc_something(n):
    primes = []
    for candidate in range(2, n + 1):
        is_prime = True
        for divisor in range(2, int(candidate ** 0.5) + 1):
            if candidate % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
    return primes



a = time()
for i in range(100_000):
    calc_something(1000)
print("rust:", time() - a)

a = time()
for i in range(100_000):
    python_calc_something(1000)
print("python", time() - a)
