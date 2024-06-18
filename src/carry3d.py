import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection, Patch3DCollection, Path3DCollection
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import root_scalar
import carryfn

def lease(carry,operating_cost,df,price_acre,ri,dp,oil_price,irr):
    df["Net Revenue to CML"] = df["Monthly Oil Production"]*oil_price*.954*(1-ri) - operating_cost

    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))

    intial_cost = dp + carry*640*price_acre
    return npv(df=df,irr=irr,intial_cost=intial_cost)

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
    print(df)
    exit()
    return npv(df=df,irr=irr,intial_cost=dp),solver_irr(df)

def npv(df,irr,intial_cost):
    for idx, row in df.iterrows():
        df.at[idx, 'PV of Row'] = row["Net Revenue to CML"]*((1+(irr/12))**(-(idx+1)))
    npv = df['PV of Row'].sum() - intial_cost
    return npv

def solver_irr(df:pd.DataFrame):
    def npv_solver(irr,cfs:list):#cfs [[month,cf]]
        return sum([cf[1] / (1 + irr)**cf[0] for cf in cfs])
   
    cfs = df[['month', 'Net CML']]

    cfs = cfs.values.tolist()
    res = root_scalar(npv_solver,args=(cfs,),bracket=[0,1],method='brentq')
    irr = (1+res.root)**12-1#annually
    return irr

def plot(cumlOilCase,block):
    df = pd.read_csv(f'./prod{cumlOilCase}MBO.csv')#monthly oil production
    ri_lease = .25
    dc = 4350000
    oil_price = 80

    xs = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
        0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19,
        0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30])
    
    ys = np.array([   0,  100,  200,  300,  400,  500,  600,  700,  800,  900, 1000,
       1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100,
       2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000])
    
    z_carried = []
    z_lease = []

    for y in ys: 
        row_carried = []
        row_lease = []
        for x in xs: 
            cIrr,_ = carryfn.carried(df,x,0,ri_lease,dc,oil_price,y)
            lIrr,_ = carryfn.lease(df,ri_lease,0,y,dc,oil_price,None)
            row_carried.append(cIrr)
            row_lease.append(lIrr)

        z_carried.append(row_carried)
        z_lease.append(row_lease)
    Zl = np.array(z_lease)
    Zc = np.array(z_carried)

    X, Y = np.meshgrid(xs, ys)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    lease_surf = ax.plot_surface(X, Y, Zl, cmap='Purples', label='Lease',picker=True)
    carry_surf = ax.plot_surface(X, Y, Zc, cmap='Blues', label='Carry',picker=True)

    fig.colorbar(lease_surf, ax=ax, label='Lease', pad=0.1)
    fig.colorbar(carry_surf, ax=ax, label='Carry', pad=0.1)

    ax.set_xlabel('Leasor Percent')
    ax.set_ylabel('$/acre')
    ax.set_zlabel('IRR')

    ax.set_title('IRR of Project when Leasing vs Co-tenancy')

    ax.annotate(f"{cumlOilCase}MBO, 80/Bbl, 20 LOE, 4.35M D&C, 100 acre lease",
                xy=(0.05, 0.95), xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"),
                fontsize=10, ha="left")
    plt.show(block=block)

def plotPlotly(cumlOilCase):
    df = pd.read_csv(f'./prod{cumlOilCase}MBO.csv')#monthly oil production
    ri_lease = .25
    dc = 4350000
    oil_price = 80

    xs = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
        0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19,
        0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30])
    
    ys = np.array([   0,  100,  200,  300,  400,  500,  600,  700,  800,  900, 1000,
       1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100,
       2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000])
    
    z_carried = []
    z_lease = []

    for y in ys: 
        row_carried = []
        row_lease = []
        for x in xs: 
            cIrr,_ = carryfn.carried(df,x,0,ri_lease,dc,oil_price,y)
            lIrr,_ = carryfn.lease(df,ri_lease,0,y,dc,oil_price,None)
            row_carried.append(cIrr)
            row_lease.append(lIrr)

        z_carried.append(row_carried)
        z_lease.append(row_lease)
    Zl = np.array(z_lease)
    Zc = np.array(z_carried)

    X, Y = np.meshgrid(xs, ys)

    lease_surf = go.Surface(x=X, y=Y, z=Zl, colorscale='Purples', name='Lease',showlegend=True,colorbar=dict(title="Lease",x=1.0,y=0.35))
    carry_surf = go.Surface(x=X, y=Y, z=Zc, colorscale='Greens', name='Carry',showlegend=True,colorbar=dict(title="Carry",x=1.1,y=0.35))

    fig = go.Figure(data=[lease_surf, carry_surf])


    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Leasor Percent'),
            yaxis=dict(title='$/acre'),
            zaxis=dict(title='IRR (%)'),
            camera=dict(eye=dict(x=1.3, y=1.3, z=0.7))
            ),
        title='IRR of Project when Leasing vs Co-tenancy',
    )
    fig.add_annotation(
        text=f"{cumlOilCase}MBO, 80/Bbl, 20 LOE, 4.35M D&C, 100 acre lease",
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.05,
        y=0.95,
        bgcolor='rgba(255, 255, 255, 0.7)',
        bordercolor='rgba(0, 0, 0, 0.7)',
        borderwidth=2,
    )

    fig.show()

def main():
    pd.set_option('display.max_rows', None)  
    block = False
    
    for case in ['150','200','250','300']:
        if case == '300':block=True
        plotPlotly(case)
        #plot(case,block)


if __name__ == "__main__": main()