from algolib.maths.number_theory.prime import is_prime
from algolib.numerics.exp import exp
from algolib.numerics.hyper import atanh
import math

print("I'm Yuanxun")
print("I'm Joshua")


print("is_prime(29) =", is_prime(29))
print("is_prime(97) =", is_prime(97))


from algolib.algorithms.sort_demo import bubble_sort
import random
# 4) Bubble sort demo
arr = []

for i in range(100):
    arr.append(random.randint(1, 10000))
print("Original array:", arr)
print("Bubble sorted:", bubble_sort(arr))

print(exp(3) - math.exp(3))

print(atanh(1), atanh(0.0001))

