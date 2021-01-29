import pandas as pd
import numpy as np

from pprint import pprint


def map_cluster_id(cluster_filename, mapped_cluster_filename, mapping_filename):
	"""
	Map each cluster id to numeric equivalent.
	Simplest thing to do is just grab number from 0 to whatever, store it in
	array, then just map it with zip loop

	Unclustered data will be assigned numeric id 0 i.e. those with None as cluster id.
	
	Parameters
	==========
	cluster_filename : str
		Name of the file containing data points and the cluster each of it belong to.
	mapped_cluster_filename : str
		Name of the file to output the mapped cluster id
	mapping_filename : str
		Name of the file to export the mapping scheme.

	Return
	======
	None
	"""


	df = pd.read_csv(cluster_filename)

	unique_clusters = df['cluster_id'].unique()

	# Handling unclustered data. 
	# To do this by removing none from unique clusters and manually add it to
	# the mapping dictionary (storing the mapping)
	numeric_cluster_id_mapping = {'None': 0}
	none_index = np.where(unique_clusters == 'None')
	unique_clusters = np.delete(unique_clusters, none_index)

	unique_clusters = np.sort(unique_clusters) # not necessary, but help

	for cl, i in zip(unique_clusters, range(1, len(unique_clusters)+1)):
	    numeric_cluster_id_mapping[cl] = i

	with open(mapping_filename, 'wt') as out:
	    pprint(numeric_cluster_id_mapping, stream=out)

	# start mapping
	numeric_cluster_id = []
	for row in df.itertuples():
	    cluster_id = getattr(row, 'cluster_id')
	    numeric_cluster_id.append(numeric_cluster_id_mapping[cluster_id])

	with open(mapped_cluster_filename, 'w') as f:
	    f.write('label\n')
	    for n in numeric_cluster_id:
	        f.write(str(n))
	        f.write('\n')
