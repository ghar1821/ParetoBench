# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 17:25:17 2019

@author: ghar1821
"""

import pandas as pd

from coclust.evaluation.external import accuracy
from pathlib import Path
import os

def calculate_accuracy(i):
    
    datasets = ['Levine_13dim', 'Levine_32dim', 'Samusik_01', 'Samusik_all']
    true_labels_dir = os.path.expanduser("~/dropbox/pareto_bench/dataset/csv_exports_unnormalised")
    res_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/flowsom/raw_clusterings")
    out_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/flowsom/clusterings_qualities/accuracy")

    for dataset in datasets:

        truth_file = '{}/{}.csv'.format(true_labels_dir, dataset)
        truth_df = pd.read_csv(truth_file)
    
        truth = truth_df['label'].to_numpy()
  
        datadir = Path("{}/{}".format(res_dir,dataset))

        # read and convert meta cluster to the mapped label
        cluster_file = datadir / 'Clustered_FlowSOM_Param{}.csv'.format(i)
        cluster_df = pd.read_csv(cluster_file)

        df = pd.DataFrame({
            'TrueLabel': truth,
            'PredictedLabel': cluster_df['FlowSOM_metacluster'].to_numpy()
            })

        # To remove cells with no mapped true label.
        df = df.dropna()
        
        acc = accuracy(df['TrueLabel'].to_numpy(), df['PredictedLabel'].to_numpy())

        # For writing the result
        f = open("{}/{}/{}.txt".format(out_dir, dataset, i), 'w')
        f.write(str(acc))
        f.close()
