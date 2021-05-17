#%%
from plotly.offline import init_notebook_mode
import plotly.graph_objects as go
from plotly.subplots import make_subplots
init_notebook_mode()
from PIL import Image
from RLtools.data_processing.stylusprofiler.debug_tulip import generate_report, CircleStructure
from RLtools.Utilities.file_io import get_fname, read_files_to_dict
from RLtools.data_processing.stylusprofiler.surfaceprofile import (results_folder,
        SurfaceProfile, add_profile_and_align, show_substrate, get_sample_rundata, blank_dektak_figure,
        report_etch_characteristics, align_pre_post_deriv, radius_of_curvature)

pre = (read_files_to_dict(results_folder + '/Pre Strip', '*.txt', SurfaceProfile))
post = (read_files_to_dict(results_folder + '/Post Strip', '*.txt', SurfaceProfile))
img = read_files_to_dict(results_folder + '\Post Strip\Images\Long SVC soak', '*.jpg')


#%%

mask = pre['24'].data['Scan Length (um)'].between(3750,3750+170)
crop = pre['24'].data[mask]
import plotly.express as px
f=px.scatter(crop, x='Scan Length (um)',y = 'Profile (um)')

roi = crop['Profile (um)'].values
roc = radius_of_curvature(roi, smoothing=2001)
f.add_scatter(x=crop['Scan Length (um)'].values, y=roc)

#%%
# SAMPLE 24
lhs = 3750
xxrange = [lhs, lhs+170]
yyrange = [0,12]
etch_depth = 0.52

alignments = [[0,-0.1],[-1416,0]]

f = align_pre_post_deriv(pre['24'],post['24'], alignments)

f.update_xaxes(range=xxrange)
f.layout.yaxis1['range']=yyrange
f.layout.yaxis2['range']=[-0.2,0.2]
f.layout.title = 'Sample 24: Selectivity = 0.719'
f.update_layout(width = 600, height = 600, legend = dict(xanchor='center', x= 0.5, orientation= 'h' ))
f=show_substrate(f, etch_depth)

roi = pre['24'].data['Profile (um)'].values
roc = radius_of_curvature(roi, smoothing=211)
f.add_scatter(x=pre['24'].data['Scan Length (um)'].values, y=roc)





# %%
# SAMPLE 44
lhs = 3059
xxrange = [lhs, lhs+170]
yyrange = [0,12]
etch_depth = 0.9

alignments = [[0,-0.1],[-1015,0]]

f44 = align_pre_post_deriv(pre['44'],post['44'], alignments)

f44.update_xaxes(range=xxrange)
f44.layout.yaxis1['range']=yyrange
f44.layout.yaxis2['range']=[-0.2,0.2]
f44.update_layout(width = 600, height = 600, legend = dict(xanchor='center', x= 0.5, orientation= 'h' ))
f44.layout.title = 'Sample 44: Selectivity = 1.82'
f44=show_substrate(f44, etch_depth)




# %%
# SAMPLE 14
lhs = 1860
xxrange = [lhs, lhs+170]
yyrange = [0,12]
etch_depth = 4.39

alignments = [[0,0.13],[-320,0]]

f14 = align_pre_post_deriv(pre['14'],post['14'], alignments)

f14.update_xaxes(range=xxrange)
f14.layout.yaxis1['range']=yyrange
f14.layout.yaxis2['range']=[-0.2,0.2]
f14.update_layout(width = 600, height = 600, legend = dict(xanchor='center', x= 0.5, orientation= 'h' ))
f14.layout.title = 'Sample 14: Selectivity = 3.192'
f14=show_substrate(f14, etch_depth)



  
# %%
# SAMPLE 52
lhs = 4115
xxrange = [lhs, lhs+170]
yyrange = [0,12]
etch_depth = 2.6

alignments = [[0,0.02],[878,0.07]]

f52 = align_pre_post_deriv(pre['52'],post['52'], alignments)
f52.update_xaxes(range=xxrange)
f52.layout.yaxis1['range']=yyrange
f52.layout.yaxis2['range']=[-0.2,0.2]
f52.update_layout(width = 600, height = 600, legend = dict(xanchor='center', x= 0.5, orientation= 'h' ))
f52.layout.title = 'Sample 52: Selectivity = 2.535'
f52=show_substrate(f52, etch_depth)




# %%
# %%
