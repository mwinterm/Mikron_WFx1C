# oneshot.py

from linuxcnc_timer import Timer

class mbool(object):
    def __init__(self, value = False):
        self.__state = value
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, value):
        self.__state = value
    

class Oneshot(object):
    def __init__(self, component, pin_name, shot_time=0.1):
        self._component = component
        self._pin_name = pin_name
        self._pin_old = getattr(component, pin_name)
        self._up_timer = Timer(shot_time)
        self._down_timer = Timer(shot_time)


    def update(self):
        if not self._pin_old and getattr(self._component, self._pin_name):
            self._up_timer.start()
            self._pin_old = True
            print("up_timer started")
        elif self._pin_old and not getattr(self._component, self._pin_name):
            self._down_timer.start()
            self._pin_old = False
            print("down_timer started")

    def up(self):
        self.update()
        return self._up_timer()

    def down(self):
        self.update()
        return self._down_timer()

    def change(self):
        self.update()
        if self._up_timer() or self._down_timer():
            return True
        else:
            return False
        

