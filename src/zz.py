import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

def lease(carry,operating_cost,df,price_acre,ri,dp,oil_price,irr):
    df["Net Revenue to CML"] = df["Monthly Oil Production"]*oil_price*.954*(1-ri) - operating_cost

    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))

    intial_cost = dp + carry*640*price_acre
    return npv(df=df,irr=irr,intial_cost=intial_cost),1

def carried(df,carry,operating_cost,ri,dp,oil_price,irr,loe_percent):
    ri -= carry*.25 #if carried they do not get royalty
    ni = 1 - ri
    niCML_apo = 1 - ri - carry
    df["Gross AT"] = df["Monthly Oil Production"]*oil_price*.954*(ni)
    df["LOE"] = df["Gross AT"]*loe_percent
    df["Net CML"] = df["Gross AT"]*ni - df["LOE"]
    
    payout_info = {"found":False}
    curr_netRev = 0
    for idx, row in df.iterrows():
        curr_netRev += row["Net CML"]
        if curr_netRev/dp >= 1 and payout_info["found"] is False:
            payout_info["found"] = True
            payout_info["idx"] = idx
            payout_info["needed"] = dp - (curr_netRev - row["Net CML"])
        df.at[idx, 'Payout'] = curr_netRev/dp
    
    for idx,row in df.iterrows():
        if idx == payout_info["idx"]:#apply bpo and apo rules to respective amts
            bpo_amt = payout_info["needed"]
            apo_amt = row["Net CML"] - bpo_amt
            
            rev_CMl = bpo_amt
            rev_CMl += ((apo_amt + df["LOE"])/ni)*niCML_apo - row[""]
            df.at[idx,"Net Revenue to CML"] = rev_CMl
            continue
        if row["Payout"] >= 1:
            gross_rev = (row["Net CML"] + operating_cost)/ni
            df.at[idx,"Net Revenue to CML"] = gross_rev*niCML_apo - operating_cost*(1-carry)
        else:
            df.at[idx,"Net Revenue to CML"] = row["Net CML"]
    print(df)
    exit()
    return npv(df=df,irr=irr,intial_cost=dp)

def npv(df,irr,intial_cost):
    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))
    npv = df['PV of Row'].sum() - intial_cost
    return npv

def main():
    pd.set_option('display.max_rows', None)  
    df = pd.read_csv('./prod250MBO.csv')
    ri_lease = .25
    carry = .07
    dp = 4350000
    oc = 10000
    oil_price = 80
    irr = .1
    loe = .2#as percent of gross rev AT
    price_acre = 800
    
    
    carries = [i/1000 for i in range(0,401)]
    npv_carry = [carried(df,c,oc,ri_lease,dp,oil_price,irr) for c in carries]


    # Plot the second set of values
    plt.plot(carries, npv_carry, label='NPV Carry')
    plt.grid(True)
    # Add labels and title
    plt.xlabel('Carry')
    plt.ylabel('NPV [$ Millions]')
    plt.title('')

    plt.legend()
    plt.show()
    
main()