# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 17:25:17 2019

@author: ghar1821
"""

import pandas as pd
from sklearn.metrics import adjusted_rand_score
from pathlib import Path
import os

def calculate_ari(i):

    # datasets = ['Levine_13dim', 'Levine_32dim', 'Samusik_01', 'Samusik_all']
    datasets = ['Levine_32dim', 'Samusik_all']
    true_labels_dir = os.path.expanduser("/Users/macmini/dropbox/pareto_bench/dataset/csv_exports_unnormalised")
    res_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/phenograph/raw_clusterings")
    out_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/phenograph/clusterings_qualities/ari")

    for dataset in datasets:

        truth_file = '{}/{}.csv'.format(true_labels_dir, dataset)
        truth_df = pd.read_csv(truth_file)
    
        truth = truth_df['label'].to_numpy()
  
        datadir = Path("{}/{}".format(res_dir, dataset))

        # read and convert meta cluster to the mapped label
        cluster_file = datadir / '{}_clustered.csv'.format(i)
        cluster_df = pd.read_csv(cluster_file)

        df = pd.DataFrame({
            'TrueLabel': truth,
            'ClusterLabel': cluster_df['phenograph_cluster'].to_numpy()
            })

        # replace NA with a numeric number
        df['ClusterLabel'].fillna(-1, inplace=True)

        # To remove cells with no mapped true label.
        df = df.dropna()
        
        ari = adjusted_rand_score(df['TrueLabel'].to_numpy(), df['ClusterLabel'].to_numpy())
        
        with open("{}/{}/{}.txt".format(out_dir, dataset, i), 'w') as f:
            f.write(str(ari))
