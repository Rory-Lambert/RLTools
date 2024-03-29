#%%
#from BroadexToolbox.MathsAndStatistics.Geometry import Coord, PointCloud
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import os 
from RLtools.Math.FilteringAndDerviation import savitzky_golay
from plotly.subplots import make_subplots
from RLtools.Utilities.plotlyfuncs import make_transparent, draw_axes
from RLtools.Utilities.file_io import read_files_to_dict
import warnings

sharepoint = os.path.join(os.path.expanduser('~'), 'CST Global Ltd')
integration_drive = os.path.join(sharepoint, 'Integration - Documents')
results_folder = os.path.join(integration_drive ,r'MLA2\HBr trials\UoG Trials 1\Resist3')

#%%
class SurfaceProfile(object):
    """Object representing a dektak trace. Grabs the meta data as attributes,
    and processes the scan data."""
    def __init__(self, path=None, name='Untitled trace', x_offset=0, y_offset=0):
        super(SurfaceProfile, self).__init__()
        
        self.name = name

        if path:
            try:
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
                
            
                #get the tracedata
                df=pd.read_csv(path, encoding='cp1252', skiprows=39)
                
                #create an x axis and scale the y axis
                try:
                    self.y=(df.index.values/1e4) 
                    self.x=np.array([n*self.x_resolution for n, v in enumerate(self.y)])
                except TypeError:
                    raise TypeError(f'There is a problem processing file {path}, are you sure there arent two scans in this file?')
            
            # If the normal read method fails, have a go at reading it as though its a Dektak XT file
            except:
                print('Failed normal read. Trying dektakt XT import')
                df=pd.read_csv(path, skiprows=22)
                
                df.columns = ['x','y','foo','bar']
                self.y = df['y']
                self.x = df['x']*1e3

            self.align(x_offset, y_offset)
    
    def __repr__(self):
        return f'SurfaceProfile "{self.name}" with length {self.Sclen}um'
    
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
        """Convenience function to generate and show a plot with only this trace"""
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
        """Compute the derivative of this trace, and add to the 'data' attribute

        Args:
            smoothing (int): The number of samples used in the smoothing window, must be odd.
            derivorder (int): The order of the desired derivative
            makefig (bool, optional): Flag indicating whether or not you want to generate a figure. Defaults to False.

        Returns:
            [None, or go.Figure]: [description]
        """        
        prof = 'Profile (um)'
        sclen = 'Scan Length (um)'
        self.data['deriv'] = savitzky_golay(self.data[prof].values, smoothing, 2, derivorder)
        if makefig:
            figx=blank_dektak_figure()
            figx.add_scatter(x=self.data[sclen], y=self.data[prof],name='Measured Height')
            figx.add_scatter(x=self.data[sclen], y=self.data['deriv'], secondary_y=True, name=f' Order {derivorder} Derivative')
            
            return figx

