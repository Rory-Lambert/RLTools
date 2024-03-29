
import pandas as pd
import numpy as np

# reads files as exported from https://apps.automeris.io/wpd/
def read_wpd_outputs(ppath, dataname, xheading, yheading):
    df=pd.read_csv(ppath)

    segments=[]
    for n in np.arange((len(df.columns)/2)):
        seg=df.iloc[1:, 0+int(n*2):2+int(n*2)]
        tracename=seg.columns[0]
        seg['trace']=tracename
        seg['dataset'] = dataname
        seg.columns=[xheading, yheading, 'trace','dataset']
        segments.append(seg)
    df = pd.concat(segments,axis=0)
    #cast to numeric, ignore errors
    df = df.apply(pd.to_numeric, errors='ignore')    
    return df