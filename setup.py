from distutils.core import setup

setup(
    name='RLTools',
    version='0.1.0', 
    packages=['RLTools','RLTools.database','RLTools.data_processing'],
    #install_requires=['pandas', 'plotly'],
    description='A collection of useful code by Rory Lambert',
    license='',
    author='Rory Lambert',
    author_email='rory.lambert@hotmail.co.uk',
    long_description=open('README.md').read()
)
