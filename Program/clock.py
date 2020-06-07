from time import time

times = {}
print_time, print_count = 0,0
    
def __call__(identifier):
    times[identifier]=time()
def difference(start, stop):
    now = time()
    return times.get(stop,now)-times.get(start,now)

_print = print
def print(*args, **kwargs):
    global print_time, print_count
    print_time -= time()
    _print(*args, **kwargs)
    print_time += time()
    print_count += 1
def clear():
    times.clear()
def average_print_time():
    if print_count:
        return print_time/print_count
    else:
        return 0

#And now, for somthing completely different...
#We morph into a class to support __call__!
import sys
class clock:
    def __call__(self, identifier):
        __call__(identifier)
    def __getattr__(self, name):
        return globals()[name]
    
sys.modules[__name__] = clock()
