# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 17:25:17 2019

@author: ghar1821
"""

import pandas as pd
import os
from coclust.evaluation.external import accuracy
from pathlib import Path

def calculate_accuracy(i):
    
    datasets = ['Levine_13dim', 'Levine_32dim', 'Samusik_01', 'Samusik_all']
    true_labels_dir = "~/dropbox/pareto_bench/dataset/csv_exports_unnormalised"
    res_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/chronoclust/raw_clusterings")
    out_dir = os.path.expanduser("~/Documents/phd/code/ParetoBench/experiments_materials/chronoclust/clusterings_qualities/accuracy")

    print(out_dir)

    for dataset in datasets:

        truth_file = os.path.expanduser('{}/{}.csv'.format(true_labels_dir, dataset))
        truth_df = pd.read_csv(truth_file)
    
        truth = truth_df['label'].to_numpy()
  
        datadir = Path("{}/{}".format(res_dir,dataset))

        # read and convert meta cluster to the mapped label
        cluster_file = datadir / '{}_clusters.txt'.format(i)
        cluster_df = pd.read_csv(cluster_file)

        df = pd.DataFrame({
            'TrueLabel': truth,
            'PredictedLabel': cluster_df['label'].to_numpy()
            })

        # To remove cells with no mapped true label.
        df = df.dropna()
        
        acc = accuracy(df['TrueLabel'].to_numpy(), df['PredictedLabel'].to_numpy())

        # For writing the result
        f = open("{}/{}/{}.txt".format(out_dir, dataset, i), 'w')
        f.write(str(acc))
        f.close()


# def calculate_accuracy(dataset, truth, outdir, datadir):

#     accuracies = []

#     out_dir = "{}/accuracy/{}".format(outdir, dataset)
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir)

#     for i in range(0, 100):
#         # numeric cluster label - converted
#         data_fname = datadir / Path('{}/{}_clusters.txt'.format(dataset, i))

#         cluster_label = pd.read_csv(data_fname)['label'].to_numpy()

#         df = pd.DataFrame({"cluster_id": cluster_label, "true_label": truth})
#         df = df.dropna()  # remove no label for true label.

#         if df.shape[0] == 0:
#             acc = 0
#         else:
#             acc = accuracy(df['true_label'].to_numpy(), df['cluster_id'].to_numpy())
            
#         accuracies.append(acc)
#     df = pd.DataFrame({"param": range(0,100), "accuracy": accuracies})
#     df.to_csv("{}/{}_accuracy.csv".format(out_dir, dataset), index=False)
