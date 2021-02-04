from ParetoBench.find_pareto import find_pareto_per_dataset
from ParetoBench.analyse_pareto import normalise_fronts_and_compare
from functools import reduce

import os
import pandas as pd


def compare(metrics, datasets, algorithms, datadir, savedir, param_id_col, front_limits = [0.1, 0.33]):
    """
    Compare algorithms performance using Pareto front.
    For this to work, you need to have 1 csv file per algorithm per dataset. 
    The files must be stored within datadir.
    Within each file, you need to have x rows where each row represents the quality of 1 clustering solution
    for that dataset for that algorithm.
    There must be y columns where each column represents a metric.
    The name of the columns must match what's stored in metrics variable below.
    The datasets name must match what's stored in datasets variable below.
    The algorithms name must match what's stored in the algorithms variable below.
    So for instance, if you have 2 datasets (A and B), and 2 algorithms (Alg1 and Alg2), if datadir is "~/ParetoBench", 
    then you should have the following files (watch the naming):
        "~/ParetoBench/Alg1/A_scores.csv",
        "~/ParetoBench/Alg1/B_scores.csv",
        "~/ParetoBench/Alg2/A_scores.csv",
        "~/ParetoBench/Alg2/B_scores.csv".

    Parameters
    ----------
    metrics
        Array of name of metrics used for comparison
    datasets
        Array of name of datasets used for comparison
    algorithms
        Array of name of algorithms to be compared
    datadir
        String showing the folder where the csv files containing quality of algorithm's solutions are stored.
    savedir
        String showing the folder where the results will be stored
    param_id_col
        String indicating the column in the csv files denoting the unique ID of the solution. MUST BE THE SAME for all csv files!
    front_limits
        The Pareto front ranks limits to report in summary. Used to compare how easy to tune an algorithm is.
        Default to [0.1, 0.33].
        
    Returns
    -------
    Nothing. Results are automatically exported.

    """


    create_dir(savedir)

    pareto_per_dataset = find_pareto_per_dataset(datadir, datasets, algorithms, metrics, param_id_col)

    pareto_all_datasets = []

    for dataset, df in pareto_per_dataset.items():
        ks_scores, norm_df = normalise_fronts_and_compare(df)
        norm_df.to_csv('{}/front_positions_{}.csv'.format(savedir, dataset), index=False)
        ks_scores.to_csv('{}/ks_{}.csv'.format(savedir, dataset), index=False)

        # count number of solutions per front
        count_solution_per_front = count_proportion_of_solutions_on_each_front(norm_df)
        count_solution_per_front.to_csv('{}/proportion_solutions_per_front_{}.csv'.format(savedir, dataset), index=False)

        summary_dataset = create_summary(norm_df, front_limits)
        summary_dataset.to_csv('{}/summary_{}.csv'.format(savedir, dataset), index=False)
        
        # for normalising for all datasets
        pareto_all_datasets.append(df)

    # combine all results and normalise
    pareto_all_datasets = pd.concat(pareto_all_datasets)
    ks_scores, norm_df = normalise_fronts_and_compare(pareto_all_datasets)
    norm_df.to_csv('{}/front_positions_all_datasets.csv'.format(savedir), index=False)
    ks_scores.to_csv('{}/ks_all_datasets.csv'.format(savedir), index=False)

    count_solution_per_front = count_proportion_of_solutions_on_each_front(norm_df)
    count_solution_per_front.to_csv('{}/proportion_solutions_per_front_all_datasets.csv'.format(savedir), index=False)

    summary_dataset = create_summary(norm_df, front_limits)
    summary_dataset.to_csv('{}/summary_all_datasets.csv'.format(savedir), index=False)


