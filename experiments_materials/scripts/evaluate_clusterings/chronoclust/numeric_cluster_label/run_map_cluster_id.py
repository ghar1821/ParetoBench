import sys

from pathlib import Path
from get_numeric_cluster import map_cluster_id

dataset_path = Path(sys.argv[1])

outdir_cl_pts = dataset_path / Path('mapped_cluster_points')
outdir_mapping = dataset_path / Path('mapping_scheme')

# create output directory
outdir_cl_pts.mkdir(parents=True, exist_ok=True)
outdir_mapping.mkdir(parents=True, exist_ok=True)

data_fname = dataset_path  / 'cluster_points_D0.csv'

out_cl_fname = outdir_cl_pts / 'cluster.txt'
out_mapping = outdir_mapping / 'mapping.txt'
map_cluster_id(data_fname, out_cl_fname, out_mapping)
