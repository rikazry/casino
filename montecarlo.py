import pandas as pd
import random as rd
import itertools

def mc(scenario_func, iters, *args, **kwargs):
    '''
    scenario_func: function that is to be called each iteration. Expects\
            the return values to be a dictionary with key/values of the result\
            from that particular run. See oscar_func for example in sim.py
    iters: number of iterations for this simulation
    *args: argument parameter for the scenario_func
    **kwargs: print_progress (True/False)
    '''

    # by default, don't pring progress
    print_progress = kwargs.get("print_progress", False)

    # always print out the passed in arguments
    print "iteration: %d\nargs:%s\nkwargs:%s\n" % (iters, args, kwargs)

    results = list()
    cnt = 0
    res = 0
    while(cnt < iters):
        if print_progress:
            print "Current iteration: %d" % cnt
        results.append(scenario_func(*args))
        cnt = cnt+1
    
    return pd.DataFrame(results, index = range(iters))

def optimize_params(mc_iters, scenario_func, *args):
    '''
    scenario_func: function to be passed into monte carlo
    mc_iters: number of iterations for MC simulation under each parameter combo
    *args: lists of parameter range
    '''
    results = {}
    args_list = list(itertools.product(*args))
    print "mc_iters: %d\nscenario_func: %s\nargs:%s" % (mc_iters, scenario_func, args) 
    for arg in args_list:
        print "%s" % str(arg)
        
        # mc() returns a dataframe, so results[] is a dict where each key is the\
        # arguments passed for particular mc simulation
        results[str(arg)] = mc(scenario_func, mc_iters, *arg)
       
    # first create Panel (3D of dataframes) where each layer has 'item' identifier of\
    # mc arguments

    # second transpose that Panel such that the major axis is the mc args and minor axis\
    # is the mc iteration number. items are keys of dict returned by scenario_func\
    # (pnl, max_unit_size, max_drawdown using oscar_func as example)

    # third convert back the panel to hierarchical dataframe. Once this is done, the\
    # columns would be the items, and major/minor indexes -> major/minor axis
    
    # ie: Panel looks like this after the transpose
    #<class 'pandas.core.panel.Panel'>
    #Dimensions: 3 (items) x 6 (major_axis) x 100 (minor_axis)
    #Items axis: max_drawdown to pnl
    #Major_axis axis: (0.49, 10) to (0.5, 30)
    #Minor_axis axis: 0 to 99

    # once converted to dataframe, looks like this:
    #                   max_drawdown  max_unit_size  pnl
    #major      minor                                  
    #(0.49, 10) 0                 5              2    1
    return  pd.Panel(results).transpose('minor_axis','items','major_axis').to_frame()


if __name__ == '__main__':
    iters = 1000
    p = 0.48
    capital = 20
    df = mc(oscar_func, iters, p, capital, print_progress = True)
    df = df.sort(['max_drawdown'],ascending=[0])
    num_busts = len(df[df.pnl<0])
    pct_busts = num_busts/iters
    print "\nBust count: %d/%d" % (num_busts, iters)

    # print stats of non-busted scenarios
    print "\nMeans (excluding busted scenarios):\n%s" % df[df.pnl>0].mean()
    print "\nMedian (excluding busted scenarios):\n%s" % df[df.pnl>0].median()
    print "\nMax (excluding busted scenarios):\n%s" % df[df.pnl>0].max()
    
