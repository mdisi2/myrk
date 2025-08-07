import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import h5py
plt.style.use(os.path.join(os.path.dirname(__file__), 'plotting.mplstyle'))


### Each timestep is a table with an array of all the components in a repeating loop. 
### There is also a corresponding temperature array that loops each timestep with the
### temp at the same index for that particular component. Meaning if mod0 is at component[0],
### then the temp for the component is at temp[0]. And if I had 5 components, mod0 at the
### second timestep would be like component[6] temp[6] MEANING I am going to use modulololo
### opporator methinks


### Need to check where the data is stored for the neutronics and make functions for those
### or add lines to the functions


# TODO determine if a script or a class
# TODO parse through neutronics, probably similar th_timeseries


def color(n):
    t = ["#332288", "#117733",
         "#44AA99", "#88CCEE", 
         "#DDCC77", "#CC6677", 
         "#AA4499", "#882255"]
    return t[n]


def plot_singular(infilelist,plotdir):

    """
    Constructs the graphs for the components given the database file

    :param infilelist: H5 file path
    :param plotdir: the output directory
    
    """

    infile = infilelist[0]
    os.makedirs(plotdir, exist_ok=True)

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
            plt.plot(data[key], label=f"{key.capitalize()}",color=color(i % len(comps)))
            plt.xlabel("Time [S]")
            plt.ylabel("Temperature [K]")
            plt.title(f"{key.capitalize()} Temperature")
            path = os.path.join(plotdir,f'{key.capitalize()}.png')
            plt.savefig(path,dpi=300,format='png')
            print(f'Saved {path}')
            plt.close()
            i += 1

def plot_multiple(infilelist,names,plotdir):

    """
    For comparison of components across multiple simulations 

    :param infilelist: a list of H5 file paths
    :param plotdir: the output directory 
    :param names: a list of the names corresponding to files
    """


    all_sims = []
    os.makedirs(plotdir, exist_ok=True)

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
                plt.plot(data_dict[c], label=f"{names[i]}")
        plt.xlabel("Time [S]")
        plt.ylabel("Temperature [K]")
        plt.title(f"{c.capitalize()} Temperature")
        path = os.path.join(plotdir, f"{c.capitalize()}_comparison.png")
        plt.savefig(path, dpi=300,format='png')
        print(f"Saved {path}")
        plt.close()


def plot_difference(infilelist, names, plotdir):
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
    os.makedirs(os.path.join(plotdir,'difference'), exist_ok=True)

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
                plt.plot(diff, label=f"{names[i]} - {names[j]}",color = color(j % len(comps)))
                plt.xlabel("Time [s]")
                plt.ylabel(r"$\Delta$ Temp")
                plt.title(f"{c.capitalize()} Absolute Difference: {names[i]} vs {names[j]}")
                plt.legend()
                path = os.path.join(plotdir, f"{c.capitalize()}_difference_{names[i]}_{names[j]}.png")
                plt.savefig(path, dpi=300, format='png')
                print(f"Saved {path}")
                plt.close()

def main():
    """ 
    Post processing using h5 database file for
    reconstrucing graphs and plotting multiple
    simulations against each other.

    run like:

    python3 postprocessing.py
    --infiles sim1.h5 sim2.h5
    --names Simulation1 Simulation2
    --plotdir testingfolder
    """

    parser = argparse.ArgumentParser(description='Parse through h5 database')
    parser.add_argument('--infiles', nargs='+', required=True, help='List of h5 files')
    parser.add_argument('--names', nargs='+', required=True, help='Names corresponding to the inputs')
    parser.add_argument('--plotdir', default='h5plots', help="Name of folder for plot output")
    args = parser.parse_args()

    if len(args.infiles) != len(args.names):
        parser.error("The number of --infiles must match the number of --names.")
    
    os.makedirs(args.plotdir, exist_ok=True)

    # the singular infile case
    if len(args.infiles) == 1:
        plot_singular(args.infiles, args.plotdir)

    # multiple infiles case
    else:
        plot_multiple(args.infiles, args.names, args.plotdir)
        plot_difference(args.infiles, args.names, args.plotdir)
    

if __name__ == "__main__":
    main()