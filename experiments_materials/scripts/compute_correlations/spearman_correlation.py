from scipy import stats
import itertools
import pandas as pd

from collections import defaultdict
from os.path import expanduser


metrics = ["accuracy", "ari", "f1", "v_measure"]
datasets = ['Levine_13dim', 'Levine_32dim','Samusik_01', 'Samusik_all']
metrics_inc_rare = ['accuracy', 'f1']
pval_threshold = 0.005


def calculate_spearman(datasets_arg, metrics_arg, scores_per_metric, scores_per_metric_per_dataset):
    # calculate overall spearman correlation
    spearman_overall = {}
    # initialise dict within dict
    spearman_per_dataset_overall = {}
    for d in datasets_arg:
        spearman_per_dataset_overall[d] = {}

    metric_combos = list(itertools.combinations(metrics_arg, 2))

    for metric_combo in metric_combos:

        rho, pval = stats.spearmanr(scores_per_metric[metric_combo[0]], scores_per_metric[metric_combo[1]])
        spearman_overall[metric_combo] = (rho, pval)

        # calculate correlation per dataset
        for d in datasets_arg:
            all_scores = scores_per_metric_per_dataset[d]
            rho, pval = stats.spearmanr(all_scores[metric_combo[0]], all_scores[metric_combo[1]])
            spearman_per_dataset_overall[d][metric_combo] = (rho, pval)

    return spearman_overall, spearman_per_dataset_overall


def calculate_spearman_correlation(datadir, outdir, algorithms):
    """
    Calculate spearman correlation between different supervised metrics for all clustering.
    """

    # setup the datasets

    # for overall calculation (combining flowsom and chronoclust)

    datasets_to_process = datasets

    scores_per_metric_overall = defaultdict(list)
    # initialise dict within dict
    scores_per_metric_per_dataset_overall = {}
    for d in datasets_to_process:
        scores_per_metric_per_dataset_overall[d] = {}

    # calculate spearman per algorithm
    for algo in algorithms:
        scores_per_metric = defaultdict(list)

        # initialise dict within dict
        scores_per_metric_per_dataset = {}
        for d in datasets_to_process:
            scores_per_metric_per_dataset[d] = {}

        for dataset in datasets_to_process:
            scores = pd.read_csv("{}/{}/clusterings_qualities/all_scores/{}_scores.csv".format(datadir, algo, dataset))
            for m in metrics:
                score_for_param = scores[m].to_numpy()

                scores_per_metric[m].extend(score_for_param)
                scores_per_metric_per_dataset[dataset][m] = score_for_param

                # for overall calculation (combining flowsom and chronoclust)
                scores_per_metric_overall[m].extend(score_for_param)
                scores_per_metric_per_dataset_overall[dataset][m] = score_for_param

        # calculate spearman correlation
        spearman, spearman_per_dataset = calculate_spearman(datasets_to_process,
                                                            metrics, scores_per_metric, scores_per_metric_per_dataset)

        # save as csv
        csv_filename = "{}/{}/spearman_score.csv".format(outdir, algo)
        save_spearman_overall(csv_filename, spearman)

        csv_per_dataset_filename = "{}/{}/spearman_score_per_dataset.csv".format(outdir, algo)
        save_spearman_per_dataset(csv_per_dataset_filename, spearman_per_dataset)

    # calculate overall spearman correlation
    spearman_overall, spearman_per_dataset_overall = calculate_spearman(datasets_to_process, metrics,
                                                                        scores_per_metric_overall,
                                                                        scores_per_metric_per_dataset_overall)

    # save as csv
    csv_filename_overall = "{}/spearman_score.csv".format(outdir)
    save_spearman_overall(csv_filename_overall, spearman_overall)

    csv_per_dataset_overall_filename = "{}/spearman_score_per_dataset.csv".format(outdir)
    save_spearman_per_dataset(csv_per_dataset_overall_filename, spearman_per_dataset_overall)


def save_spearman_per_dataset(csv_filename, spearman_per_dataset):
    with open(csv_filename, "w") as f:
        f.write("Dataset,Metric1,Metric2,CorrelationCoefficient,PValue,PValue<{}\n".format(pval_threshold))
        for dataset in spearman_per_dataset.keys():
            metric_combos = spearman_per_dataset[dataset]
            for metric_combo, value in metric_combos.items():
                rho = value[0]
                pval = value[1]
                f.write("{},{},{},{},{},{}\n".format(dataset, metric_combo[0], metric_combo[1], rho, pval,
                                                     pval < pval_threshold))


def save_spearman_overall(csv_filename, spearman):
    with open(csv_filename, "w") as f:
        f.write("Metric1,Metric2,CorrelationCoefficient,PValue,PValue<{}\n".format(pval_threshold))
        for metrics_combo, val in spearman.items():
            pval = val[1]
            rho = val[0]
            f.write("{},{},{},{},{}\n".format(metrics_combo[0], metrics_combo[1], rho, pval, pval < pval_threshold))


if __name__ == "__main__":
    home = expanduser("~")
    outdir = '{}/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/spearman_scores'.format(home)
    datadir = '{}/Documents/phd/code/ParetoBench/experiments_materials'.format(home)

    calculate_spearman_correlation(datadir=datadir, outdir=outdir, algorithms=['chronoclust', 'flowsom', 'phenograph'])
