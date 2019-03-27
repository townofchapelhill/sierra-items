import re
import inspect
import threading
# data = [1, 2, 3, 4, 5, 6]

# def f1(x):
#     return 3 * x

# def f2(x):
#     try:
#         return x > 3
#     except:
#         return 0

# result = list(map(f1, list(filter(f2, data))))
# print("result: " + str(result))

# result1 = list(map(lambda r: r * 3, filter(f2, data)))
# print("result1: " + str(result1))

# pat = re.compile(r"(?P<c>(?P<a>[A-Z][a-zA-Z]*)\s*(?P<b>[A-Z][a-zA-Z]*))")
# x = pat.match("Oliver Twist by Charles Dickens")
# print(x.group("b"))

# def bar (x, *y, **z):
#     return x, y, z

# print(bar(5,6,7, a=7, b=8))

# data={'a':[3,4,5],
#       'b':{'c':[5,6,7],
#            'd':[8,9,10],
#            'e':{'f':11, 'g':12, 'h':13}
#            },
#       'i':{'j':[14,15,{'k':16,'l':17} ],
#            'l':['m', 'n', ['o', 'p', 'q']]}}

# def foo(d,pre=(),res={}) :
#     if isinstance(d,dict) :
#         for i in d :
#             foo(d[i], pre=pre+(i,), res=res)
#     elif isinstance(d,list) :
#         for i in enumerate(d) :
#             foo(i[1], pre=pre+(i[0],), res=res)
#     else :
#         res[pre] = d
#     return res
   
# r = foo(data)
# print(r)

# class CM(object):
#     def __enter__(self):
#       print("Raising OSError 1")
#       raise OSError()
#       return self

#     def __exit__(self,exc_type, exc_val, exc_tb):
#       print("Exiting")
#       return False

# c = CM()
# with c:
#     try:
#       print("Raising ValueError 2")
#       raise ValueError()
#     except ValueError:
#       print("Exception caught")

# vector = [[1,2],[3,4],[5,6],[7,8],[9,10]]

# b = ( x for y in vector for x in y if x % 2 == 0 )
# print(list(b))

# class Foo(object):
#     @classmethod
#     def class_foo(cls):
#         print("Class method for the class: %s" % cls)
# Foo.class_foo()

# class Foo(object):
#     def class_foo():
#         print("Class method for the class: %s" % cls)
#     class_foo = classmethod(class_foo)
# Foo.class_foo()

# exec_list = [3,4,5,6]
# wait_list = [1,2,3,4]

# comb_list = reversed(list(zip(wait_list, exec_list))) 
# res = list(map(sorted, list(map(list, list(zip(*comb_list)))))) 
# print(res[0][-1],res[1][-1]) 

# for name, obj in inspect.getmembers(threading, inspect.isclass):
#     print(name)

# def compute():
#     d = {}
#     for c in (65, 97): # 'A' and 'a'
#         for i in range(26):
#             d[chr(i+c)] = chr((i+13) % 26 + c)
#     return d

# d = compute()
# print(d)

# s = "Hello Encryption"
# print("Encrypted:", "".join([d[c] for c in s]))

# for n in range(2, 10):
#     for x in range(2, n):
#         if n % x == 0:
#             break
#         else:
#             print(n)

# a=1
# b=1
# c=3

# class A(object):
#     def __init__(self):
#         print("%d" % a)
#         super(A,self).__init__()
#         print("<%d>" % a)

# class B(object):
#     def __init__(self):
#         print("%d" % b)
#         super(B,self).__init__()
#         print("<%d>" % b)

# class C(A,B):
#     def __init__(self):
#         print("%d" % c)
#         super(C,self).__init__()
#         print("<%d>" % c)

from functools import reduce
lst = list(range(5))
x = reduce(lambda x,y : x*y, lst)
print(x)