class A():
    refresh = None

A.refresh="123"
b = A()
print(b.refresh,A.refresh)
b.refresh="456"
print(b.refresh,A.refresh)