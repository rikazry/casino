import pandas as pd
import random as rd


def mc(scenario_func, iters = 10000, *args):
    '''
    scenario_func: function that is to be called each iteration
    iters: number of iterations for this simulation
    *args: argument parameter for the scenario_func
    '''
    df = pd.DataFrame()
    cnt = 0
    res = 0
    while(cnt < iters):
        print "Current iteration: %d" % cnt
        df = df.append(scenario_func(*args))
        cnt = cnt+1
    return df

def oscar_func(p, capital, prints = False):
    '''
    p: player's probability of winning each game
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
                if capital + pnl < 0:
                    # bust!!
                    break
            else:
                break
        else:
            pnl = pnl - cur_unit
            drawdown = max(abs(pnl), drawdown)
    return pd.DataFrame({'pnl':[pnl], 'max_unit_size':[cur_unit], 'max_drawdown':[drawdown]})

if __name__ == '__main__':
    iters = 1000
    p = 0.48
    capital = 80
    df = mc(oscar_func, iters, p, capital)
    df = df.sort(['max_drawdown'],ascending=[0])
    num_busts = len(df[df.pnl<0])
    pct_busts = num_busts/iters
    print "\nBust count: %d/%d" % (num_busts, iters)

    # print stats of non-busted scenarios
    print "\nMeans (excluding busted scenarios):\n%s" % df[df.pnl>0].mean()
    print "\nMedian (excluding busted scenarios):\n%s" % df[df.pnl>0].median()
    print "\nMax (excluding busted scenarios):\n%s" % df[df.pnl>0].max()
    
