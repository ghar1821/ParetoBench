# ParetoBench
A framework for benchmarking clustering algorithms, using Pareto fronts to capture tradeoffs in clustering performance as quantified through complementary use of several supervised clustering performance metrics. 

This code is related to the following manuscript, which has recently been accepted to Bioinformatics journal. DOI will be updated once manuscript is made available by the journal.

> Givanna H. Putri, Irena Koprinska, Thomas M. Ashhurst, Nicholas J.C. King, Mark N. Read. Using single-cell cytometry to illustrate the generalisable unbiased evaluation of clustering algorithms using Pareto fronts. 

## Installation
Make sure you have Python >= 3.6 installed.
Then run the setup.py: `python3 setup.py install`

This shall install ParetoBench and all its dependencies.

It is mandatory to run Pandas >= 1.1.4 version.
The time of writing this README, 1.1.4 is only available from Pip. 
Thus please install from pip by running `pip install pandas==1.1.4`


## Usage
Examples folder contains Jupyter notebook showing a step by step instruction on how to run ParetoBench.


## Scripts to reproduce result in manuscript
Folder `experiments_materials` contains all the scripts and results used to reproduce all the plots and tables in the manuscript. 
The datasets used in the experiments are too big to be uploaded here, and thus will be uploaded to FlowRepository pending publication.

## Acknowledgements

The UNSGA3 code is adopted from prior work by Mark N. Read, contained within the repository https://github.com/marknormanread/unsga3, and devloped as part of the following manuscript:

> MN Read, K Alden, J Timmis and PS Andrews. (2020). Strategies for Calibrating Models of Biology. Briefings in Bioinformatics 21(1):24–35
