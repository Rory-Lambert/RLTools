
#simple decorator for debugging.
# Prints the function/method name whenever it is called
def dump_func_name(func):
    def echo_func(*func_args, **func_kwargs):
        print('')
        print('Start func: {}'.format(func.__name__))
        return func(*func_args, **func_kwargs)
    return echo_func