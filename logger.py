import colorama as c
import inspect

c.init()

def __caller__():
    return inspect.getouterframes(inspect.currentframe())[2].function

class Logger:
    def ok(self, message):
        print(f'[  {c.Fore.GREEN}OK{c.Fore.RESET}  ] {c.Fore.BLUE}({self.__class__.__name__}::{__caller__()}){c.Fore.RESET}  {message}')
    def error(self, message):
        print(f'[  {c.Fore.RED}ERROR{c.Fore.RESET}  ] {c.Fore.BLUE}({self.__class__.__name__}::{__caller__()}){c.Fore.RESET}  {message}')
        