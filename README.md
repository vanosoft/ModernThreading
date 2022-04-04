# ModernThreading
It is tiny module for better threading based on standard pythonic library "threading"
- -
very easy example:
```
from random import randint
from thr import Thr


Space = Thr.Env("3n+1")

@Space.append
def hdl(t, spc, ID, num):
    """3n+1_handle"""
    if num % 2 == 0:
        # значения возвращать так
        t.ret = True
        spc.rets[ID] = num/2
        return
    # значения возвращать так
    t.ret = True
    spc.rets[ID] = 3*num+1
    return

@Space.append
def loop(t, spc, ID, num):
    """3n+1_mainloop"""

    steps = 0

    while num not in (4, 2, 1):
        num = hdl.getrun(num)
        steps += 1
        pass
    # значения возвращать так
    t.ret = True
    spc.rets[ID] = steps
    return

print()
print(Space)
print()
print(repr(Space))

ticks = 0

num = randint(5, 100)

loop.run(num)

while not loop.ret:
    ticks += 1
    pass

print(f"loop reached 4 -> 2 -> 1 trap,"
      f"time has passed (loop ticks): "
      f"{ticks}, steps has passed: {loop.get()}, start number: {num}")
```
So,
- for create threadspace do ```your_space = Thr.Env("name")```,
- for create thread into threadspace:
  - append decorator ```@your_space.append```
  - append arguments ```t, spc, ID``` at start of arguments list
- for return value from thread do ```t.ret = True; spc.rets[ID] = your_value; return```
