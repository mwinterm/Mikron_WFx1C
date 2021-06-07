#debug.py

class Debug(object):
    def __init__(self, name="Debug", value = -1):
        self.__name = name
        self.__level = value
        self.__changed = True
        self._vocal = False
    
    @property
    def level(self):
        return self.__level
    
    @level.setter
    def level(self, value):
        if self.__level != value:
            self.__level = value
            self.__changed = True
            if self._vocal: 
                print(self.__name + ': ' + str(self.__level))

    def __str__(self):
        if self.__changed:
            self.__changed = False
            return self.__name + ': ' + str(self.__level)
        else:
            return ""

    def msg(self):
        if self.__changed:
            self.__changed = False
            print(self.__name + ': ' + str(self.__level))