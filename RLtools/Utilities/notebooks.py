# To enable notebooks to exported with interactive plotly graphs
from plotly.offline import init_notebook_mode
init_notebook_mode()

# Enter this from Anaconda prompt to convert your ipynb file to html without showing any of the code. 
# This is not python code(!)
jupyter nbconvert YourNotebook.ipynb --no-input --to html