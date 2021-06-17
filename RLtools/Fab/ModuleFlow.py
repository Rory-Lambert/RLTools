#%%
import pandas as pd

class ProcessStep(object):
    """Generic class describing a process step
       Maybe this can also be used for those steps which dont require 
       a piece of eqiupment, or anything fancy """
    def __init__(self, id, process_type='Undefined Process', recipe=None):
        super(ProcessStep, self).__init__()
        self.id = id
        self.process_type = process_type
        self.recipe = recipe
        
    def __repr__(self):
        return f'{self.process_type} Step instance with ID "{self.id}"'

    def breakdown(self):
        return pd.Series(self.__dict__)

class Dielectric(ProcessStep):
    """For deposition of thin film dielectrics"""
    def __init__(self, ID, equip, recipe):
        super(Dielectric, self).__init__(ID, recipe=recipe)
        self.process_type = 'Dielectric Deposition'
        eqiupment_list = ['PECVD1','PECVD2']

        if equip not in eqiupment_list:
            print(f'{equip} not valid. Please enter one of {eqiupment_list}')
        self.equip = equip

class OxideDep(Dielectric):
    """For deposition of SiO2 specifically. Lets imagine this process
        only occurs on equipment PECVD1 """
    def __init__(self, ID, thickness):
        
        super(OxideDep, self).__init__(ID, 'PECVD1',f'{thickness}nmSiO')
        


#%%
class Spin(object):
    """Resist spin"""
    
   
    def __init__(self, name, resist, program, baketime, baketemp):
        super(Spin, self).__init__()
        
        available_resists = ['LOR20B','LOR7B','S1805','S1813','S1818','SPR220']
        self.name = name 
       
        if resist not in available_resists:
            raise ValueError(f'Please choose one of {available_resists}')
        self.resist = resist

        self.program = program
        self.baketime = baketime
        self.baketemp = baketemp

    def __repr__(self):
        return f'Spin {self.resist} using program {self.program}, bake for {self.baketime}s at {self.baketemp}C'

p5LOR7 = Spin('LOR7: Program 5', 'LOR7B', 5,60,160)
p7S1818 = Spin('S1818: Program 7', 'S1818', 7, 60, 115)
#%%
        


class Photo(ProcessStep):
    """Represents a photolithgraphy step"""
    def __init__(self, ID, ox, res, prog, exp, peb=None, dev=5, maskid='Unkown Mask'):
        
        photodict = dict(resist=res,
                         exposure=exp,
                         spinner_program=prog

                        )
        
        super(Photo, self).__init__(ID)
        self.process_type = 'Photolithography'
        self.ox = ox
        self.res = res
        self.prog = prog
        self.exp = exp
        self.peb = peb
        self.dev = dev
        self.maskid = maskid


class DryEtch(ProcessStep):
    """Represents a plasma etch process"""
    def __init__(self, ID, equip, recipe):
        super(DryEtch, self).__init__(ID)
        self.equip = equip
        self.recipe = recipe 
        self.process_type = 'Dry Etch'

class ResistStrip(ProcessStep):
    """Represents a resist removal process"""
    def __init__(self, arg):
        super(ResistStrip, self).__init__()
        self.arg = arg


        

class Module(object):
    """Represents a collection of process steps """
    def __init__(self, name, *ps):
        super(Module, self).__init__()
        self.name = name
        self.processes = ps

    def __repr__(self):
        return f'Module "{self.name}" with {len(self.processes)} Process Steps'

    def overview(self):
        for n, process in enumerate(self.processes):
            print(f'Step {n}: {process.process_type}')

    def detailed_overview(self):
        df = pd.concat([pd.Series(process.breakdown()) for process in self.processes], axis=1)
        df = df.T
        df['Module'] = self.name
        #put the important columns first, leave all the rest how they are
        #https://stackoverflow.com/q/41968732/7611883
        first_cols = ['Module','id']
        new_index, _ = df.columns.reindex(first_cols + list(df.columns.drop(first_cols)))
        df[new_index]
        return df

    def append(self, operation):
        self.processes += (operation,)
            

# %%

# %%
