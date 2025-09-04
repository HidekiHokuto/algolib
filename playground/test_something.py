from algolib.numerics import set_backend, get_backend_name
from algolib.numerics.trig import sin, cos, tan
from algolib.maths.number_theory.prime import is_prime
from algolib.numerics.exp import exp
from algolib.numerics.hyper import atanh
import math

print("I'm Yuanxun")
print("I'm Joshua")

# 1) 切换到 system backend（就是用 math 库）
set_backend("system")
print("Backend:", get_backend_name())
print("tan(pi/2) ~", tan(3.1415926 / 2))
print("sin(pi/2) ~", sin(3.1415926 / 2))
print("cos(pi/2) ~", cos(3.1415926 / 2))

# 2) 切换到 pure backend（就是你自己写的 trig_pure）
set_backend("pure")
print("Backend:", get_backend_name())
print("tan(pi/2) ~", tan(3.1415926 / 2))
print("sin(pi/2) ~", sin(3.1415926 / 2))
print("cos(pi/2) ~", cos(3.1415926 / 2))

# 3) 其它库照常用
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

