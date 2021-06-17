from flask import Flask, redirect, url_for, render_template, request
import pandas as pd
app = Flask(__name__)



mycontent = 'This is the homepage for Sivers Photonics web apps - under development!'

wafer_dia = [3, 4]
device_type = ['DFB', 'FP']
fiducials = ['Fiducials True','	Fiducials False']
coplanar = True
passivation = 'sio2'
metallisation = 'pmetal1'
ef = False
owc = ['ar','hr']
#%%
#from RLtools import integration_drive
from pathlib import Path
import os

sharepoint = os.path.join(os.path.expanduser('~'), 'CST Global Ltd')


integration_drive = os.path.join(sharepoint, 'Integration - Documents')
fpath=Path(integration_drive, 'Platform', 'module flow factors.xlsx')

def find_viable_modules(fpath, col_select):
    
    df=pd.read_excel(fpath, sheet_name='Truth Table', index_col='Modules', usecols = ['Modules'] + col_select)
    for col in col_select:
        df=df[col_select].drop(df[df[col]==0].index)
    df=df.dropna(how='all', axis=0)
    return df


#%%
class Input(object):
    """Input options for module selection"""
    def __init__(self, name, choices):
        super(Input, self).__init__()
        self.name = name
        self.choices = choices


        
fid = Input('Fiducial Requirement', choices={'Fiducials required':'Fiducials True','Fiducials not required':'Fiducials False'})
wafer_dia = Input('Wafer_Diameter', choices={'3 inch':'3 inch','4 inch':'4 inch'})
device_type = Input('Device Type' , choices ={'Distributed Feedback':'DFB','Fabry-Perot':'FP'})
coplanar = Input('Coplanar Device?' , choices ={'Coplanar device':'Coplanar True','Not a coplanar device':'Coplanar False'})
passivation = Input('Passivation Material', choices={'Silicon Dioxide':'SiO Passivation','Silicon Nitride':'SiN Passivation'})


testpair = [device_type, fid, wafer_dia, coplanar, passivation]


#%%

@app.route("/")
def homepage():
    return render_template("index.html", content=mycontent)


about_text = 'This website is created by Rory Lambert for Sivers Photonics. Built using Python/Flask'
@app.route("/about/")
def about():
    return render_template("index.html", content=about_text)

@app.route("/mfg/", methods=['GET','POST'])
def login():
    df=pd.read_excel(fpath, sheet_name='Truth Table', index_col='Modules')
    if request.method=='POST':
        
        #get the form responses
        responses = []
        for name,response in request.form.items():
            responses.append(response)
        
        #use them to query the dataframe
        df = find_viable_modules(fpath, responses)
        _ = [print(module) for module in df.index]



        last_selection = {}
        for param in testpair:
            last_selection[param.name] = request.form.get(param.name)
            
        #    print({param.name:request.form.getlist(param.name)})
        print(last_selection)



        #return redirect(url_for('page2', name=user))
        return render_template('select.html', subresult = df.index.values, inputs=testpair, last_selection=last_selection )
    else:
        return render_template('select.html', subresult = [], inputs=testpair, last_selection = {})




if __name__ == "__main__":
    app.run(debug=True)
    #from waitress import serve
    #serve(app, host='0.0.0.0', port=5000)