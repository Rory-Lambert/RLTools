#%%
#from BroadexToolbox.MathsAndStatistics.Geometry import Coord, PointCloud
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

#%%
class SurfaceProfile(object):
    """Object representing a dektak trace. Grabs the meta data as attributes,
    and processes the scan data."""
    def __init__(self, path, name='Untitled trace', x_offset=0, y_offset=0):
        super(SurfaceProfile, self).__init__()
        
        #get the metadata
        df=pd.read_csv(path, encoding='cp1252', nrows=13)
        df.columns=['Parameter','Value']
        df=df.set_index('Parameter')
        for row, value in df.iterrows(): 
            #print(row, value)
            try:
                setattr(self, row, float(value.values[0]))
            except ValueError:
                setattr(self, row, value.values[0])

        self.x_resolution = self.Sclen/self.NumPts
        self.name = name
    
        #get the tracedata
        df=pd.read_csv(path, encoding='cp1252', skiprows=39)
        self.y=(df.index.values/1e4) + y_offset
        self.x=np.array([n*self.x_resolution for n, v in enumerate(self.y)])
        self.x = self.x + x_offset

    def plot(self):
        df=pd.DataFrame(np.column_stack([self.x, self.y]), columns=['Scan Length (um)', 'Profile (um)'])
        df['Name'] = self.name
        f=px.line(df,'Scan Length (um)', 'Profile (um)', color='Name' )
        return f

def add_profile_and_align(f, profile, xoff=0, yoff=0):
    f.add_trace(go.Scatter(x=profile.x + xoff, y=profile.y + yoff, name=profile.name))
    return f



if __name__ == "__main__":
    
    path=r'C:\Users\roryl\Programming Offline\BranchTesting\dektakexample.txt'
    path2=r'C:\Users\roryl\Programming Offline\BranchTesting\dektak2.txt'
    ex=SurfaceProfile(path, 'test trace' ,0,0)
    dt2=SurfaceProfile(path2, 'Trace DT2' ,0,0)

    #%%
    #plot the first curve
    fex=ex.plot()
    #add another trace and (optionally) offset it's position
    add_profile_and_align(fex, dt2, 0,0)


# %%
