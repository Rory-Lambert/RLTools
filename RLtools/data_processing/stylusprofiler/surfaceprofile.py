#%%
#from BroadexToolbox.MathsAndStatistics.Geometry import Coord, PointCloud
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import os 
from RLtools.data_processing.stylusprofiler.FilteringAndDerviation import savitzky_golay
from plotly.subplots import make_subplots
from RLtools.Utilities.plotlyfuncs import make_transparent, draw_axes

sharepoint = os.path.join(os.path.expanduser('~'), 'CST Global Ltd')
integration_drive = os.path.join(sharepoint, 'Integration - Documents')
results_folder = os.path.join(integration_drive ,r'MLA2\HBr trials\Resist3')

#%%
class SurfaceProfile(object):
    """Object representing a dektak trace. Grabs the meta data as attributes,
    and processes the scan data."""
    def __init__(self, path=None, name='Untitled trace', x_offset=0, y_offset=0):
        super(SurfaceProfile, self).__init__()
        
        
        if path:
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
            
            try:
                self.y=(df.index.values/1e4) 
                self.x=np.array([n*self.x_resolution for n, v in enumerate(self.y)])
            except TypeError:
                raise TypeError(f'There is a problem processing file {path}, are you sure there arent two scans in this file?')

            self.align(x_offset, y_offset)


    def align(self, x_offset, y_offset):
        """Shift the x and y positions of the data

        Args:
            x_offset ([float]): 
            y_offset ([float]): 

        Returns:
            [self]: [description]
        """        
        self.x += x_offset
        self.y += y_offset
        df=pd.DataFrame(np.column_stack([self.x, self.y]), columns=['Scan Length (um)', 'Profile (um)'])
        df['Name'] = self.name
        self.data=df

        return self

    def get_area_average(self, region):
        """Get the average y value across a certain xspan

        Args:
            region (list): [lower, upper] extent of averaging region

        Returns:
            float: Average y value in this region
        """        
        df= self.data
        sclen = 'Scan Length (um)'
        avg =df[df[sclen].between(*region)].mean()
        return avg['Profile (um)']

    def cursor_measure(self, r, m):
        """Measure the difference in y between two points, r and m


        Args:
            r (list): region selected by r cursor
            m (list): region selected by measurement cursor

        Returns:
            [float]: The difference in height between the average regions R and M
        """        
        df = self.data
        r = self.get_area_average(r)
        m = self.get_area_average(m)
        return (m-r)


    def plot(self):
        
        f=px.line(self.data,'Scan Length (um)', 'Profile (um)', color='Name' )
        return f

    def crop_xdata(self,lower,upper, name = ': Cropped'):
        self.xcrop = [lower, upper]
        self.name = self.name + name
        cropped = self.data['Scan Length (um)'].between(lower, upper)
        self.data= self.data[cropped].copy(deep=True)
        self.data.reset_index(inplace=True)
        self.x = self.data['Scan Length (um)'].values
        self.y = self.data['Profile (um)'].values


    def xscale(self, val): 
        return val*self.x_resolution + self.xcrop[0]

    def compute_derivative(self, smoothing, derivorder, makefig=False):
        prof = 'Profile (um)'
        sclen = 'Scan Length (um)'
        self.data['deriv'] = savitzky_golay(self.data[prof].values, smoothing, 2, derivorder)
        if makefig:
            figx = make_subplots(specs=[[{"secondary_y": True}]])
            figx.add_scatter(x=self.data[sclen], y=self.data[prof],name='Measured Height')
            figx.add_scatter(x=self.data[sclen], y=self.data['deriv'], secondary_y=True, name='1st derivative')
            
            return figx


def add_profile_and_align(f, profile, xoff=0, yoff=0, name=None, **kwargs):
    """[summary]

    Args:
        f ([go.Figure]): figure to which the trace should be added
        profile ([SurfaceProfile]): profile to add to the figure
        xoff (int, optional): [description]. x offset in um. Defaults to 0.
        yoff (int, optional): [description]. y offset in um. Defaults to 0.
        name ([str], optional): [description]. Defaults to None.

    Returns:
        [go.Figure]: 
    """    
    thisname = name if name else profile.name
    f.add_trace(go.Scatter(x=profile.x + xoff, y=profile.y + yoff, name=thisname, **kwargs))
    return f

def get_sample_rundata(id):
    folder2 = os.path.join(integration_drive ,r'MLA2\HBr trials')
    xlfile = next(Path(folder2).rglob('Cobra*.xlsx'))
    import pandas as pd
    usecols = ['Sample# Res C', 'Process', 'carrier', 'HBr', 'Ar', 'Pressure mT',
       'RF Power', 'ICP power', 'Temp', 'Time (min)']
    df=pd.read_excel(xlfile, usecols=usecols)
    
    return df[df['Sample# Res C'] == id]


def show_substrate(f, y1):
    return f.add_hrect(-1, y1, line_width=0, fillcolor='green',opacity =0.2, name='substrate')

def blank_dektak_figure():
    
    f = make_subplots(specs=[[{"secondary_y": True}]])
    
    f.update_layout(xaxis_title = 'Scan Length (um)',
                yaxis_title = 'Profile (um)')
    f.layout.yaxis2['showgrid']=False
    f.layout.yaxis2['title'] = 'Derivative (um/um)'
    return f


def blank_spincurve():
    f=go.Figure()
    f.update_layout(xaxis_title = 'Spin Speed (rpm)',
                    yaxis_title = 'Measured Thickness (um)')
    f=make_transparent(f)   
    f=draw_axes(f)
    return f


