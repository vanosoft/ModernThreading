# Documentation

## Table of contents

1. Decorators
2. Thread Environments
   1. Define an env
   2. Append thread to env
   3. Run thread
   4. Get thread return

## 1. Decorators

For create a single thread,
use decorator ```Thr.thread```:
```
from thr import Thr

@Thr.thread
def foo(a, b, c):
    print(a, b, c)
    pass
```
In a single threads value
returns not allowed.

## 2. Thread Environments

### 1. Define an environmenment
For define an env for threads,
use Thr.Env type:
```
foo = Thr.Env("FooEnv")
```

### 2. Append thread to environment
For append thread to the environment,
use decorator Thr.Env.append and ID
in docstring for convertation:
```
@foo.append
def egg(*args):
    """id_of_egg"""
    ret = 1
    for i in args:
        ret *= i
        pass
    return ret
```

### 3. Run thread in environment
For run env thread, use Thr.Env.append.run
method:
```
egg.run(1,2,3,4,5) # 5!
```

### 4. Get thread return
For get thread return,
1. test if thread already returned sth:
   ```if egg.ret:```
2. use Thr.Env.append.get method:
   ```bar = egg.get()```

or use Thr.append.getrun
method(waits for thread return and returns it):
```bar = egg.getrun()```
