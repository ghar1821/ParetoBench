import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pdc_in_a = [10-x for x in list(range(0,11))]

accuracy = [0.9950, 0.9949, 0.9948, 0.9947, 0.9946, 0.9945, 0.9944, 0.9943, 0.9942, 0.9941, 0.9940]

precision = [0.5833, 0.5762, 0.5689, 0.5612, 0.5534, 0.5452, 0.5367, 0.5279, 0.5188, 0.5093, 0.4495]
recall = [0.9975, 0.9475, 0.8975, 0.8475, 0.7975, 0.7475, 0.6975, 0.6475, 0.5975, 0.5475, 0.4975]
fmeasure = [0.6416, 0.6292, 0.6163, 0.6031, 0.5895, 0.5755, 0.5611, 0.5462, 0.5308, 0.5149, 0.4985]

# merge all measures into 1 column
all_measures = accuracy + precision + recall + fmeasure
all_pdc_in_a = pdc_in_a + pdc_in_a + pdc_in_a + pdc_in_a
measure_type = ['Accuracy'] * len(accuracy) + ['Precision'] * len(precision) + ['Recall'] * len(recall) + ['F-measure'] * len(fmeasure)
ylabel = "Value"
xlabel = "Number of PDC in moved from cluster B to cluster A"
hue = "Metric"
df = pd.DataFrame({
    ylabel: all_measures,
    xlabel: all_pdc_in_a,
    hue: measure_type
    })

sns.set_style("whitegrid")
ax = sns.lineplot(x=xlabel, y=ylabel, hue=hue, data=df)
ax.set_xticks(np.arange(0, 11, 1))
ax.set_yticks(np.arange(0.4, 1.05, 0.05))
ax.get_legend().remove()
plt.title("Changes in accuracy, precision, recall, and F-measure")
plt.xlabel("Number of PDC re-allocated from cluster B to cluster A")
plt.savefig("/Users/givanna/Documents/phd/writings/clustering_performance_assessment/images/metrics/changes.eps")