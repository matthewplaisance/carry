import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def lease(carry,operating_cost,df,price_acre,ri,dp,oil_price,irr):
    df["Net Revenue to CML"] = df["Monthly Oil Production"]*oil_price*.954*(1-ri) - operating_cost

    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))

    intial_cost = dp + carry*640*price_acre
    return npv(df=df,irr=irr,intial_cost=intial_cost),df["Net Revenue to CML"].sum()

def carried(df,carry,operating_cost,ri,dp,oil_price,irr):
    ri -= carry*.25 #if carried they do not get royalty
    ni = 1 - ri
    niCML_apo = 1 - ri - carry

    df["Net Revenue to NI"] = df["Monthly Oil Production"]*oil_price*.954*(ni) - operating_cost
    payout_info = {"found":False}
    curr_netRev = 0
    for idx, row in df.iterrows():
        curr_netRev += row["Net Revenue to NI"]
        if curr_netRev/dp >= 1 and payout_info["found"] is False:
            payout_info["found"] = True
            payout_info["idx"] = idx
            payout_info["needed"] = dp - (curr_netRev - row["Net Revenue to NI"])
        df.at[idx, 'Payout'] = curr_netRev/dp
    for idx,row in df.iterrows():
        if idx == payout_info["idx"]:#apply bpo and apo rules to respective amts
            bpo_amt = payout_info["needed"]
            apo_amt = row["Net Revenue to NI"] - bpo_amt
            
            rev_CMl = bpo_amt
            rev_CMl += ((apo_amt + operating_cost)/ni)*niCML_apo - operating_cost*(1-carry)
            df.at[idx,"Net Revenue to CML"] = rev_CMl
            continue
        if row["Payout"] >= 1:
            gross_rev = (row["Net Revenue to NI"] + operating_cost)/ni
            df.at[idx,"Net Revenue to CML"] = gross_rev*niCML_apo - operating_cost*(1-carry)
        else:
            df.at[idx,"Net Revenue to CML"] = row["Net Revenue to NI"]
    return npv(df=df,irr=irr,intial_cost=dp),df["Net Revenue to CML"].sum()

def npv(df,irr,intial_cost):
    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))
    npv = df['PV of Row'].sum() - intial_cost
    return npv

def main():
    pd.set_option('display.max_rows', None)  
    df = pd.read_csv('./prod.csv')
    ri_lease = .25
    carry = .15
    dp = 3000000
    oil_price = 70
    irr = .1
    operating_cost = 10000
    price_acre = 800
    print(lease(carry=carry,ri=ri_lease,operating_cost=10000,df=df,price_acre=400,dp=dp,oil_price=oil_price,irr=irr))
    print(carried(carry=carry,ri=ri_lease,operating_cost=10000,df=df,dp=dp,oil_price=oil_price,irr=irr))
main()