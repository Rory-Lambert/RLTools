#%%
import plotly.graph_objects as go
from BroadexToolbox.OpticsAndPhotonics.thinfilms import ThinFilm, FilmStack
#%%


fig.show()
# %%
a = ThinFilm(1.4451, 0.4, name='FILM A')
b = ThinFilm(1.34521, 2,name='FILM B')
c = ThinFilm(1.34521, 3, name='FILM C')
d =ThinFilm(1.34521, 1)



# %%
from BroadexToolbox.MathsAndStatistics.Geometry import Coord, PointCloud




#%%

layers=[]
tx_pointer=0

fs = FilmStack(a,b,c)
for key,var in vars(fs).items():
    print(var)
    if type(var) == ThinFilm:
        ll=Coord(0,tx_pointer)
        lr=Coord(1,tx_pointer)

        #replace 'a' w/ ThinFilm
        ul, ur = [l + [0, var.tx] for l in [ll,lr]]

        pc=PointCloud(ll,lr,ur,ul,ll, title=var.name)
        l = go.Scatter(x=pc.x, y=pc.y, name=pc.title, fill="toself")
        layers.append(l)
        tx_pointer+=var.tx
    else:
        continue
    
# %%
f=go.Figure(layers)
f.show()
# %%
