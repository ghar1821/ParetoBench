library(ggplot2)
library(ggbeeswarm)

setwd("~/Documents/phd/code/ParetoBench/ParetoBench/plots")
source("custom_ecdf.R")
source("draw_paretos.R")

setwd("~/Documents/phd/code/ParetoBench/experiments_materials/pareto_comparison/comparison_results/")

datasets = c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all")

for (dataset in datasets) {
    for (blank_axis in c(TRUE, FALSE)) {
        draw_cdf(dataset=dataset,
                 colours=c("#ff653b", "#3b55ff", "#3cc23a"),
                 blank_axis=blank_axis,
                 save_to_disk=TRUE,
                 img_width=10
        )
        
        draw_swarm(dataset=dataset, 
                   colours=c("#ff653b", "#3b55ff", "#3cc23a"), 
                   blank_axis=blank_axis,
                   use_quasi_random=TRUE,
                   save_to_disk=TRUE
        )
    }
    
}

draw_cdf(dataset="all_datasets", 
         colours=c("#ff653b", "#3b55ff", "#3cc23a"), 
         blank_axis=TRUE,
         save_to_disk=TRUE,
         img_width=10
)

draw_swarm(dataset="all_datasets", 
           colours=c("#ff653b", "#3b55ff", "#3cc23a"), 
           blank_axis=TRUE,
           save_to_disk=TRUE,
           use_quasi_random=TRUE,
           dot_size = 0.5
)
