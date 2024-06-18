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
    df = pd.read_csv('./prod250MBO.csv')
    ri_lease = .25
    carry = .07
    dp = 4350000
    operating_cost = 10000
    oil_price = 70
    irr = .111
    loe = .2#as percent of gross rev AT
    price_acre = 800
    #print(lease(carry=carry,ri=ri_lease,operating_cost=10000,df=df,price_acre=800,dp=dp,oil_price=oil_price,irr=irr))
    #print(carried(carry=carry,ri=ri_lease,operating_cost=10000,df=df,dp=dp,oil_price=oil_price,irr=irr))
    
    cs = [.15,.0595,.06]
    for cc in cs:
        carried(carry=cc,ri=ri_lease,df=df,dp=dp,oil_price=oil_price,irr=irr,operating_cost=operating_cost)
    carries = [i/1000 for i in range(101)]
    npv_lease = []
    npv_l4 = []
    npv_l8 = []
    npv_l10 = []
    npv_l12 = []
    npv_l14 = []
    npv_l20 = []
    npv_carry = []
    nom_lease = []
    nom_carry = []
    for c in carries:
        c1 = carried(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,dp=dp,oil_price=oil_price,irr=irr)
        l4 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=400,dp=dp,oil_price=oil_price,irr=irr)
        l8 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=800,dp=dp,oil_price=oil_price,irr=irr)
        l10 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=1000,dp=dp,oil_price=oil_price,irr=irr)
        l12 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=1200,dp=dp,oil_price=oil_price,irr=irr)
        l14 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=1400,dp=dp,oil_price=oil_price,irr=irr)
        l20 = lease(carry=c,ri=ri_lease,operating_cost=operating_cost,df=df,price_acre=2000,dp=dp,oil_price=oil_price,irr=irr)
        npv_carry.append(c1[0])
        npv_l4.append(l4[0])
        npv_l8.append(l8[0])
        npv_l10.append(l10[0])
        npv_l12.append(l12[0])
        npv_l14.append(l14[0])
        npv_l20.append(l20[0])

        #nom_lease.append(l[1])
        #nom_carry.append(c[1])

    


    



    '''nom plot
    plt.plot(carries, nom_lease, label='Lease')

    # Plot the second set of values
    plt.plot(carries, nom_carry, label='Carry')

    # Add labels and title
    plt.xlabel('Carry')
    plt.ylabel('$ Nominal')
    plt.title('')

    plt.legend()
    plt.show()
    '''
    
    
    plt.plot(carries, npv_l4, label='NPV Lease $/acre = 400')
    plt.plot(carries, npv_l8, label='NPV Lease $/acre = 800')
    plt.plot(carries, npv_l10, label='NPV Lease $/acre = 1000')
    plt.plot(carries, npv_l12, label='NPV Lease $/acre = 1200')
    plt.plot(carries, npv_l14, label='NPV Lease $/acre = 1400')
    plt.plot(carries, npv_l20, label='NPV Lease $/acre = 2000')


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