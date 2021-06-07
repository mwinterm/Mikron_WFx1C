#linuxcnc_timer.py

import time


class Timer(object):
    def __init__(self, value=None):
        self._start_time = None
        self._is_active = None
        self._time_value = value
        self._alarm = False
        self._started = False

    def start(self):
        if(not self._started):
            self._start_time = time.time()
            self._is_active = True
            self._alarm = False
            self._started = True

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        self._is_active = False
        self._alarm = False
        self._started = False

    def update(self):
        if(self._time_value and self._is_active):
            elapsed = time.time() - self._start_time
            if(elapsed > self._time_value):
                self._alarm = True
                self._is_active = False
                
    def start_time(self):
        return self._start_time
        
    def time(self):
        self.update()
        if self._is_active and self._time_value:
            return time.time() - self._start_time
        else: 
            return -1.0

    def __call__(self):
        self.update()
        if self._is_active:
            return True
        else:
            return False
        
    def alarm(self):
        self.update()
        return self._alarm

     

