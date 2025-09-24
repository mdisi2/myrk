from pyrk.timer import Timer
import sys
import time


class ProgressBar(object):
    """This class holds the progressbar
    and ETA functions for use in the driver.
    """


    def __init__(self, bar_len=50):
        self.fill = '#'
        self.bar_len = bar_len
        self.last_time = None
        self.avg_time = 0
        self.last_progress = 0

    def bar_update(self, timer=Timer()):
        """
        Updates the output to the terminal by calculating
        the average time between timesteps, finding out how
        many timesteps are left, then calculating the remaining 
        time.

        :param timer: The timer from the simulation input file
        :type timer: Timer() object  
        """

        # Responsible for filling the timebar
        progress = timer.current_timestep()
        total_len = timer.timesteps()
        percent = progress / total_len
        filled_len = int(percent * self.bar_len)
        bar = self.fill * filled_len + "-" * (self.bar_len - filled_len)

        eta_str = self.eta_string(now=time.time(),
                                  total_len=total_len,
                                  progress=progress,
                                  percent=percent)

        sys.stdout.write(f'\rProgress: [{bar}] | {int(percent * 100):02d}% | {eta_str}')

        sys.stdout.flush()


    def eta_string(self,now,total_len,progress,percent):
        
        if self.last_time is None: # Initializing for start of sim
            self.last_time = now
            self.avg_time = 0
            self.last_progress = progress
            eta_str = ""
        
        else:
            step_time = now - self.last_time #Real time Inbetween steps
            steps = progress - self.last_progress #Integer step 
            if steps > 0:
                if self.avg_time == 0: # First timestep
                    self.avg_time = step_time / steps
                else:
                    self.avg_time = (self.avg_time * (progress - steps) \
                                        + step_time) / progress
            self.last_time = now
            self.last_progress = progress

            if percent > 0:
                eta = (total_len - progress) * self.avg_time
                hours = int(eta) // 3600
                minutes = (int(eta) % 3600 ) // 60
                seconds = int(eta) % 60
                eta_str = f"ETA {hours:02d}:{minutes:02d}:{seconds:02d}"

        return eta_str