#%%
###########################################################################

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
    
    warnings.warn(
        "align_pre_post_deriv is deprecated, the functionality should be entirely reproduced in generate_report()",
        DeprecationWarning
    )
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
    """
# %%
def generate_report(dir, query, ref=0, alignments=np.zeros((100,2)), 
                    axis_range = [0,10000], title=None, derivative_index=None, etch_depth=None):
    """Searches though a directory to find dektak traces and loads them into a dict
       The traces are aligned using an (nx2) alignments array, which can be defined by the user
       The height of each trace is measured at the reference position, and used to generate the report

    Args:
        dir (str, Path-like): The parent directory in which to begin the file search
        query (str (regex?): The query defining the criterea for file selection
        ref (int, optional): Reference location along the scan (x). Defaults to 0. This defines where heights are measured
        alignments ([np.array], optional): The alignments to be used to offset the files in [x,y].
                                           There should be at least one row per file. Defaults to np.zeros((100,2)).
        axis_range ([float, float], optional): The x range over which to plot the output. Defaults to [0,10000].
        title (str, optional): Title of the dataset. Used for plotting. Defaults to None.
        derivative_index (int, optional): The index of the trace within a go.Figure object for which the derivative should be calculated. 
        etch_depth (float, optional): The etch depth in um used to highlight the surface of the substrate using show_substrate()


    Returns:
        files ({filename(str):trace(SurfaceProfile)}): dict of the files used
        f (plotly.Figure): graph of the traces
        peaks(pd.DataFrame): measured heights for each of the traces
    """                    
    files = read_files_to_dict(dir, query, SurfaceProfile) 

    f=blank_dektak_figure()


    m_bounds = [ref-2, ref+2]   #averaging region for peak height measurement


    #align the scans and plot
    for d, alignment in zip(files.items(), alignments):
        name, scan = d
        scan.align(*alignment)
        f.add_scatter(x=scan.x, y=scan.y, name=name.lower())
        
        #calulate the average height of this scan in the region defined by m_bounds
        scan.peak = scan.get_area_average(m_bounds)
        #draw m_bounds
        f.add_vrect(*m_bounds, fillcolor='green',opacity=0.1, line_width=0)
    

    #optionally plot the derivative of one of the curves
    if derivative_index:
        trace = f.data[derivative_index]

        deriv = savitzky_golay(trace['y'], window_size=5, order=2, deriv=1)
        f.add_scatter(x=trace['x'], y=deriv, secondary_y=True, name='1st derivative')

    #optionally plot the surface
    if etch_depth:
        f=show_substrate(f, etch_depth)

    #figure formatting
    f.update_xaxes(range=axis_range)
    f = make_transparent(f)
    f = draw_axes(f)
    f.update_layout(title=title)

    #package up the measured heights into a Series
    peaks = {key: value.peak for key, value in files.items()}
    peaks=pd.Series(peaks)
    return files, f, peaks


def report_etch_characteristics(report, reflow_ix, etch_ix, strip_ix,
                                runtime, name='Untitled Summary',verbose = True):
    
    
    pre_max_in_window = report[etch_ix]
    etch_depth = report[strip_ix]
    remaining_resist = pre_max_in_window - etch_depth
    initial_resist = report[reflow_ix] - report[strip_ix]
    erosion = (initial_resist - remaining_resist)
    erosion_rate = (erosion*1000)/runtime   #'um/min'
    etch_rate = (etch_depth*1000)/runtime   #'um/min'
    sel = etch_rate/erosion_rate
    if verbose:
        print(f'Total depth after etching is {pre_max_in_window:.3f} um')
        print(f'Intial resist measured as {initial_resist:.2f} um')
        print(f'Calculated remaining resist as {remaining_resist:.2f}um, indicating an erosion of {erosion:.2f}um in {runtime} minutes of etching')
        print(f'This equates to an erosion rate of {erosion_rate:.0f} nm/min')
        print(f'The etch depth of {etch_depth:.2f}um in {runtime} mins indicates an etch rate of {etch_rate:.0f}nm/min')
        print(f'The selectivity is therefore {sel:.2f}:1')

    rkeys = ['Initial resist (um)',
            'Total depth after etch (um)',
            'Remaining resist (um)',	
            'Semiconductor etched(um)',	
            'Etch rate (nm/min)',	
            'Erosion rate (nm/min)',
            'Selectivity']

    rvals =[initial_resist, pre_max_in_window, remaining_resist, etch_depth, etch_rate, erosion_rate, sel]

    df = pd.DataFrame(pd.Series({key:val for key, val in zip(rkeys, rvals)}, name=name))

    return df.T


def radius_of_curvature(f, smoothing=5):
    #https://www.desmos.com/calculator/xmfkeatiu6
    f1 = savitzky_golay(f,smoothing,2,deriv = 1)
    f2 = savitzky_golay(f,smoothing,2, deriv = 2)
    
    
    #num = (1+ (f1**2))**(3./2.)
    

    num = np.power((1 + np.power(f1, 2)), 1.5)
    denom = np.abs(f2)

    return  num/denom

def dektak_template(f):
    f.update_layout(template='plotly_dark', width=900, showlegend=False)
    f.update_traces(line=dict(color='white'))
    return f

#%%
if __name__ == "__main__":

    
    path=Path(integration_drive, 'MLA2','WP1 - External HBr Trials','UoG trials 1','Resist3', 'Pre Strip','12.txt')
    f=SurfaceProfile(path, 'Example trace - pre - strip')
    f.plot()
# %%
    #calculate the radius of curvature for every entry in the array
    roc = radius_of_curvature(f.y)
    #remove infinites
    roc = roc[np.isfinite(roc)]
    #find the maximum non NaN value
    minroc = np.nanmin(roc)
    #this is the index of the minimum value
    arg_min_roc = roc[np.argmin(roc)]

    #plot a circle whose centre is (x[argmin_roc)], f.y - minroc), and whose radius is minroc


# %%
