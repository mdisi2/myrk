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
        Responsible for filling the timebar.

        :param timer: The timer from the simulation input file
        :type timer: Timer() object  
        """


        progress = timer.current_timestep()
        total_len = timer.timesteps()
        percent = progress / total_len
        filled_len = int(percent * self.bar_len)
        bar = self.fill * filled_len + "-" * (self.bar_len - filled_len)

        eta_str = self.calculate_eta(real_time=time.time(),
                                     total_len=total_len,
                                     progress=progress)

        sys.stdout.write(f'\rProgress: [{bar}] | {int(percent * 100):02d}% | {eta_str}')

        sys.stdout.flush()


    def calculate_eta(self,real_time,total_len,progress):
        """
        Responsible for Calculating ETA by first checking the amount of time inbetween timesteps 
        
            (real_time - last_time = time in seconds since the last timestep) 

        It then averages out the time inbetween steps and checks how many steps
        are left in the simulation.

        :param real_time: The current 'in real life time' like on a clock
        :param total_len: The number of timesteps in the time array of the sim
        :total_len type: int
        :param progress: the index of the current timestep of the time array
        """
        

        if self.last_time is None: # Initializing for start of sim
            self.last_time = real_time
            self.avg_time = 0
            self.last_progress = progress
            eta_str = ""
        
        else:
            step_time = real_time - self.last_time #Real time Inbetween steps
            steps = progress - self.last_progress 
            if steps > 0:
                if self.avg_time == 0: # First timestep
                    self.avg_time = step_time / steps
                else:
                    self.avg_time = (self.avg_time * (progress - steps) \
                                        + step_time) / progress
            self.last_time = real_time
            self.last_progress = progress

            eta = (total_len - progress) * self.avg_time
            hours = int(eta) // 3600
            minutes = (int(eta) % 3600 ) // 60
            seconds = int(eta) % 60
            eta_str = f"ETA {hours:02d}:{minutes:02d}:{seconds:02d}"

        return eta_str