import matplotlib.pyplot as plt
import numpy as np
import os
import h5py
plt.style.use(os.path.join(os.path.dirname(__file__), 'plotting.mplstyle'))

# TODO convert into an object so the module can be imported to plotter
# TODO clean up all code its so poor
# TODO Think of a the actual intent. This was meant to compare 
#      multiple simulation together, I don't neccesarily think
#      we should replace the current plotting function. Maybe 
#      this can live inside the current plotting function as 
#      a secondary utility?

# The thermal hydralic portion stores two arrays,
# the component array and the temp array. The 'component'
# array is a continous list of the names of the components,
# looping every timestep. The temp array holds the temp for 
# corresponding index of the component, also looping every 
# timestep. Meaning Comp[0] and Temp[0] refer to the first 
# component's temperature at the first timestep. If I have 5 
# components, then Comp[5] and Temp[5] refer to the same 
# component at the second timestep. There is probably a better
# way using enumerate to match all these up to one another than
# what I did using the modulo opporator and np.unique.  


# As a class, it will take a list of paths and a list of names for each simulation


class H5Processor(object):

    """
    This class handles post-processing of h5 database
    files for reconstructing plots or comparing multiple 
    simulations together

      
    :param infile: Paths to .h5 files
    :infile type: list or str when singular sim
    :param names: Names of .h5 files for graphing and storage
    :type names: list of str
    :param plotdir: Directory of output files
    :type plotdir: os path


    """

    def __init__(self,
                 infile = None,
                 names = None,
                 plotdir = None):
        
        if not isinstance(infile, list):
            self.infilelist = list(infile)
        else:
            self.infilelist = infile

        if names is None:
            self.names = [f'Simulation {i + 1}' for i in range(len(self.infilelist))]
        elif isinstance(names, str):
            self.names = [names]
        elif isinstance(names, list):
            if len(names) != len(self.infilelist):
                raise ValueError("Length of names must match number of input files")
            self.names = names
        else:
            raise TypeError("Refer to Documentation")
            
        self.plotdir = plotdir
        if self.plotdir is not None:
            os.makedirs(self.plotdir, exist_ok=True)

        if len(self.infilelist) > 1:
            self.multisim = True
        else:
            self.multisim = False

    def color(self,n):
        colors = ["#332288", "#117733",
                "#44AA99", "#88CCEE", 
                "#DDCC77", "#CC6677", 
                "#AA4499", "#882255"]
        return colors[n]

    def plot_thcomponent(self, infilelist=None, names=None, plotdir=None):
        
        if infilelist is None:
            infilelist = self.infilelist
        if names is None:
            names = self.names
        if plotdir is None:
            plotdir = self.plotdir

        os.makedirs(os.path.join(self.plotdir,'Components'), exist_ok=True)

        """
        Constructs the graphs for the components given the database file

        :param infilelist: H5 file path
        :param plotdir: the output directory
        """

        if not self.multisim: # single sim case

            infile = infilelist[0]

            with h5py.File(infile) as file:
                timeseries = file['th']['th_timeseries']
                components = timeseries['component'] ### List of every component
                temps = timeseries['temp'] ### List of every temp
                components = np.unique(components)
                comps = [component.decode('utf-8') for component in components]
                data = {c : [] for c in comps}

                for i in range(len(temps)):
                    data[comps[i % len(comps)]].append(temps[i])

                i = 0
                for key in data:
                    plt.figure()
                    plt.plot(data[key], label=f"{key.capitalize()}",color=self.color(i % len(comps)))
                    plt.xlabel("Time [S]")
                    plt.ylabel("Temperature [K]")
                    plt.title(f"{key.capitalize()} Temperature")
                    plt.legend()
                    path = os.path.join(plotdir,'Components',f'{key.capitalize()}.png')
                    plt.tight_layout()
                    plt.savefig(path,dpi=300,format='png')
                    print(f'Saved {path}')
                    plt.close()
                    i += 1
        
        if self.multisim: #multisimulation case
            self.plot_multiple_th()
            self.plot_difference_th()

    def plot_multiple_th(self, infilelist=None, names=None, plotdir=None):

        if infilelist is None:
            infilelist = self.infilelist
        if names is None:
            names = self.names
        if plotdir is None:
            plotdir = self.plotdir

        """
        For comparison of components across multiple simulations 

        :param infilelist: a list of H5 file paths
        :param plotdir: the output directory 
        :param names: a list of the names corresponding to files
        """

        all_sims = []

        for infile in infilelist:
            with h5py.File(infile) as file:
                timeseries = file['th']['th_timeseries']
                components = timeseries['component'] ### List of every component
                temps = timeseries['temp'] ### List of every temp
                components = np.unique(components)
                comps = [component.decode('utf-8') for component in components]
                data = {c : [] for c in comps}

                for i in range(len(temps)):
                    data[comps[i % len(comps)]].append(temps[i])

                all_sims.append(data)

        for c in comps:
            plt.figure()
            for i, data_dict in enumerate(all_sims):
                if c in data_dict:
                    plt.plot(data_dict[c], label=f"{self.names[i]}")
            plt.xlabel("Time [S]")
            plt.ylabel("Temperature [K]")
            plt.title(f"{c.capitalize()} Temperature")
            plt.legend()
            path = os.path.join(plotdir, 'Components', f"{c.capitalize()}_comparison.png")
            plt.tight_layout()
            plt.savefig(path, dpi=300,format='png')
            print(f"Saved {path}")
            plt.close()

    def plot_difference_th(self, infilelist=None, names=None, plotdir=None):

        if infilelist is None:
            infilelist = self.infilelist
        if names is None:
            names = self.names
        if plotdir is None:
            plotdir = self.plotdir

        """
        Plots the absolute difference between components of 
        multiple simulations.
        
        If the number of sims is greater than 2, 
        the differences will be pairwise 

        Ex:                 (1 & 2) , (1 & 3) , (2 & 3)

        :param infilelist: a list of H5 file paths
        :param plotdir: the output directory 
        :param names: a list of the names corresponding to files
        """
        all_sims = []
        os.makedirs(os.path.join(plotdir,'Difference'), exist_ok=True)

        for infile in infilelist:
            with h5py.File(infile) as file:
                timeseries = file['th']['th_timeseries']
                components = timeseries['component']
                temps = timeseries['temp']
                components = np.unique(components)
                comps = [component.decode('utf-8') for component in components]
                data = {c: [] for c in comps}

                for i in range(len(temps)):
                    data[comps[i % len(comps)]].append(temps[i])

                all_sims.append(data)

        for c in comps:
            for i in range(len(all_sims)):
                for j in range(i + 1, len(all_sims)):

                    diff = np.abs(np.array(all_sims[i][c]) - np.array(all_sims[j][c]))

                    plt.figure()
                    plt.plot(diff, label=f"{self.names[i]} - {self.names[j]}",color = self.color(j % len(comps)))
                    plt.xlabel("Time [s]")
                    plt.ylabel(r"$\Delta$ Temp")
                    plt.title(f"{c.capitalize()} Absolute Difference: {self.names[i]} vs {self.names[j]}")
                    plt.legend()
                    path = os.path.join(plotdir, 'Difference', f"{c.capitalize()}_difference_{self.names[i]}_{self.names[j]}.png")
                    plt.tight_layout()
                    plt.savefig(path, dpi=300, format='png')
                    print(f"Saved {path}")
                    plt.close()


    def plot_neutronics(self, infilelist=None, names=None, plotdir=None):

        if infilelist is None:
            infilelist = self.infilelist
        if names is None:
            names = self.names
        if plotdir is None:
            plotdir = self.plotdir

        os.makedirs(os.path.join(plotdir,'Neutronics'), exist_ok=True)

        """
        Treatment for the neutronics and power
        section of the database.
        """

        for idx, infile in enumerate(infilelist):
            with h5py.File(infile) as f:
                n = f['neutronics']['neutronics_params']
                m = f['metadata']['sim_timeseries']
                t = f['metadata']['sim_info']
                t_arr = np.linspace(t['t0'], t['tf'], len(n['t_idx']))

                figs,ax1 = plt.subplots()
                ax1.plot(t_arr, m['power'], label='Power (Normalized)', color="#332288")
                ax1.set_xlabel('Time [s]')
                ax1.set_ylabel('Power [watts]')
                ax1.tick_params(axis='y', color="#332288")

                ax2 = ax1.twinx()
                ax2.plot(t_arr, n['rho_ext'], label='External Reactivity', color="#AA4499")
                ax2.plot(t_arr, n['rho_tot'], label='Total Reactivity', color="#882255")
                ax2.set_ylabel(r'Reactivity $\rho$')
                ax2.tick_params(axis='y', color="#CC6677")

                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

                plt.title(f'Power vs Reactivity | {names[idx]}')
                plt.tight_layout()
                filepath = os.path.join(plotdir, 'Neutronics', f'{names[idx]}_rho_and_power.png')
                plt.savefig(filepath, dpi=300, format='png')
                print(f'Saved {filepath}')
                plt.close()

        if self.multisim: #True! if mutlisim
            data = []
            for infile in infilelist:
                with h5py.File(infile) as f:
                    m = f['metadata']['sim_timeseries']
                    t = f['metadata']['sim_info']
                    data.append({'time_arr': np.linspace(t['t0'], t['tf'], len(m['power'])),
                                'p_arr': m['power']})

            plt.figure()
            for idx, sim in enumerate(data):
                plt.plot(sim['time_arr'], sim['p_arr'], label=f'{names[idx]}')

            plt.title('Power Comparison')
            plt.xlabel('Time [s]')
            plt.ylabel('Power [normalized]')
            plt.legend()
            filepath = os.path.join(plotdir, 'Neutronics', 'power_comparison.png')
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, format='png')
            print(f'Saved {filepath}')
            plt.close()