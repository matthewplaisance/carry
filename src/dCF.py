import pandas as pd

def dcf(target,intial_d,periods,start=None):
    cfs = [0 for _ in range(0,periods)]
    cfs[0] = target/periods if start == None else start
    s = sum(cfs)
    d = intial_d
    print(cfs)
    cnt = 0
    while abs(s-target)/((s+target)/2) > .1 and cnt < 100 :
        cnt += 1
        newcfs = [cfs[0]]
        print(f'd : {d}')
        for i in range(len(cfs)):
            if i != 0:
                newcfs.append(newcfs[i-1]*(1-d))
        s = sum(newcfs)
        if s > target: d +=.1
        else: d -= .1
        if d <= 0:d += .1; break
    print(d)
    print(newcfs)
    print(f'sum {s}')
    return 
dcf(4350000,.1,16,665000)