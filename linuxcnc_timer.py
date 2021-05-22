#linuxcnc_timer.py

import time


class Timer:
    def __init__(self, value=None):
        self._start_time = None
        self._is_running = None
        self._time_value = value

    def start(self):
        if(not self._is_running):
            self._start_time = time.time()
            self._is_running = True

    def stop(self):
        self._is_running = False

    def update(self):
        if(self._time_value and self._is_running):
            elapsed = time.time() - self._start_time
            if(elapsed > self._time_value):
                self.stop()
            

    def time(self):
        self.update()
        if self._is_running and self._time_value:
            return time.time() - self._start_time
        else: 
            return None

    def __call__(self):
        self.update()
        if self._is_running:
            return True
        else:
            return False
