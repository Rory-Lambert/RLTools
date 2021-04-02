#%%
import pyDOE2 as doe
import pandas as pd
import plotly.express as px
import numpy as np
#%%
def cd_from_minmax(mn, mx):
    delta = (mx-mn)/2
    centre = mx - delta
    return centre, delta

def myround(x, base=5):
    return base * round(x/base)

#%%

class Factor(object):
    """Factor of an experiments"""
    def __init__(self, centre, delta, name='Untitled Factor', unit='', precision=1, levels=None):
        super(Factor, self).__init__()
        self.centre = centre
        self.delta = delta
        self.name = name
        self.unit=unit
        self.precision=precision
        self.levels = levels
        

    def __repr__(self):
        return f'Experimental factor {self.name} with values {self.centre} +/- {self.delta}{self.unit}'

#%%
class DesignedExperiment(object):
    """Design an experiment, using an arbitrary number of Factors. 
       Wraps around the pyDOE2 central composite design generator
    """
    def __init__(self, *factors, name='Untitled Experiment'):
        super(DesignedExperiment, self).__init__()
        #[setattr(self, f'F{n}', factor) for n, factor in enumerate(factors)]
        self.f = factors
        self.data = None
        #self.build_experiment()

    def visualise(self):
        d={2:px.scatter, 3:px.scatter_3d}

        #use the number of factors to select the appropriate plot function
        vis=d[len(self.f)](self.data, *[f.name for f in self.f])
        vis.show()

class CCExperiment(DesignedExperiment):
    """Specific Central Composite experiment"""
    #https://pythonhosted.org/pyDOE/rsm.html
    def __init__(self, *factors, name='Untitled'):
        self.name = f'{name} Central Composite Experiment'
        super(CCExperiment, self).__init__(*factors, name=self.name)
        self.build_experiment()
 
    
    def build_experiment(self):
        df=pd.DataFrame(doe.ccdesign(len(self.f), (1,1), face='cci'), 
                            columns=[f.name for f in self.f])

        for f in self.f:
            df[f.name] = (df[f.name] * f.delta) + f.centre
            df[f.name] = myround(df[f.name], f.precision)
        self.data = df


#%%
class FullFactorialExperiment(DesignedExperiment):
    """Specific Full Factorial Experiment"""
    def __init__(self, *factors, name='Untitled'):
        self.name = f'{name} Full Factorial Experiment'
        super(FullFactorialExperiment, self).__init__(*factors, name=self.name)
        self.build_experiment()
 
    
    def build_experiment(self):
        
        data = doe.fullfact([f.levels for f in self.f])
        data  = pd.DataFrame(data,  columns=[f.name for f in self.f])
        for f in self.f:
            inc=(f.delta*2)/f.levels
            data[f.name] = data[f.name]*inc + f.centre - f.delta
            #**********
                #this is what you worked on last
            #*********
        
        return(data)
"""        df=pd.DataFrame(doe.ccdesign(len(self.f), (1,1), face='cci'), 
                            columns=[f.name for f in self.f])

        for f in self.f:
            df[f.name] = (df[f.name] * f.delta) + f.centre
            df[f.name] = myround(df[f.name], f.precision)
        self.data = df"""

length = Factor(*cd_from_minmax(10,30), 'L','um',levels =5)
height = Factor(*cd_from_minmax(90, 92), 'H','nm',levels =9)

FullFactorialExperiment(length,height)

#%%

if __name__ == "__main__":
    
    #some example Factors to include in your DOE
    ti_tx=Factor(*cd_from_minmax(5, 50), 'Titanium Thickness','nm',precision=5)
    

    ti_dep=Factor(*cd_from_minmax(50,400), 'Power','W')        
    pt_tx = Factor(*cd_from_minmax(40, 200), 'Platinum Thickness','nm', precision=5)
    time=Factor(100, 20,'Time', 'seconds')

    
    #make a Designed Experiment - currently only surface response, 
    #but arbitrary number of dimensions
    ex=CCExperiment(pt_tx, ti_tx, time)   
    
    #automatically selects between two or 3d. 
    #Higher dimension DOEs cant be visualised
    ex.visualise()

    #See the data by calling the .data attribute
    print(ex.data)
# %%
    
resists = Factor(*cd_from_minmax(1, 4), 'Resist type', levels=4)

temps = Factor(170,70,'Bake Temp','C',levels=8)
ff=FullFactorialExperiment(resists,temps)
vars(ff)
# %%
res = Factor(None,None, name='res type', levels=4)
res


# %%
