from threading import Timer

def f():
    print ("world")

t = Timer(2.0, f)
t.start()
print ("hello")