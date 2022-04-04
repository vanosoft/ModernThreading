from curses.ascii import isalnum
from threading import Thread as thrd
from random import randrange
from sys import exit as exitall


__all__ = ['Thr']

# f-str не позволяет использовать "\" напрямую,
# пришлось выкручиваться =)
nl = "\n"
bs = "\b"
tb = "\t"
rt = "\r"

# просто полезная функция
def strcleanup(s: str = ""):
    while s[0]  == ' ': s = s[1:]
    while s[-1] == ' ': s = s[:-1]
    if not isalnum(s[0]): s = '_' + s
    s = s.replace(' ', '_')
    for i in range(len(s)):
        if not isalnum(s[i]):
            s = s.replace(s[i], '_')
            pass
        pass
    s += f"{randrange(100, 999)}"
    return s

# Класс для всего содержимого либы
class Thr:
    # класс для сред потоков
    class Env(object):
    
        # поля

        # потоки
        thrs: list = None
        # возвращаемые значения
        rets: dict = None
        # название среды
        name: str  = None
    
        # методы

        # инициализация
        def __init__(self, name):
            self.thrs = []
            self.rets = {}
            self.__name__ = self.name = name
            # self.name на всякий случай.
            # __name__ - магическая переменная, вдруг поменяется.
            pass

        # в строку
        __str__ = lambda self:\
    	    f"""ThreadSpace "{self.name}": {len(self.thrs)} threads"""
        
        # тоже в строку, но скорее для дебага, чем для печати юзеру
        __repr__ = lambda self:\
    	    f"""ThreadSpace "{self.name}"
    threads:
       {(nl+"       ").join(self.thrs)}
    total: {len(self.thrs)}
"""
        def __add__(self, other):
            self.thrs = {**self.thrs, **other.thrs}
            pass

        # Декоратор/метод для добавления в список потоков.
        def append(self, fn):
            # функции нужен docstring
            ID = strcleanup(fn.__doc__.casefold())
            self.thrs += [ID]
            self.rets[ID] = None
            #
            class Thrd(object):
                ID = None
                space = None
                fn = None
                thr = None
                runned = None
                ret = None
                def __init__(slf, ID, self, fn):
                    slf.ID = ID
                    slf.space = self
                    slf.fn = fn
                    slf.thr = None
                    slf.runned = False
                    slf.ret = False
                    pass
                def run(slf, *args):
                    if slf.runned:
                        print(f"Exception: Thread \"{slf.ID[:-3]}\" of threadspace \"{slf.space.name}\" already started")
                        exitall(1)
                        pass
                    slf.thr = thrd(target = slf.fn, args = (slf, slf.space, slf.ID, *args,))
                    slf.thr.start()
                    slf.runned = True
                    pass
                def join(slf):
                    if not slf.runned:
                        print(f"Exception: Thread \"{slf.ID[:-3]}\" of threadspace \"{slf.space.name}\" not started yet")
                        exitall(1)
                        pass
                    slf.thr.join()
                    slf.runned = False
                    pass
                def get(slf):
                    if not slf.ret:
                        print(f"Exception: Thread \"{slf.ID[:-3]}\" of threadspace \"{slf.space.name}\" didn`t return anything yet")
                        exitall(1)
                        pass
                    slf.runned = False
                    return slf.space.rets[slf.ID]
                def getrun(slf, *args):
                    slf.run(*args)
                    slf.join()
                    return slf.get()
                pass
            return Thrd(ID, self, fn)
        pass
    #  Декоратор для "голого" потока
    def thread(fn):
        def thr(*args, **kwargs):
            thrd(target = fn, args = (*args,), kwargs={**kwargs,}).start()
            pass
        return thr
    pass
# конец файла
