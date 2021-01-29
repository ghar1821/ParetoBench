import pandas as pd
from pathlib import Path
from os import listdir, makedirs
from os.path import isfile, join, exists, expanduser
from collections import defaultdict
from functools import reduce

home = expanduser("~")

def collect_f1(dataset):
    df = defaultdict(list)
    res_dir = '{}/Documents/phd/code/ParetoBench/experiments_materials/phenograph/clusterings_qualities/F1-eval/{}'.format(home, dataset)
    files = [f for f in listdir(res_dir) if isfile(join(res_dir, f))]

    for f in files:
        with open('{}/{}'.format(res_dir, f), 'r') as fname:
            score = fname.readline().strip()
        param_id = f.split("_")[1].split('Param')[-1].split('.')[0]

        df['param'].append(int(param_id))
        df['f1'].append(score)

    df = pd.DataFrame(df)

    return df

def collect_others(metric, dataset):
    df = defaultdict(list)

    res_dir = '{}/Documents/phd/code/ParetoBench/experiments_materials/phenograph/clusterings_qualities/{}/{}'.format(home, metric, dataset)
    files = [f for f in listdir(res_dir) if isfile(join(res_dir, f))]

    for f in files:
        with open('{}/{}'.format(res_dir, f), 'r') as fname:
            score = fname.readline().strip()
        param_id = f.split(".")[0]

        df['param'].append(int(param_id))
        df[metric].append(score)

    df = pd.DataFrame(df)

    return df


if __name__ == '__main__':
    datasets = ['Levine_13dim', 'Levine_32dim', 'Samusik_01', 'Samusik_all']
    
    out_dir = "{}/Documents/phd/code/ParetoBench/experiments_materials/phenograph/clusterings_qualities/all_scores".format(home)
    if not exists(out_dir):
        makedirs(out_dir)

    for d in datasets:

        f1_df = collect_f1(d)
        accuracy_df = collect_others("accuracy", d)
        ari_df = collect_others("ari", d)
        v_measure_df = collect_others("v_measure", d)

        dfs = [f1_df, accuracy_df, ari_df, v_measure_df]
        # join all 4 dataframes on param
        df_final = reduce(lambda left,right: pd.merge(left,right,on='param'), dfs)

        # read the parameter file and join it to the score file
        param_file = "{}/Documents/phd/code/ParetoBench/experiments_materials/phenograph/lhc_samples/LHC_{}.csv".format(home, d)
        params = pd.read_csv(param_file)
        param_cols = params.columns
        params['param'] = range(0, 100)
        df_final = df_final.merge(params, on=['param'])
        df_final.sort_values(by='param', inplace=True)
        # drop duplicated parameters
        df_final.drop_duplicates(subset=param_cols, inplace=True)

        df_final.to_csv("{}/{}_scores.csv".format(out_dir, d), index=False)
