#%%
import pandas as pd
from sqlalchemy import create_engine
import pyodbc
from pathlib import Path

from RLtools import integration_drive
#%%

def mssql_engine(user = 'wiptrac_reader', password = 'R3ad0nly4!W1P' 
                 ,host = '10.10.100.112',db ='wiptrac'):
    engine = create_engine(f'mssql+pyodbc://{user}:{password}@{host}/{db}?driver=SQL+Server')
    return engine

#https://stackoverflow.com/a/46939748/7611883
queries_folder = Path(integration_drive, 'Platform', 'Database Interfacing')
query = open(Path(queries_folder, 'spc_by_dfr.sql'))

mssql_engine()
#%%

df = pd.read_sql(query.read(), mssql_engine())
df
# %%

# %%
q2 = ("""
    select device.lot_num, traveler.traveler_id, traveler.trav_number, travelerd.spc, travelerd.op_id

    from device
    left join traveler
    on traveler.traveler_id = device.traveler_id

    left join travelerd
    on traveler.traveler_id = travelerd.traveler_id
    where trav_number = 'DFR-7056'
    


""")
df = pd.read_sql(q2, mssql_engine())
df
# %%
