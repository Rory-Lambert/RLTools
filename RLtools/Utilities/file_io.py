from pathlib import Path
import os 

def get_fname(f):
    """
    Gets a filename, without extension, from the full path
    """
    return str(f).split('\\')[-1].split('.')[0]



def read_files_to_dict(path, ftype, func=None,**fkwargs):
    """
    Given a path to a folder and a str for globbing (usually '*.filetype'), look in the folder for files matching the criteria
    Optionally provide a function which can be applied to the files opened. 
    If func, returns {filename: func(filename, **fkwargs)}
    If not func, returns {filename: full file path}
    """
    outfiles = {}
    


    for f in Path(path).rglob(ftype):

        if not func:
            outfiles[get_fname(f)] = f
        if func:
            try:
                outfiles[get_fname(f)] = func(f, name = get_fname(f))
            except TypeError:
                outfiles[get_fname(f)] = func(f, **fkwargs)

    return outfiles