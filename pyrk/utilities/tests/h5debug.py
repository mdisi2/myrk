from pyrk.utilities.h5processor import H5Processor
import os

f1 = os.path.join(os.path.dirname(__file__), 'h5_examples', 'master.h5')
path = [f1]
out_dir = os.path.join(os.path.dirname(__file__), 'output')

Sim = H5Processor(infile=path,
                  names='example1',
                  plotdir=out_dir)

power_tot = Sim.power_total(infile=f1)

print(power_tot)
