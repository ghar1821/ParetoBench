import phenograph
import pandas as pd
import numpy as np
import sys

def run(dataset, k, res_file):
    dat = pd.read_csv("~/dropbox/pareto_bench/dataset/csv_exports_unnormalised/{}.csv".format(dataset))
    dat.drop(['label'], axis=1, inplace=True)

    # dat_sub = dat.loc[np.random.choice(dat.index, 10000, replace=False)]

    cluster, graph, modularity_score = phenograph.cluster(dat, k=int(k), primary_metric='euclidean')

    dat['phenograph_cluster'] = pd.Series(cluster)

    dat.to_csv(res_file)


dataset_name = sys.argv[1]
param_file = sys.argv[2]
out_dir = sys.argv[3]

params = pd.read_csv(param_file)
for idx, row in params.iterrows():
    k = int(row['k'])
    print("clustering param={}, k={}".format(idx, k))
    res_file = '{}/{}_clustered.csv'.format(out_dir, idx)
    run(dataset_name, k, res_file)