def create_summary(data, front_limits):
    """
    Compute a summary result showing the proportion of solutions for each algorithm which lie on the Pareto front,
    as well as the proportion of solutions (per algorithm) which lie before (including) front_limit_1 and front_limit_2

    Parameters
    ----------
    data
        Data frame containing the front position of clustering solutions
    front_limits
        The Pareto front ranks limits to report in summary. Used to compare how easy to tune an algorithm is.

    Returns
    -------
    summary
        Data frame summarising the performance of algorithms
    """

    summary_res = []
    # count proportion of solutions per algorithm
    # cnt_sol_per_front = count_proportion_of_solutions_on_each_front(data)
    # cnt_sol_per_front = cnt_sol_per_front[(cnt_sol_per_front.FrontPosition == 0)].filter(items=['Algorithm', 'proportion', 'num_solutions_total'], axis=1).reset_index(drop=True)
    # cnt_sol_per_front.rename(columns={"proportion": "Proportion_front=0"}, inplace=True)
    # summary_res.append(cnt_sol_per_front)
    
    # count proportion of solutions up until limit
    front_limits_to_compute = [0] + front_limits
    for front_limit in front_limits_to_compute:      
        solutions_up_until_limit = count_proportion_of_solutions_until_limit(data, front_limit)        
        solutions_up_until_limit_colsRenamed = solutions_up_until_limit.filter(items=['Algorithm', 'proportion']).reset_index(drop=True)
        solutions_up_until_limit_colsRenamed.rename(columns={"proportion": "Proportion_front<={}".format(front_limit)}, inplace=True)
        summary_res.append(solutions_up_until_limit_colsRenamed)

    df_summary = reduce(lambda left,right: pd.merge(left,right,on='Algorithm'), summary_res)
    df_summary.sort_values(by='Algorithm', inplace=True)
    return(df_summary)

def count_proportion_of_solutions_until_limit(data, front_limit):
    """
    Compute proportion of solutions lie up until a certain limit in normalised front.

    Parameters
    ----------
    data
        Data frame containing the front position of clustering solutions
    front_limit
        The limit of normalised front to count the proportion

    Returns
    -------
    prop
        Proportion of solutions per algorithm which lie up until the front_limit
    """
    dat_subset = data[(data.NormalisedFrontPosition <= float(front_limit))]
    num_solutions_per_algo = count_num_solutions_per_algo(data)

    cnt = dat_subset.value_counts(subset=['Algorithm'])
    cnt_df = pd.DataFrame({'count' : cnt}).reset_index()

    # join them and compute the proportions
    cnt_df_joined = cnt_df.set_index('Algorithm').join(num_solutions_per_algo.set_index('Algorithm')).reset_index()
    cnt_df_joined['proportion'] = cnt_df_joined['count'] / cnt_df_joined['num_solutions_total']


    # if an algorithm does not contribute any solutions, this won't return the row for it
    # so we need to explicitly add it as a row
    algorithms = num_solutions_per_algo['Algorithm'].to_numpy()
    algo_in_cnt_df_joined = cnt_df_joined['Algorithm'].to_numpy()

    for algo in algorithms:
        if (algo not in algo_in_cnt_df_joined):
            algo_details = num_solutions_per_algo[(num_solutions_per_algo.Algorithm == algo)]
            cnt_df_joined = cnt_df_joined.append({'Algorithm':algo, 'count':0, 'num_solutions_total':algo_details['num_solutions_total'], 'proportion':0}, ignore_index=True)
    
    return(cnt_df_joined)



def count_proportion_of_solutions_on_each_front(data):
    """
    Compute the proportion of solutions contributed by each algorithm for each front.

    Parameters
    ----------
    data
        Data frame containing the front position of clustering solutions

    Returns
    -------
    cnt
        Data frame showing count of solutions in each front for each algorithm

    """
    cnt = data.value_counts(subset=['Algorithm', 'FrontPosition']) 
    cnt_df = pd.DataFrame({'count' : cnt}).reset_index()
    cnt_df.sort_values(by=['FrontPosition'], inplace=True)

    # count number of solutions per algorithm
    num_solutions = count_num_solutions_per_algo(data)

    # join them and compute the proportions
    cnt_df_joined = cnt_df.set_index('Algorithm').join(num_solutions.set_index('Algorithm')).reset_index()
    cnt_df_joined['proportion'] = cnt_df_joined['count'] / cnt_df_joined['num_solutions_total']

    cnt_df_joined.sort_values(by=['FrontPosition', 'proportion'], ascending=[True, False], inplace=True)

    return(cnt_df_joined)


def count_num_solutions_per_algo(data):
    """
    Count number of solutions per algorithm

    Parameters
    ----------
    data
        Data frame containing the front position of clustering solutions

    Returns
    -------
    num_solutions
        Data frame showing number of solutions for each algorithm
    """
    
    num_solutions = data.value_counts(subset=['Algorithm'])
    num_solutions = pd.DataFrame({'num_solutions_total' : num_solutions}).reset_index()

    return(num_solutions)
    

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)