def align_pre_post_deriv(pre,post, alignments):
    """Aligns two traces with one another

    Args:
        pre (SurfaceProfile): [description]
        post (SurfaceProfile]): [description]
        alignments (list[pre[x],pre[y]],post[x],post[y]]): [description]

    Returns:
        [go.Figure]
    """    
    smoothing=5 
    derivorder =1 
    
    f = blank_dektak_figure() 
    add_profile_and_align(f, pre, *alignments[0], name=f'{pre.name} Pre-strip')
    add_profile_and_align(f, post,*alignments[1],  name=f'{post.name} Post Strip')
    deriv = savitzky_golay(f.data[0]['y'], smoothing, 2, derivorder)
    f.add_scatter(x=f.data[0]['x'], y=deriv, secondary_y=True, name='1st derivative')
    f = make_transparent(f)
    f=draw_axes(f)
    return f


def report_etch_characteristics(pre, post, id, xxrange, etch_depth, verbose = True):
    import pandas as pd
    initial_resist = 8.741

    pre_max_in_window = pre[id].data[pre[id].data['Scan Length (um)'].between(*xxrange)]['Profile (um)'].max()
    remaining_resist = pre_max_in_window - etch_depth
    remaining_resist
    erosion = (initial_resist - remaining_resist)
    erosion_rate = (erosion*1000)/10 
    etch_rate = (etch_depth*1000)/10
    sel = etch_rate/erosion_rate
    if verbose:
        print(f'Total depth after etching is {pre_max_in_window:.3f} um')
        print(f'Calculated remaining resist as {remaining_resist:.2f}um, indicating an erosion of {erosion:.2f}um in 10 minutes of etching')
        print(f'This equates to an erosion rate of {erosion_rate:.0f} nm/min')
        print(f'The etch depth of {etch_depth:.2f}um in 10 mins indicates an etch rate of {etch_rate}nm/min')
        print(f'The selectivity is therefore {sel:.2f}:1')

    rkeys = ['Initial resist (um)',
            'Total depth after etch (um)',
            'Remaining resist (um)',	
            'Semiconductor etched(um)',	
            'Etch rate (nm/min)',	
            'Erosion rate (nm/min)',
            'Selectivity']

    rvals =[initial_resist, pre_max_in_window, remaining_resist, etch_depth, etch_rate, erosion_rate, sel]

    df = pd.DataFrame(pd.Series({key:val for key, val in zip(rkeys, rvals)}, name='Result'))

    return df


def radius_of_curvature(f, smoothing=5):
    #https://www.desmos.com/calculator/xmfkeatiu6
    f1 = savitzky_golay(f,smoothing,2,deriv = 1)
    f2 = savitzky_golay(f,smoothing,2, deriv = 2)
    
    
    #num = (1+ (f1**2))**(3./2.)
    

    num = np.power((1 + np.power(f1, 2)), 1.5)
    denom = np.abs(f2)

    return  num/denom




if __name__ == "__main__":
    
    path=r'C:\Users\roryl\Programming Offline\BranchTesting\dektakexample.txt'
    path2=r'C:\Users\roryl\Programming Offline\BranchTesting\dektak2.txt'
    ex=SurfaceProfile(path, 'test trace' ,0,0)
    dt2=SurfaceProfile(path2, 'Trace DT2' ,0,0)

    #%%
    #plot the first curve
    fex=ex.plot()
    #add another trace and (optionally) offset it's position
    add_profile_and_align(fex, dt2, 221-50,0)


    # %%
    from pathlib import Path
    import os
    from scipy.signal import find_peaks, peak_widths

    # Load the file and plot
    trace = [f for f in Path('D:/Rory').rglob('*.txt')]

    t=SurfaceProfile(trace[1], 'Second Trace')
    f=t.plot()

    #%%
    # Manually crop the trace to include only one data set. Add to the figure
    t.crop_xdata(3500, 6270)
    f.add_trace(go.Scatter(x=t.x, y = t.y, name = t.name, fill='tozeroy'))
    #%%
    # Find and plot the peaks in this region
    ind, ph = find_peaks(t.y, height = 0.5, distance=150)
    f.add_trace(go.Scatter(x=t.x[ind], 
                        y=t.y[ind], 
                        mode='markers', 
                        marker_symbol='x',
                        name = t.name + ' peak detection'))


    # %%
    # Find and plot the widths of the detected peaks
    width, heights, L, R = peak_widths(t.y, ind, rel_height=0.99)

    for l,r,h in zip(L,R,heights):
        

        xr = [t.xscale(side) for side in [l,r]]
        f.add_trace(go.Scatter(x=xr, y= [h, h], name = 'Lens widths', marker_color='black'))

    f
    # %%
    # Use the peak detection data to create a parabola
    from numpy.polynomial.polynomial import Polynomial as Poly
    foo=Poly.fit(t.x[ind], t.y[ind],2)
    xx=np.arange(0,10000)
    yy=foo(xx)
    mask = yy>0

    f.add_trace(go.Scatter(x=xx[mask], y =yy[mask]))




    print(f'Maximum height is estimated as {yy[mask].max():.2f}um')
    print(f'Lens diameter in this region is {width[ph["peak_heights"].argmax()]*t.x_resolution:.2f}um')

    # %%
    heights
    # %%
    #replot the peaks at the frequnecy of the offset
    # sort of equivalent to the other direction
    offset = 5

    xxx=np.arange(len(ind))*offset
    ff=go.Figure(go.Scatter(x=xxx, y =ph["peak_heights"]))

    # %%

        