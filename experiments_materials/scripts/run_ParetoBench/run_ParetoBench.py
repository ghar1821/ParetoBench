# Run pareto bench

import ParetoBench
from os.path import expanduser

home = expanduser("~")

metrics = ['accuracy', 'ari', 'f1', 'v_measure']
datasets = ['Levine_13dim', 'Levine_32dim', 'Samusik_01', 'Samusik_all']
algorithms = ['chronoclust', 'flowsom', 'phenograph']
datadir = "{}/Documents/phd/code/ParetoBench/experiments_materials/pareto_comparison".format(home)
savedir = "{}/Documents/phd/code/ParetoBench/experiments_materials/pareto_comparison/comparison_results".format(home)

ParetoBench.compare(
    metrics = metrics,
    datasets = datasets,
    algorithms = algorithms,
    datadir = datadir,
    savedir = savedir
)
