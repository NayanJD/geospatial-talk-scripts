import random 
from math import pi, sqrt, cos, sin

for i in range(10):
    # print(random.uniform(0,1))
    t = 2 * pi * random.uniform(0,1)
    r = 20 * sqrt(random.uniform(0,1))

    x = 0 + r * cos(t)
    y = 0 + r * sin(t)

    print('x, y', (x,y))