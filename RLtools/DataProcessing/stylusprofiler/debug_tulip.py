#%%
import pandas as pd
from scipy.signal import find_peaks, peak_widths
from numpy.polynomial.polynomial import Polynomial as Poly
from RLtools.DataProcessing.stylusprofiler.surfaceprofile import SurfaceProfile
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import os
from RLtools.Math.FilteringAndDerviation import savitzky_golay
from plotly.subplots import make_subplots




class CircleStructure(pd.DataFrame):
    
    """docstring for CircleStructure."""
    def __init__(self, name, data):
        super(CircleStructure, self).__init__(data)
        self.name = name
        self.split1 = None 
        self.split2 = None
        self.peaks = None
        self.fit = None
        self.fit_max = None
    
    
    def add_trace(self, f, **kwargs): 
        return f.add_traces(go.Scatter(x=self[sclen],
                                       y=self[prof],
                                       name = self.name, 
                                       **kwargs))
 
    def add_child_traces(self,f, **kwargs):
        if isinstance(self.split1, CircleStructure):
            
            self.split1.add_trace(f, **kwargs)
            self.split1.add_child_traces(f, **kwargs)
        
        if isinstance(self.split2, CircleStructure):
            self.split2.add_trace(f, **kwargs)
            self.split2.add_child_traces(f, **kwargs)

    def split(self, name1, name2, split_function=None, **split_kwargs): 
        #split this data based upon an arbitrary split function
        #children are instances of this same class
        
        split1, split2 = split_function(self, **split_kwargs)
        self.split1 = CircleStructure(name1, split1)
        self.split2 = CircleStructure(name2, split2)

    def df_find_peaks(self, h=0.5, d=150, width=10, f=None, x_resolution=1, verbose=False):
        
        ind, ph = find_peaks(self[prof].values, height = h, distance=d, width=width)
        if verbose:
            print(f'Found {len(ind)} peaks')

        keys = ['widths', 'heights','L','R']
        values = peak_widths(self[prof], ind, rel_height=0.99)
        
        #self.peaks = dict(indices = ind, heights = ph)
        self.peaks= self.iloc[ind].copy(deep=True)


        for key, value in zip(keys,values):
            self.peaks[key] = value 
        
        #TODO - GET THE X RESOLUTION PROPERLY
        self.peaks['widths'] *= x_resolution

        

        if f:
            f.add_trace(go.Scatter(x=self.peaks[sclen], 
                                   y=self.peaks[prof], 
                                    mode='markers', 
                                    marker_symbol='x',
                                    name =self.name + ' peak detection'))
            
            #plot the widths
            """

            for ix,row in self.peaks.iterrows():
                
                rescale_x = [(x_resolution*row[key]) + self[sclen].min() for key in ['L','R']]
                f.add_trace(go.Scatter(x=rescale_x, y=[row['heights']]*2))
            """

            return f

    def highest_peak(self):
        return self.peaks.query(f'`Profile (um)` == `Profile (um)`.max()')

    def fit_peaks(self,f, verbose = False):
        
        self.fit=Poly.fit(self.peaks[sclen],
                     self.peaks[prof],
                     2)
        
        if verbose:
            print(f'Fitted 2nd order to measured peaks:\n {self.fit}')

        x=np.arange(0,10000)
        y=self.fit(x)
        yargmax =  y.argmax()
        self.fit_max = [x[yargmax], y[yargmax]]

        if f:
 
            mask = y>0
            f.add_trace(go.Scatter(x=x[mask], y=y[mask], name='Polynomial Fit'))
            return f
    
    def compute_derivative(self, smoothing, derivorder, makefig=False):
        self['deriv'] = savitzky_golay(self[prof].values, smoothing, 2, derivorder)
        if makefig:
            figx = make_subplots(specs=[[{"secondary_y": True}]])

            figx.add_scatter(x=self[sclen], y=self['deriv'], secondary_y=True, name='1st derivative')
            figx.add_scatter(x=self[sclen], y=self[prof],name='Measured Height')
            return figx



