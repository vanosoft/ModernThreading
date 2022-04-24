from curses.ascii import isalnum
import re
from threading import Thread as thrd
from random import randrange
from sys import exit as exitall
from inspect import getsource as decompile
from types import GeneratorType
from typing import Any


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
            _fn = fn
            def fn(t, spc, ID, *args, **kwargs):
                ret = _fn(*args, **kwargs)
                t.ret = True
                spc.rets[ID] = ret
                pass
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
                def run(slf, *args, **kwargs):
                    if slf.runned:
                        print(f"Exception: Thread \"{slf.ID[:-3]}\" of threadspace \"{slf.space.name}\" already started")
                        exitall(1)
                        pass
                    slf.thr = thrd(target = slf.fn, args = (slf, slf.space, slf.ID, *args,), kwargs={**kwargs,})
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
            T = thrd(target = fn, args = (*args,), kwargs={**kwargs,})
            T.daemon = True
            T.start()
            pass
        return thr
    pass
#
# LexToken class -
# container for lexems (tokens)
# useful for operations with
# code syntax units
class LexToken(object):
    # Constructor
    def __init__(self, typ, val, pos) -> None:
        self.typ = typ
        self.val = val
        self.ps = pos

    # to str (output for user)
    def __str__(self) -> str:
        return '{\n\ttype: '+self.typ+',\n\tvalue: \"'+self.val+'\",\n\tpos: '+str(self.ps)+'\n}'
    
    # repr (debug output, or for posthandle)
    def __repr__(self) -> str:
        return str('LexToken{'+self.type()+':\"'+self.value()+'\":'+str(self.ps)+'}').replace('\n', '\\n')
    
    # getitem - for make it iterable
    def __getitem__(self, i) -> Any:
        return [self.type, self.val][i]
    
    # setitem - for make it iterable
    def __setitem__(self, i, value) -> None:
        if i == 0:
            self.typ = value
            pass
        elif i == 1:
            self.val = value
            pass
        else:
            raise IndexError('Sequence index out of range: ' + str(i))

    # returns type of token
    def type(self) -> str:
        return self.typ
    
    # returns value of token
    def value(self) -> str:
        return self.val

    # returns where this token was found
    def pos(self) -> int:
        return self.ps
    pass

# LexError class -
# Exception for posthandle
# catching, raises if syntax
# error on lexing stage has
# occured, usual fatal
class LexError(Exception):
    # Constructor
    #
    # Note:
    #   typ - maybe "unexpected" or "missing"
    def __init__(self, token, pos, typ='unexpected') -> None:
        self.token = token
        self.pos = pos
        self.type = typ
        pass
    pass

# Lex class -
# Class for lexer constructing
# uses RegExp for tokens detecting
# universal, can be used anywhere
class Lex(object):
    # Constructor
    #
    # rules - sequence of pairs
    # <typename, regexp>
    def __init__(self, rules) -> None:
        # init local variables
        self.pos = None
        self.buf = None
        idx = 1
        regex_parts = []
        self.group_type = {}

        # loop which generates one big regexp based on groups
        for typ, regex in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = typ
            idx += 1

        # catcantanate regexp`s
        self.regex = re.compile('|'.join(regex_parts), re.DOTALL)

    # method uses for input string to lex
    def input(self, buf) -> None:
        self.buf = buf
        self.pos = 0

    # generates once token per call
    def token(self) -> LexToken | None:
        # end of buf?
        if self.pos >= len(self.buf):
            return None
        else:
            # token detect
            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = LexToken(tok_type, m.group(groupname), self.pos)
                self.pos = m.end()
                return tok

            # if we're here, no rule matched
            raise LexError(LexToken('<unexpected>', self.buf[self.pos], self.pos), self.pos)

    # method to generate multiple tokens per call
    def tokens(self) -> GeneratorType:
        while 1:
            tok = self.token()
            if tok is None: break
            yield tok
        return -1
    pass

PYRULES = [
    ['ret', r'\s*return \s*(.*)'],
    ['other', r'.*']
]

# конец файла
