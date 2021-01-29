import itertools
import pandas as pd
import seaborn as sns

from matplotlib import pyplot as plt
from collections import defaultdict
from os.path import expanduser


metrics = ["accuracy", "ari", "f1", "v_measure"]
datasets = ['Levine_13dim', 'Levine_32dim','Samusik_01', 'Samusik_all']

sns.set(style="whitegrid")


def plot_correlation_scatter(datadir, outdir, algorithms):
    """
    Draw scatter plot for every combination of 2 metrics to show correlation.
    Manuscript Figure 2C.
    """

    datasets_to_process = datasets

    scores_per_metric = defaultdict(list)

    # initialise dict within dict
    scores_per_metric_per_dataset = {}
    for d in datasets_to_process:
        scores_per_metric_per_dataset[d] = {}

    for algo in algorithms:
        for dataset in datasets_to_process:
            scores = pd.read_csv("{}/{}/clusterings_qualities/all_scores/{}_scores.csv".format(datadir, algo, dataset))
            for m in metrics:
                score_for_param = scores[m].to_numpy()

                scores_per_metric[m].extend(score_for_param)
                scores_per_metric_per_dataset[dataset][m] = score_for_param

    # custom label for plot
    labels = {
        "accuracy": "Accuracy",
        "ari": "ARI",
        "f1": "F-measure",
        "v_measure": "V-measure"
    }

    metric_combos = list(itertools.combinations(metrics, 2))

    # scatter plot per metric combo
    for metric_combo in metric_combos:
        sorted_metric_combo = sorted(metric_combo)

        # work out size of the data
        # print(len(scores_per_metric[sorted_metric_combo[0]]))
        # print(len(scores_per_metric[sorted_metric_combo[1]]))

        scatter = sns.scatterplot(x=scores_per_metric[sorted_metric_combo[1]],
                                  y=scores_per_metric[sorted_metric_combo[0]])
        scatter.tick_params(labelsize=12)
        plt.ylim(0, 1)
        plt.xlim(0, 1)

        plt.tight_layout()
        plt.savefig("{}/correlation_plots/correlation_{}_{}.pdf".format(outdir,
                                                                           sorted_metric_combo[0],
                                                                           sorted_metric_combo[1]))
        plt.clf()

if __name__ == "__main__":
    home = expanduser("~")
    outdir = '{}/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/spearman_scores'.format(home)
    datadir = '{}/Documents/phd/code/ParetoBench/experiments_materials'.format(home)

    plot_correlation_scatter(datadir=datadir, outdir=outdir, algorithms=['chronoclust', 'flowsom', 'phenograph'])