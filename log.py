from colors import green

def log(message):
    def log_decorate(func):
        def func_wrapper(self, tenant):
            line = '-----------------------------------'
            print('\n' + line + '[[ ' + message + ' => ' + green(tenant.name) + ' ]]' + line)
            func(self, tenant)
        return func_wrapper
    return log_decorate