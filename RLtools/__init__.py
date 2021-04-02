#%%
import os
from sys import platform
import sys


sys.path.append(os.path.dirname(os.path.realpath(__file__)))

if platform == "linux" or platform == "linux2":
    sharepoint = os.path.join("/Volumes", "CST Global Ltd")
    

elif platform == "win32":
    sharepoint = os.path.join(os.path.expanduser('~'), 'CST Global Ltd')


integration_drive = os.path.join(sharepoint, 'Integration - Documents')
# %%
