import pandas as pd
import carryfn
df = pd.read_csv('prod250MBO.csv')
 
l = carryfn.lease(df,.25,0.2,500,4350000,80,None)
print(l)