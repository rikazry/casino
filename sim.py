import montecarlo as mc
import random as rd
import pandas as pd

def oscar_func(p, capital, max_unit=None, prints = False):
    '''
    p: player's probability of winning each game
    capital: capital in terms of number of units
    max_unit: unit size where we take the stop loss
    '''
    pnl = 0
    cur_unit = 1
    drawdown = 0
    while(True):
        if prints:
            print "pnl: %d\ncur_unit: %d\ndrawdown: %d\n" % (pnl, cur_unit, drawdown)
        if rd.random() < p:
            pnl = pnl + cur_unit
            if pnl <= 0:
                cur_unit = min(cur_unit + 1, abs(pnl)+1)
            else:
                break
        else:
            pnl = pnl - cur_unit
            drawdown = max(abs(pnl), drawdown)
            if capital + pnl < 0:
                # bust!!
                break
            elif max_unit is not None and cur_unit == max_unit:
                #stop loss!!
                break
    return {'pnl':pnl, 'max_unit_size':cur_unit, 'max_drawdown':drawdown}

def martingale_func(p, capital, prints = False):
    pnl = 0
    cur_unit = 1
    drawdown = 0
    while(True):
        if prints:
            print "pnl: %d\ncur_unit: %s\ndrawdown: %d\n" % (pnl, cur_unit, drawdown)
        if rd.random() < p:
            pnl = pnl + cur_unit
            if pnl > 0:
                break
        else:
            pnl = pnl - cur_unit
            drawdown = max(abs(pnl), drawdown)
            if capital + pnl < 0:
                # bust
                break
            cur_unit = min(2*cur_unit, capital+pnl)
            if cur_unit == 0:
                break

    return {'pnl':pnl, 'max_unit_size':cur_unit, 'max_drawdown':drawdown}

def arithmetic_func(p, capital, prints = False):
    pnl = 0
    cur_unit = 1
    drawdown = 0
    while(True):
        if prints:
            print "pnl: %d\ncur_unit: %s\ndrawdown: %d\n" % (pnl, cur_unit, drawdown)
        if rd.random() < p:
            pnl = pnl + cur_unit
            if pnl > 0:
                break
        else:
            pnl = pnl - cur_unit
            drawdown = max(abs(pnl), drawdown)
            if capital + pnl < 0:
                # bust
                break
            cur_unit = min(1+cur_unit, capital+pnl)
            if cur_unit == 0:
                break

    return {'pnl':pnl, 'max_unit_size':cur_unit, 'max_drawdown':drawdown}


if __name__=='__main__':
    # p = 0.46:0.49, 0.001 increments
    p_list = [x*0.001 for x in range(460,490)]
    p_list = [0.48]

    # capitals = [10,11,...,100] times the betting unit
    capital_list = range(10,40)

    # max_unit stoploss
    max_units = range(3,20)

    # monte carlo iteration for each parameter combo
    mc_iterations = 10000

    # define all the scenario funcs that needs testing. 
    # values are the arguments to mc.optimze_params
    scenario_funcs = {
            'oscar':(oscar_func, p_list, capital_list),
            'mart':(martingale_func,p_list,capital_list),
            'arth':(arithmetic_func,p_list,capital_list),
            }

    results = {}
    for k in scenario_funcs:
        results[k] = mc.optimize_params(mc_iterations, *scenario_funcs[k])

    # groupby the result by the major axis, which is the parameter used for \
    # given mc simulation
    gps = {}
    pnls = {}
    bust_pct = {}
    for k in results:
        gps[k] = results[k].groupby(level=0)
        pnls[k] = gps[k].apply(lambda x:x.pnl.mean())
        bust_pct[k] = gps[k].apply(lambda x: 1-float(len(x[x.pnl>0]))/float(len(x)))

    df_pnls = pd.DataFrame(pnls)
    df_bust_pcts = pd.DataFrame(bust_pct)
