from unsga3.non_dominated_sort import non_dominated_sort as non_dominated_sort
from unsga3.unsga3 import (ParetoFitness, Candidate)
from collections import defaultdict

import numpy as np
import pandas as pd

def tranform_scores_to_population(score_file, algorithm, dataset, measures_to_use, param_id_col):
    """
    Read the clustering quality score and transform them to unsga3 population for processing later.

    Parameters
    ----------
    score_file
        Csv file containing the quality of clustering solutions for a dataset and an algorithm.
    
    algorithm
        The name of the algorithm which produces the clustering solutions in the score_file.
    
    dataset
        The dataset in which the algorithm is ran on.
    
    measures_to_use
        Array of metrics used to evaluate the quality of the clustering solutions. 
        The content of the array must match the columns in the score_file.

    param_id_col
        String indicating the column in the csv files denoting the unique ID of the solution.

    Return
    ------
    population (unsga3.Candidate object)
        Array of Candidate object whereby each object represents a clustering solution. 
    """

    population = []

    reciprocal_score_per_measure = []
    original_score_per_measure = []

    # consolidate scores for all dataset into 1 giant dataframe
    df = pd.read_csv(score_file)

    for m in measures_to_use:
        scores = df[m].to_numpy()

        scores_reciprocal = np.negative(scores)
        
        reciprocal_score_per_measure.append(scores_reciprocal)
        original_score_per_measure.append(scores)

    # original array contain 4 arrays, each array is all the clustering as evaluated by ONE metric.
    # we need to transpose it in such a way that each array is a clustering result as evaluate by all FOUR metrics.
    reciprocal_score_per_measure = np.transpose(np.array(reciprocal_score_per_measure))
    original_score_per_measure = np.transpose(np.array(original_score_per_measure)) 

    param_ids = df[param_id_col].to_numpy()   

    for i, c in enumerate(reciprocal_score_per_measure):
        fit = ParetoFitness(c)
        cand = Candidate(solution=[])
        cand.training_fitness = fit
        cand.activate_training_fitness()
        cand.label = param_ids[i]
        cand.original_score = original_score_per_measure[i]
        cand.algorithm = algorithm
        cand.dataset = dataset
        population.append(cand)

    return population


def find_pareto_per_dataset(datadir, datasets, algorithms, measures_to_use, param_id_col):
    """
    Determine the front positions of each clustering solution.

    Parameters
    ----------
    datadir 
        Directory where the files storing the clustering solutions qualities are stored.
                            This directory must store all the solutions for an algorithm in its own folder.
                            Within each algorithm directory, there must be several csv files in which each csv file contains the 
                            quality of the clustering solutions for a dataset.
                            So for instance, if you have 2 datasets (A and B), and 2 algorithms (Alg1 and Alg2),
                            if datadir is "~/ParetoBench", then you should have the following structure:
                                "~/ParetoBench/Alg1/A_scores.csv",
                                "~/ParetoBench/Alg1/B_scores.csv",
                                "~/ParetoBench/Alg2/A_scores.csv",
                                "~/ParetoBench/Alg2/B_scores.csv".
    
    datasets
        Array of datasets in which the algorithms are ran on.
    
    algorithms
        Array of algorithms to compare.
    
    measures_to_use
        Array of metrics used to compare the quality of solutions.

    param_id_col
        String indicating the column in the csv files denoting the unique ID of the solution.

    
    Return
    ------
    pareto_df
        Data frame showing the front position for each algorithm and parameter

    """

    # to store the pareto front of a dataset. 1 dataset = 1 data frame ordered by the front position
    pareto_df = {}

    for dataset in datasets:
        populations = []

        for algorithm in algorithms:
            score_file = "{}/{}/{}_scores.csv".format(datadir, algorithm, dataset)
            population = tranform_scores_to_population(score_file=score_file,
                                                       algorithm=algorithm,
                                                       dataset=dataset,
                                                       measures_to_use=measures_to_use,
                                                       param_id_col=param_id_col)

            populations.extend(population)

        fronts = non_dominated_sort(populations)

        # for saving data as csv
        front_df = defaultdict(list)

        for i, front in enumerate(fronts):
            for cand in front:
                front_df['FrontPosition'].append(i)
                front_df['Param'].append(cand.label)
                front_df['Algorithm'].append(cand.algorithm)
                for score, metric in zip(cand.original_score, measures_to_use):
                    front_df[metric].append(score)

                for objective, metric in zip(cand.training_fitness, measures_to_use):
                    front_df[metric + '_negate'].append(objective)

        df_paretos = pd.DataFrame(front_df)
        pareto_df[dataset] = df_paretos

    return pareto_df
