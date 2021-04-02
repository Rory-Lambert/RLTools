#%%
import pandas as pd
import plotly.express as px

df= pd.read_excel('./wiptrac_export_columns.xls')
#default column headings have a leading whitespace, lets remove
df.columns= [key.strip() for key in df.keys()]

#get the operation name from the most common entry in the dataframe
op=df['Operation'].mode()[0]
proc=df['Process Num'].mode()[0]


f=px.scatter(df, x='Lot Num', y=['TOP RIGHT TR', 'TOP LEFT TL', 'BOTTOM RIGHT BR', 'BOTTOM LEFT BL'])
f.update_layout(

    yaxis_title=f"Critical Dimension (um) @ operation {op}",
    legend_title="Measurement Position",
    title = f'{proc}'

)
#px.histogram(df, 'AVERAGE')
# %%