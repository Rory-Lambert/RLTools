#%%
#import the file

from RLtools.DataProcessing.stylusprofiler.surfaceprofile import SurfaceProfile, blank_dektak_figure, dektak_template
import os 

# %%
path_to_example_trace = './RLtools/DataProcessing/stylusprofiler/example_long_scan.txt'
example_trace = SurfaceProfile(path_to_example_trace, name='Example Trace')
example_trace.plot()
# %%
#shifting a trace during initialisation
same_trace_shifted = SurfaceProfile(path_to_example_trace, x_offset=2000,
                                         y_offset=10, name='Shifted Trace')
same_trace_shifted.plot()
#%%
#shifting after the object is initialised
same_trace_shifted.align(0, -15)
same_trace_shifted.plot()


# %%
# how to plot many traces
f = blank_dektak_figure()
for trace in [example_trace, same_trace_shifted]:
    f.add_scatter(x=trace.x, y=trace.y, name=trace.name)#, fill='tozeroy')
f
# %%
# Do a derivative
example_trace.compute_derivative(5,1, makefig=True)

# %%
# access the derivative data;
example_trace.data
# %%
#see other stuff about the data;
vars(example_trace)
# %%
# join traces into a single dataframe then plot 
# all at once with plotly express

import pandas as pd
import plotly.express as px
df=pd.concat([example_trace.data, same_trace_shifted.data])

px.line(df, 'Scan Length (um)','Profile (um)',color='Name')


# %%
#CURSOR MEASURE - long dataframe method

#group by the trace
for n,group in df.groupby('Name'):
    #filter the xregion of interest
    mask = group['Scan Length (um)'].between(3131,3133)
    #report the mean y in this region
    print(f'{n} Average: {group[mask]["Profile (um)"].mean():.2f}um')
# %%

#CURSOR MEASURE - BUILT IN



#%%
#Make it look like the dektak
f=example_trace.plot()
f=dektak_template(f)
f
# %%
path = r'C:\Users\roryl\CST Global Ltd\Integration - Documents\MLA2\AZ45xx Process Development\Wafer Data\Wafer H\Dektak\Post Dev Pre Reflow\h2b 44 long circ.txt'
flat=SurfaceProfile(path)
f2=flat.plot()
f2=dektak_template(f2)
f2
# %%
