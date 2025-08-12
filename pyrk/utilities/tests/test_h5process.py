from pyrk.utilities.h5processor import H5Processor
import os 


infilelist = [
    os.path.join(os.path.dirname(__file__),'h5_samples','pyrk2.h5'),
    os.path.join(os.path.dirname(__file__),'h5_samples','negative_rho_10sec.h5')
]

out = os.path.join(os.path.dirname(__file__),'test_h5out')

names = ['First','Second']

def test1():
    ## Test 1 - single file no name, output 
    #  should be neutronics graphs, component
    #  graphs, no difference graphs, and the 
    #  name checker should flag there is no 
    #  name input

    single_file = [infilelist[0]]
    test_1 = H5Processor(infile=single_file,
                         plotdir=out)
    
    test_1.plot_thcomponent()
    test_1.plot_neutronics()

#test1()

def test2():
    ## Test 2 - multiple files no name, output 
    #  should be neutronics graphs, component
    #  graphs, difference graphs, and the 
    #  name checker should flag there is no 
    #  name input

    test_2 = H5Processor(infile=infilelist,
                         plotdir=out)
    
    test_2.plot_thcomponent()
    test_2.plot_neutronics()

#test2()

def test3():
    ## Test 3 - multiple files, name list,
    #  output should be neutronics graphs, 
    #  component graphs, difference graphs

    test_3 = H5Processor(infile=infilelist,
                         names=names,
                         plotdir=out)
    
    test_3.plot_thcomponent()
    test_3.plot_neutronics()

test3()