def find_breaks(df, threshold = 0.1, figure = None, verbose = False):
    """
    Find the break in a circle set to allow fitting on either side
    """
    
    y=df[prof].values
 
    true_regions = []
    for start, stop in contiguous_regions(y<threshold):
        segment = y[start:stop]
        seglength = stop-start
        true_regions.append([start,stop,seglength])

    #find the longest region of y<threshold
    longest_ind = np.array(true_regions)[:,2].argmax()
    longest = true_regions[longest_ind]

    #plot the longest region
    longest_break = df.iloc[longest[0]:longest[1]]
    x=longest_break[sclen].values
    
    

    #find the centre point
    mid = int(longest[0] + np.diff(longest[0:2])/2)
    mid = df.iloc[mid]


    if verbose:
        print(f'Found a breakpoint at {mid[sclen]}')

    if figure:
        #https://plotly.com/python/horizontal-vertical-shapes/
        
        figure.add_vrect(x[0],x[-1], 
                        line_width=0, 
                        fillcolor=trace.line.color, 
                        opacity = 0.2, 
                        annotation_text='discontinuity')

                #plot this point
        figure.add_vline(mid[sclen])

    #split1
    s1 = df[df[sclen].between(0, mid[sclen])]
    s2 = df[df[sclen].between(mid[sclen], 10000)]

    return s1, s2
    
import numpy as np
#https://stackoverflow.com/a/4495197/7611883
def contiguous_regions(condition):
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero() 

    # We need to start things after the change in "condition". Therefore, 
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size] # Edit

    # Reshape the result into two columns
    idx.shape = (-1,2)
    return idx

def tulipsplit(df):
    left = df[df[sclen].between(400,6200)].copy(deep = True)
    #left['Name'] = df.name + name1

    right = df[df[sclen].between(6201, 10001)].copy(deep=True)
    #right['Name'] = df.name + name2

    return left, right

#%%

sclen = 'Scan Length (um)'
prof = 'Profile (um)'



def generate_report(surfaceprofile, makefig=False):


    #load into the surface profile object (reads dektak file and can adjust position)
    t=surfaceprofile
    f=t.plot()

    #f.update_layout(width=1200, height=800)

    j=CircleStructure(t.name, t.data)
    #Split into large and small circles
    j.split(f'{j.name}: Large Circles',f'{j.name}: Small Circles',tulipsplit)

    #split into left and right chunks based upon where the longest zero section is
    for side in [j.split1, j.split2]:
        side.split(f'{side.name}: Left of split',f'{side.name}: Right of split',find_breaks)

        for quarter in [side.split1, side.split2]:
            quarter.df_find_peaks(f=f, x_resolution = t.x_resolution)
            quarter.fit_peaks(f)
            
    
    j.add_child_traces(f, fill='tozeroy')
    
    if makefig:

        f.show()


    peaks = [foo.highest_peak() for foo in[ j.split1.split1, j.split1.split2, j.split2.split1, j.split2.split2]]
    return j, pd.concat(peaks)
    



# %%

if __name__ == "__main__":
    
    # get files
    trace= [f for f in Path(os.getcwd(),'RLTools', 'data_processing/stylusprofiler').rglob('*.txt')]
    sp = SurfaceProfile(trace[0], name = 'Trace 0  Hello')
    j, df = generate_report(sp, makefig=True)
    """from RLtools.data_processing.stylusprofiler.FilteringAndDerviation import savitzky_golay
    
    deriv=savitzky_golay(j[prof].values,11, 2, 1)


    figx = make_subplots(specs=[[{"secondary_y": True}]])

    figx.add_scatter(x=j[sclen], y=deriv, secondary_y=True, name='1st derivative')
    figx.add_scatter(x=j[sclen], y=j[prof],name='Measured Height')"""

# %%

    #fit the entire range of the parent circle structure to a given
    max_2ndorder = j.split1.split2.fit_max
    #get the x component
    xfit = max_2ndorder[0]
    
    raw_x = j.split1.split2.peaks[sclen]

    #calculate min distance to find the raw peak closest to the fitted peak
    mindist_ix = (xfit-raw_x).abs().argmin()
    
    #use this index to select the closest peak
    j.split1.split2.peaks.iloc[mindist_ix]

    #select only this peak and re-index
    px.scatter(j[j[sclen].between(4665-136, 4665+136)], sclen, prof)
# %%
