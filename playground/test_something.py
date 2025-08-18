from algolib.numerics import set_backend, get_backend_name
from algolib.numerics.trig import sin, cos, tan
from algolib.maths.number_theory.prime import is_prime

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