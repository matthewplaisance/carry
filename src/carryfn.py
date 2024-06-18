import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import root_scalar

def lease(df:pd.DataFrame,ri,loe_percent,acre_price,dc,oil_price,leasor_bonus):
    df = df.copy()
    cml_ni = 1 - ri
    intial_cost = dc + 100*acre_price

    df["Gross AT"] = df["Monthly Oil Production"]*oil_price*.954
    df["Net CML"] = df["Gross AT"]*cml_ni - df["Gross AT"]*loe_percent
    df['month'] = df.index + 1

    running_sum = df["Net CML"].cumsum()
    payout_idx = running_sum[running_sum > intial_cost].index[0]
    
    splitrow = df.loc[payout_idx].copy()

    need = intial_cost - running_sum[payout_idx-1] 
    ratio = need/df.loc[payout_idx,'Net CML'] 
    payout_row = splitrow*ratio
    df.loc[payout_idx] *= (1-ratio)
    df.loc[payout_idx,'month'] /= (1-ratio)

    pt = splitrow['month'] - 1 + ratio
    payout_row['month'] = pt
    
    #add drilling costs
    df_extend = pd.concat([df,pd.DataFrame({
        'Monthly Oil Production':[0,payout_row['Monthly Oil Production']],'Gross AT':[0,payout_row['Gross AT']],'LOE':[0,None],
        'Net CML':[-intial_cost,payout_row['Net CML']],
        'month':[0,payout_row['month']]
    })]).reset_index(drop=True)

    return solver_irr(df_extend),pt

def carried(df:pd.DataFrame,carry,loe_percent,ri,dc,oil_price,acre_price):
    df = df.copy()
    #if carry == 0: return lease(df,ri,loe_percent,acre_price,dc,oil_price,None)
    ri -= carry*.25 #if carried they do not get royalty
    ni = 1 - ri
    niCML_apo = 1 - ri - carry
    intial_cost = (1-carry)*100*acre_price + dc

    df["Gross AT"] = df["Monthly Oil Production"]*oil_price*.954
    df["LOE"] = df["Gross AT"]*loe_percent
    
    df["Net CML"] = df["Gross AT"]*ni - df['LOE']
    df['month'] = df.index + 1

    running_sum = df["Net CML"].cumsum()
    payout_idx = running_sum[running_sum > intial_cost].index[0]
    
    #split row into bpo and apo
    splitrow = df.loc[payout_idx].copy()

    need = intial_cost - running_sum[payout_idx-1] 
    ratio = need/df.loc[payout_idx,'Net CML'] 
    payout_row = splitrow*ratio
    df.loc[payout_idx] *= (1-ratio)
    df.loc[payout_idx,'month'] /= (1-ratio)

    pt = splitrow['month'] - 1 + ratio
    payout_row['month'] = pt
    
    
    df.loc[payout_idx:, 'Net CML'] = df.loc[payout_idx:, 'Gross AT'] * niCML_apo -  df.loc[payout_idx:, 'LOE'] * (1-carry)#discount loe for apo

    #add drilling costs
    df_extend = pd.concat([df,pd.DataFrame({
        'Monthly Oil Production':[0,payout_row['Monthly Oil Production']],'Gross AT':[0,payout_row['Gross AT']],'LOE':[0,payout_row['LOE']],
        'Net CML':[-intial_cost,payout_row['Net CML']],
        'month':[0,payout_row['month']]
    })]).reset_index(drop=True)
    npvv,df = npv(df_extend,.1)
    return solver_irr(df_extend),pt

def npv(df,irr):
    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net CML"]*((1+(irr/12))**(-(row['month'])))
    return df['PV of Row'].sum(),df

def solver_irr(df:pd.DataFrame):
    def npv_solver(irr,cfs:list):#cfs [[month,cf]]
        return sum([cf[1] / (1 + irr)**cf[0] for cf in cfs])
   
    cfs = df[['month', 'Net CML']]
    cfs = cfs.values.tolist()
    res = root_scalar(npv_solver,args=(cfs,),bracket=[0,1],method='brentq')
    irr = (1+res.root)**12-1#annually
    return 100*irr

def createDecline(df:pd.DataFrame):

    return

def main():
    pd.set_option('display.max_rows', None)  
    df = pd.read_csv('./data/prod250MBO.csv')
    ri_lease = .25
    leasor_percent = .15
    dc = 4350000
    oil_price = 80
    loe = .2#as percent of gross rev AT
    acre_price = 1200
    leasor_bonus = 6500
    oc = 10000
    cIrr,_ = carried(pd.read_csv('./data/prod250MBO.csv'),0,.2,ri_lease,dc,oil_price,2800)
    lIrr,_ = lease(pd.read_csv('./data/prod250MBO.csv'),ri_lease,.2,2800,dc,oil_price,None)
    print(f'cIrr {cIrr}')
    print(f'lIrr {lIrr}')
    
    exit()
    res = {
        'leasor percent':[],
        'Carry IRR':[],
        'Carry POT':[],
        'Lease IRR':[],
        'Lease POT':[],
        'Carry NPV i=10%':[]
        
    }
   
    for i in range(0,201):
        i = i/1000
        df = pd.read_csv('./prod250MBO.csv');ri_lease=.25
        lIRR,lPOT = lease(df,i,ri_lease,loe,acre_price,dc,oil_price,leasor_bonus)
        df = pd.read_csv('./prod250MBO.csv')
        cIRR,cPOT,cnpv,_ = carried(df,i,loe,ri_lease,dc,oil_price,acre_price)
        res['leasor percent'].append(i)
        res['Carry IRR'].append(cIRR)
        res['Carry NPV i=10%'].append(cnpv)
        res['Lease IRR'].append(lIRR)
        res['Lease POT'].append(lPOT)
        res['Carry POT'].append(cPOT)
    pd.DataFrame(res).to_excel('res700.xlsx',index=False)

        
if __name__ == "__main__": main()