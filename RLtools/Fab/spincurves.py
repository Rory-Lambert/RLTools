#%%
import numpy as np
from numpy.polynomial.polynomial import Polynomial as Poly
#https://repository.upenn.edu/cgi/viewcontent.cgi?article=1000&context=scn_tooldata
s1805 = [[500 , 1.287],
        [1000, 0.914],
        [1500, 0.742],
        [2000, 0.644],
        [2500, 0.569],
        [3000, 0.524],
        [3500, 0.490],
        [4000, 0.459],
        [4500, 0.438],
        [5000, 0.420],
        [5500, 0.409],
        [6000, 0.399]]

s1805=pd.DataFrame(s1805, columns = ['Speed','Thickness'])
from scipy.optimize import curve_fit
# %%
def spin_asymptote(x,a,b,c,d): 
    return (a/(((x*c)+b)**2))

# %%
s1805_fit=Poly.fit(s1805['Speed'], s1805['Thickness'],2)
import plotly.graph_objects as go
import plotly.express as px

x=np.linspace(500,6000)
y=s1805_fit(x)
f=px.scatter(s1805, 'Speed','Thickness')
f.add_trace(go.Scatter(x=x, y=y))
f
# %%
popt, pcov = curve_fit(spin_asymptote, s1805['Speed'], s1805['Thickness'])
# %%
f.add_trace(go.Scatter(x=x, y=spin_asymptote(x, *popt)))
# %%
