#debug.py

class Debug:
    def __init__(self, name='debug', level=-1):
        self.__level = level
        self.__name = name
        self.__output = True

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, my_level):
        self.__level = my_level
        self.__output = True
    
    def __str__(self):
        if self.__output:
            self.__output = False
            return self.__name + ": " + str(self.__level)
        else:
            return ''

    def msg(self):
        if self.__output:
            self.__output = False
            print(self.__name + ": " + str(self.__level))