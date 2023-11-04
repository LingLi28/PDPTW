from functools import wraps
import time
import csv

class Log(object):
    def __init__(self, logfile, type: str = None):
        self.logfile = logfile
        self.type = type

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            s_time = time.time()
            res = func(*args, **kwargs)
            e_time = time.time()
            with open(self.logfile, 'a', newline = '') as opened_file:
                writer = csv.writer(opened_file)
                func_name = func.__name__
                time_str = str(e_time - s_time)
                temp = [func_name, time_str]
                writer.writerow(temp)
            return res

        return wrapped_function