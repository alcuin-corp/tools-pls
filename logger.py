import colorama as c

c.init()

class Logger:
    def ok(self, message):
        print(f'[  {c.Fore.GREEN}OK{c.Fore.RESET}  ] {c.Fore.BLUE}({self.__class__.__name__}){c.Fore.RESET}\t{message}')
    def error(self, message):
        print(f'[  {c.Fore.RED}ERROR{c.Fore.RESET}  ] {c.Fore.BLUE}({self.__class__.__name__}){c.Fore.RESET}\t{message}')
        