def annunity(pmt,n,i):
    return (1 - (1+i)**(-n))*(pmt/i)

def pv(fv,n,i):
    return fv*((1+i)**(-n))

#risk = PV_costs / PV_BPO + PV_APO ; for NPV = 0
def lease(cost_per_acre,acres,land_over_tot,years_to_payout,APO_prof_per_year,years_APO,NI_curr):
    irr = .1
    drill_cost = 3000000
    PV_costs = drill_cost + cost_per_acre*acres
    NI_curr -= land_over_tot*.25

    #risk for NPV = 0
    prof_BPO_per_year = drill_cost/years_to_payout

    pv_BPO = NI_curr*annunity(prof_BPO_per_year,years_to_payout,irr)

    vAPO_at_payout = NI_curr*annunity(APO_prof_per_year,years_APO,irr)
    pv_APO = pv(vAPO_at_payout,years_to_payout,irr)

    risk = PV_costs/(pv_APO + pv_BPO)

    return risk
#risk = PV_costs / PV_BPO + PV_APO ; for NPV = 0
def carry(land_over_tot,years_to_payout,APO_prof_per_year,years_APO,NI_curr):
    irr = .1
    drill_cost = 3000000
    PV_costs = drill_cost

    nI_BPO = NI_curr
    ni_APO = NI_curr - land_over_tot

    prof_BPO_per_year = drill_cost/years_to_payout

    pv_BPO = nI_BPO*annunity(prof_BPO_per_year,years_to_payout,irr)

    vAPO_at_payout = ni_APO*annunity(APO_prof_per_year,years_APO,irr)
    pv_APO = pv(vAPO_at_payout,years_to_payout,irr)

    risk = PV_costs/(pv_APO + pv_BPO)

    return risk



def main():
    cost_per_acre = 800
    acres = 140
    land_over_tot = .07

    risk_lease = lease(cost_per_acre,acres,land_over_tot,years_to_payout=2,APO_prof_per_year=350000,years_APO=10,NI_curr=0.78)

    risk_carry = carry(land_over_tot,years_to_payout=2,APO_prof_per_year=100000,years_APO=10,NI_curr=.78)

    #risk of assumptions: which are years to payout, and annunity made after payout for n years
    print("risk_lease: ",risk_lease)
    print("risk_carry: ",risk_carry)


main()