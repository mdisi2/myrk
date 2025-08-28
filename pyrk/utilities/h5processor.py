import matplotlib.pyplot as plt
import numpy as np
import os
import h5py

style_path = os.path.join(os.path.dirname(__file__), 'plotting.mplstyle')
plt.style.use(style_path)

# The th section reads two arrays, the component array
# and the temp array. The 'component' array is a continous
# list of the component names looping every timestep. The 
# temp array holds the temp for corresponding index of the
# component, also looping every timestep. Meaning Comp[0] 
# and Temp[0] refer to the first component's temperature
# at the first timestep. If I have 5 components, then 
# Comp[5] and Temp[5] refer to the same component at the 
# second timestep.

# The neutronics portion reads two tables, the omegas and 
# zetas tables. The both tables hold 3  arrays, the timestep
# (int), group index (int), and the actual data. These group
# indexes and corresponding data also loop for every timestep,
# similar to the th treatment.

class H5Processor(object):

    """
    This class handles post-processing of h5 database
    files for reconstructing plots or comparing multiple 
    simulations results against each other
      
    :param infile: Paths to .h5 files
    :infile type: list of os paths
    :param names: Names of .h5 files for graphing and storage
    :type names: list of names or single ['str'] when singular sim
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

        if names is None and len(self.infilelist) == 1:
            self.names = [None]
        elif names is None:
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

    def plot_thcomponent(self):

        os.makedirs(os.path.join(self.plotdir,'Components'), exist_ok=True)

        """
        Contructs plots of components from database file.
        For single inputs or comparisons across simulations 

        :param infilelist: a list of H5 file paths
        :param plotdir: the output directory 
        :param names: a list of the names corresponding to files
        """

        all_sims = []
        comps = None
        time_arrays = []

        for infile in self.infilelist:
            with h5py.File(infile) as file:
                timeseries = file['th']['th_timeseries']
                components = timeseries['component'][:]
                temps = timeseries['temp'][:]
                unique_comps = np.unique(components)
                unique_comps = [c.decode('utf-8') for c in unique_comps]
                if comps is None:
                    comps = unique_comps
                data = {c: [] for c in unique_comps}
                for c in unique_comps:
                    mask = (components == c.encode('utf-8'))
                    data[c] = temps[mask]

                all_sims.append(data)
                sim_info = file['metadata']['sim_info']
                t0 = sim_info['t0'][()]
                tf = sim_info['tf'][()]
                n_steps = len(temps)
                time_arr = np.linspace(t0, tf, n_steps)
                time_arrays.append((components, time_arr))

        for c in comps:
            plt.figure()
            for i, data_dict in enumerate(all_sims):
                components, time_arr = time_arrays[i]
                mask = (components == c.encode('utf-8'))
                plt.plot(time_arr[mask], data_dict[c], label=f"{self.names[i]}")
            plt.ylabel("Temperature [K]")
            plt.title(f"{c.capitalize()} Temperature")
            path = os.path.join(self.plotdir, 'Components', f"{c.capitalize()}_comparison.png")
            self.style(path)
        
        if self.multisim is True:
            self.plot_difference_th()

    def plot_difference_th(self):

        os.makedirs(os.path.join(self.plotdir,'Difference'), exist_ok=True)

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
        comps = None
        time_arrays = []

        for infile in self.infilelist:
            with h5py.File(infile) as file:
                timeseries = file['th']['th_timeseries']
                components = timeseries['component'][:]
                temps = timeseries['temp'][:]
                unique_comps = np.unique(components)
                unique_comps = [c.decode('utf-8') for c in unique_comps]
                if comps is None:
                    comps = unique_comps
                data = {c: [] for c in unique_comps}
                for c in unique_comps:
                    mask = (components == c.encode('utf-8'))
                    data[c] = temps[mask]

                all_sims.append(data)
                sim_info = file['metadata']['sim_info']
                t0 = sim_info['t0'][()]
                tf = sim_info['tf'][()]
                n_steps = len(temps)
                time_arr = np.linspace(t0, tf, n_steps)
                time_arrays.append((components, time_arr))

        for c in comps:
            for i in range(len(all_sims)):
                for j in range(i + 1, len(all_sims)):

                    if len(all_sims[i][c]) != len(all_sims[j][c]):
                        print(f"Component '{c}' has different lengths in simulations {i} and {j}")
                        break
                    diff = np.abs(np.array(all_sims[i][c]) - np.array(all_sims[j][c]))
                    components, time_arr = time_arrays[i]
                    mask = (components == c.encode('utf-8'))
                    plt.figure()
                    plt.plot(time_arr[mask], diff, label=f"{self.names[i]} - {self.names[j]}", color=self.color(j % len(comps)))
                    plt.ylabel(r"$\Delta$ Temp")
                    plt.title(f"{c.capitalize()} Absolute Difference: {self.names[i]} vs {self.names[j]}")
                    path = os.path.join(self.plotdir, 'Difference', f"{c.capitalize()}_difference_{self.names[i]}_{self.names[j]}.png")
                    self.style(path)

    def plot_power_rho(self):

        os.makedirs(os.path.join(self.plotdir,'Neutronics','Power_and_Rho'), exist_ok=True)

        """
        Treatment for the neutronics and power
        section of the database.
        """

        for idx, infile in enumerate(self.infilelist):
            with h5py.File(infile) as f:
                n = f['neutronics']['neutronics_params']
                m = f['metadata']['sim_timeseries']
                t = f['metadata']['sim_info']
                t_arr = np.linspace(t['t0'], t['tf'], len(n['t_idx']))


                #finding total power
                power_tot = f['metadata']['sim_info']['power_tot']

                fig,ax1 = plt.subplots()
                ax1.plot(t_arr, power_tot * m['power'], label='Power', color="#332288")
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

                plt.title(f'Power vs Reactivity | {self.names[idx]}')
                filepath = os.path.join(self.plotdir, 'Neutronics', 'Power_and_Rho' , f'{self.names[idx]}_rho_and_power.png')
                self.style(filepath)

        if self.multisim is True:
            data = []
            for infile in self.infilelist:
                with h5py.File(infile) as f:
                    m = f['metadata']['sim_timeseries']
                    t = f['metadata']['sim_info']
                    data.append({'time_arr': np.linspace(t['t0'], t['tf'], len(m['power'])),
                                'p_arr': m['power']})

            plt.figure()
            for idx, sim in enumerate(data):
                plt.plot(sim['time_arr'], sim['p_arr'], label=f'{self.names[idx]}')

            plt.title('Power Comparison')
            plt.ylabel('Power [normalized]')
            plt.legend()
            filepath = os.path.join(self.plotdir, 'Neutronics', 'power_comparison.png')
            self.style(filepath)

    def plot_zetas(self):

        """
        Goes through the h5/neutronics/zetas table
        and plots results on a single graph. One graph
        per simulation passed.

        """

        os.makedirs(os.path.join(self.plotdir,'Neutronics','Zetas'), exist_ok=True)

        for infile in self.infilelist:
            x = self.infilelist.index(infile)
            with h5py.File(infile) as f:
                zetas = f['neutronics']['zetas']
                zdata = zetas['zeta'][:]
                z_idx = zetas['zeta_idx'][:]
                t_idx = zetas['t_idx'][:]

                sim_info = f['metadata']['sim_info']
                t0 = sim_info['t0'][()]
                tf = sim_info['tf'][()]
                n_steps = len(np.unique(t_idx))
                time_arr = np.linspace(t0, tf, n_steps)
                time_map = {idx: time_arr[i] for i, idx in enumerate(sorted(np.unique(t_idx)))}
                t_sec = np.array([time_map[idx] for idx in t_idx])

                plt.figure()
                unique_zeta_idx = np.unique(z_idx)
                for group in unique_zeta_idx:
                    mask = (z_idx == group)
                    plt.plot(t_sec[mask], zdata[mask], label=f'Group {group}')
                plt.ylabel(r"Concentration of Neutron Precursors, $\zeta_i [\#/dr^3]$")
                plt.xlabel("Time [s]")
                plt.title(r"Concentration of Neutron Precursors, $\zeta_i [\#/dr^3]$")
                plt.legend()
                path = os.path.join(self.plotdir, 'Neutronics', 'Zetas', f'zetas_{self.names[x]}.png')
                self.style(path)

    def plot_omegas(self):

        """
        Goes through the h5/neutronics/omega table
        and plots data on a single graph. One graph
        per simulation passed.

        """

        os.makedirs(os.path.join(self.plotdir,'Neutronics','Omegas'), exist_ok=True)

        for infile in self.infilelist:
            x = self.infilelist.index(infile)
            with h5py.File(infile) as f:
                omegas = f['neutronics']['omegas']
                odata = omegas['omega'][:]
                o_idx = omegas['omega_idx'][:]
                t_idx = omegas['t_idx'][:]

                sim_info = f['metadata']['sim_info']
                t0 = sim_info['t0'][()]
                tf = sim_info['tf'][()]
                n_steps = len(np.unique(t_idx))
                time_arr = np.linspace(t0, tf, n_steps)
                time_map = {idx: time_arr[i] for i, idx in enumerate(sorted(np.unique(t_idx)))}
                t_sec = np.array([time_map[idx] for idx in t_idx])
                
                unique_omega_idx = np.unique(o_idx)
                plt.figure()
                for group in unique_omega_idx:
                    mask = (o_idx == group)
                    plt.plot(t_sec[mask], odata[mask], label=f'Group {group}')
                plt.ylabel(r'Decay Heat Fractions, $\omega_i [\#/dr^3]$')
                plt.title(r'Decay Heat Fractions, $\omega_i [\#/dr^3]$')
                plt.legend()
                path = os.path.join(self.plotdir, 'Neutronics', 'Omegas', f'omegas_{self.names[x]}.png')
                self.style(path)

    def h5plot(self):

        self.plot_thcomponent()
        self.plot_power_rho()
        self.plot_zetas()
        self.plot_omegas()

    def style(self, path):
        plt.legend()
        plt.grid(True)
        plt.xlabel(r'Time $[s]$')
        plt.tight_layout()
        plt.savefig(path, dpi=300, format='png')
        plt.close()
        print(f"Saved {path}")