from collections import defaultdict
from os.path import expanduser

import pandas as pd
import warnings

datasets = ['Levine_13dim', 'Levine_32dim','Samusik_01', 'Samusik_all']


def find_best_param_per_metric(datadir, algo, outdir):
    """
    For each supervised metric, find the best parameter i.e. the clustering it deem attains the best score.
    and obtain for that result, the score for other metrics, as well as the ranking.
    """

    df = defaultdict(list)
    for dataset in datasets:

        scores = pd.read_csv("{}/{}/clusterings_qualities/all_scores/{}_scores.csv".format(datadir, algo, dataset))

        accuracy = scores[['accuracy', 'param']]
        ari = scores[['ari', 'param']]
        f1 = scores[['f1', 'param']]
        vmeasure = scores[['v_measure', 'param']]

        best_params = {}
        # find ranking per entry
        for df_temp, metric in zip([accuracy, ari, f1, vmeasure], ['accuracy', 'ari', 'f1', 'v_measure']):
            df_temp['ranking'] = df_temp[metric].rank(method='min', ascending=False)
            # find the param of the result with
            best_params[metric] = df_temp[(df_temp['ranking'] == 1.0)]['param'].to_numpy()[0]

        for metric, best_param in best_params.items():
            accuracy_row = accuracy[(accuracy['param']) == best_param]
            ari_row = ari[(ari['param']) == best_param]
            f1_row = f1[(f1['param']) == best_param]
            v_measure_row = vmeasure[(vmeasure['param']) == best_param]

            df['dataset'].append(dataset)
            df['best_metric_by'].append(metric)
            df['best_param_id'].append(best_param)

            df['accuracy'].append(accuracy_row['accuracy'].to_numpy()[0])
            df['ari'].append(ari_row['ari'].to_numpy()[0])
            df['f1'].append(f1_row['f1'].to_numpy()[0])
            df['vmeasure'].append(v_measure_row['v_measure'].to_numpy()[0])

            df['ranking_accuracy'].append(accuracy_row['ranking'].to_numpy()[0])
            df['ranking_ari'].append(ari_row['ranking'].to_numpy()[0])
            df['ranking_f1'].append(f1_row['ranking'].to_numpy()[0])
            df['ranking_vmeasure'].append(v_measure_row['ranking'].to_numpy()[0])

    df = pd.DataFrame(df)
    # reorder columns
    df = df[['dataset', 'best_metric_by', 'best_param_id',
                'accuracy', 'ranking_accuracy',
                'ari', 'ranking_ari',
                'f1', 'ranking_f1',
                'vmeasure', 'ranking_vmeasure']]
    df.to_csv("{}/{}_best_param_per_metric.csv".format(outdir, algo), index=False)


if __name__ == "__main__":
    home = expanduser("~")
    outdir = '{}/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/best_param_per_metric'.format(home)
    datadir = '{}/Documents/phd/code/ParetoBench/experiments_materials'.format(home)

    algorithms=['chronoclust', 'flowsom', 'phenograph']

    for algo in algorithms:
        find_best_param_per_metric(datadir=datadir, outdir=outdir, algo=algo)

    
    