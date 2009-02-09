
def checkpoint():
    import inspect
    f = inspect.currentframe().f_back
    print '%s:%d: Function %s CHECKPOINT' % (__file__,f.f_lineno,f.f_code.co_name)
