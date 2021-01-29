import pandas as pd
import itertools
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
from scipy import stats


def normalise_fronts_and_compare(dat_fronts):
    """
    Extract Front position from each dataset, scale them to value 0-1, and then combined together.

    To run this, please run UNSGA3 to obtain the fronts for individual dataset.
    What UNSGA3 does is collate results from all algorithms and determine which results fall in which front.

    Parameters
    ----------
    dat_fronts
        Dataframe containing the front position of each clustering solution.


    Returns
    -------
    ks_scores_df
        Data frame containing comparison of normalised front using KS test
    dat_fronts_scaled
        Data frame containing normalised fronts

    """

    dat_fronts_scaled, scaled_front_positions_per_algo = _obtain_front_position_distribution_per_algorithm(dat_fronts)

    # do stat comparison
    algorithm_combinations = list(itertools.combinations(scaled_front_positions_per_algo.keys(), 2))

    ks_scores = {}
    for combo in algorithm_combinations:
        ks = stats.ks_2samp(scaled_front_positions_per_algo[combo[0]], scaled_front_positions_per_algo[combo[1]])
        ks_scores[combo] = ks

    # turn the dictionary into data frame
    ks_scores_df = defaultdict(list)
    for algorithms, ks_val in ks_scores.items():
        ks_scores_df['Algo1'].append(algorithms[0])
        ks_scores_df['Algo2'].append(algorithms[1])
        ks_scores_df['ks_dval'].append(ks_val[0])
        ks_scores_df['ks_pval'].append(ks_val[1])
        ks_scores_df['stat_sig(<0.005)'].append(ks_val[1] < 0.005)

    ks_scores_df = pd.DataFrame(ks_scores_df)

    return ks_scores_df, dat_fronts_scaled


def _obtain_front_position_distribution_per_algorithm(dat_fronts):
    """
    Extract the distribution of the front position assigned to clustering performed by algorithms on a collection of datasets.

    Parameters
    ----------
    dat_fronts
        Dataframe containing the front position of each clustering solution.

    Returns
    -------
    dat_fronts_copy
        Dataframe with normalised front position appended as column
    scaled_front_positions_per_algo
        Dictionary of list whereby the key is the algorithm and the value is a list of front for that algorithm


    """

    dat_fronts_copy = dat_fronts.copy(deep=True)

    scaled_front_positions_per_algo = defaultdict(list)


    front_positions, algorithms = _extract_front_position_and_algorithm(dat_fronts)
    scaled_front_positions = _scale_front_position(front_positions)

    dat_fronts_copy["NormalisedFrontPosition"] = scaled_front_positions

    for algo, scaled_front_pos in zip(algorithms, scaled_front_positions):
        scaled_front_positions_per_algo[algo].append(scaled_front_pos)

    return dat_fronts_copy, scaled_front_positions_per_algo


def _extract_front_position_and_algorithm(dat_fronts):
    """
    Extract the front position and the algorithm that attains that position from csv file containing all the fronts.

    If data frame looks like the following:
    FrontPosition,Param,Algorithm,accuracy,ari,f1,v_measure,...
    0,14,flowsom,0.8653243136343433,0.8488031614290209,0.5529401333333333,0.8480365971331482,...
    0,17,flowsom,0.8478150064630302,0.8221457602460215,0.5608524,0.8336323350777118,...
    0,4,flowsom,0.8446222287464167,0.8321724202159276,0.5693965,0.8410890842399183,...
    0,87,flowsom,0.8363324240237154,0.8339606869070382,0.5560843666666667,0.831200859165602,...

    Then it will return just the FrontPosition and Algorithm column.

    The original order in the data frame will be preserved.

    Parameters
    ----------
    dat_fronts
        Dataframe containing the front position of each clustering solution.

    Returns
    -------
    fronts
        Array of Front positions
    algorithms
        Array of Algorithms names
    """

    fronts = dat_fronts['FrontPosition'].to_numpy()
    algorithms = dat_fronts['Algorithm'].to_numpy()

    return fronts, algorithms


def _scale_front_position(front_positions):
    """
    Scale fronts position to 0-1

    Parameters
    ----------
    front_positions
        Array of integer containing position of all fronts

    Returns
    -------
    scaled_front_positions
        Array of scaled front position
    """

    # stupid sklearn cannot normalise 1d array
    front_positions_np = np.array(front_positions).reshape(-1, 1)

    min_max_scaler = MinMaxScaler()
    scaled_front_positions = min_max_scaler.fit_transform(front_positions_np)

    return scaled_front_positions.reshape(1, -1)[0]
