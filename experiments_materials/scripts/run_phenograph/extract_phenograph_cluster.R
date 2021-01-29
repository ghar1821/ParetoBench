# Don't want to store the entire data and cluster as one file is huge. 
# We only need the cluster id as we can do a cbind to the raw dataset if need be. 
# Thus let's just store the cluster data.

library(data.table)

primary_dir = "~/Documents/phd/code/ParetoBench/experiments_materials/phenograph/raw_clusterings"
out_dir = paste0(primary_dir, "/cluster_only")

list.dirs()
datasets = c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all")

for (dataset in datasets[c(1, 3)]) {
    dataset_out_dir = paste0(out_dir, '/', dataset)
    dir.create(dataset_out_dir)
    dat_dir = paste0(primary_dir, '/', dataset)
    setwd(dat_dir)
    res_files = list.files()
    for (res_file in res_files) {
        res = fread(res_file)
        clusters = data.table(phenograph_cluster=res$phenograph_cluster)
        fwrite(clusters, file = paste0(dataset_out_dir, '/', res_file))    
    }
}
