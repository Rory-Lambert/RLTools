
#%%
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

if __name__ == "__main__":
    from pathlib import Path
    import plotly.express as px

    examplefiles = Path('./', 'data_processing/web_plot_digitizer/').rglob('*csv')

    #I know these example files are for 495 and 950K
    #read both into dfs, then concatenate together
    output=[]
    for f, mwt in zip(examplefiles, ['495K','950K']):
        output.append(read_wpd_outputs(f, mwt, 'Spin speed (rpm)','Film Thickness (nm)'))
    
    df = pd.concat(output,axis=0)

    #the output is in a good format for interfacing with plotly express
    f = px.scatter(df, x='Spin speed (rpm)', y='Film Thickness (nm)', color='trace', facet_col='dataset')
