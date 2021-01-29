# ParetoBench
A framework for benchmarking clustering algorithms, using Pareto fronts to capture tradeoffs in clustering performance as quantified through complementary use of several supervised clustering performance metrics. 

This repository is related to the following manuscript, which has been accepted to Bioinformatics journal. If you use ParetoBench in your work, please kindly cite our publication:

> Putri, G. H., Koprinska, I., Ashhurst, T. M., King, N. J. C., & Read, M. N. (2021). Using single-cell cytometry to illustrate integrated multi-perspective evaluation of clustering algorithms using Pareto fronts. Bioinformatics. https://doi.org/10.1093/bioinformatics/btab038

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
Folder `experiments_materials` contains all the scripts, datasets, and results used to reproduce all the plots and tables in the manuscript. 

## Acknowledgements

The UNSGA3 code is adopted from prior work by Mark N. Read, contained within the repository https://github.com/marknormanread/unsga3, and devloped as part of the following manuscript:

> MN Read, K Alden, J Timmis and PS Andrews. (2020). Strategies for Calibrating Models of Biology. Briefings in Bioinformatics 21(1):24–35
