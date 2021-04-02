# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] 2021-04-02
### Added;
- Added `surfaceprofile`.py
    - Can read dektak files and plot with offsets
- Added `web_plot_digitizer`.py
    - Converts the ouput from this web service into a format that is convenient for pandas/plotly workflow
    - Includes example excel files
- Added `read_WIPtrac_excel`.py
    - Converts WIPtracs excel output into a format that is convenient for pandas/plotly workflow
- Added `experimental_design.py`
    - WIP extension of the pyDOE2 package for design of experiments
- Added `plotly_rect.py`
    - An example file showing a plot of thin films. Requires FilmStack from Broadex toolbox, which I havent worked out how to incorporate.

