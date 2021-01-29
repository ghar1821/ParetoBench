library(ggbeeswarm)
library(ggplot2)

setwd("~/Documents/phd/code/ParetoBench/ParetoBench/plots")
source("custom_ecdf.R")
source("draw_paretos.R")

setwd("~/Documents/phd/code/ParetoBench/experiments_materials/scripts/compute_examples/pareto_example/output/pareto_example/")

for (blank_axis in c(TRUE, FALSE)) {
  draw_cdf(dataset="",
           colours=c("#FF8900", "#0774A9"),
           blank_axis=blank_axis,
           save_to_disk=TRUE,
           img_height = 15,
           img_width = 20
  )
  draw_swarm(dataset="", 
             colours=c("#FF8900", "#0774A9"), 
             blank_axis=blank_axis,
             save_to_disk=TRUE,
             dot_size = 2,
             use_quasi_random = FALSE
  )
}





# source custom ecdf 
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)
setwd(script_dir)
source("../plot_utils/custom_ecdf.R")

setwd("/Users/givanna/dropbox/lweber_dataset/analysis_exc_noise_cells/comparing_algorithms/pareto_example")

dataset <- c("pareto_superior_hardToTune", "pareto_superior_sameToTune",
             "pareto_notSuperior_hardToTune", "pareto_notSuperior_sameToTune")

# draw cdf per dataset
for (d in dataset) {
  dat <- read.csv(paste0("normalised_front_positions_", d,".csv"))
  cdf.plt <- ggplot(dat, aes(NormalisedFrontPosition, colour = Algorithm)) + 
    # stat_ecdf(geom = 'step') +
    stat_myecdf() +
    scale_x_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
    scale_y_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
    scale_color_manual(values=c("#FF8900", "#0774A9")) +
    theme_bw()
  ggsave(paste0("cdf_", d, "_annotated.pdf"), width=15, height=8, units='cm')
  
  cdf.plt + theme(axis.title.x = element_blank()) +
    theme(axis.title.y = element_blank()) +
    theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
    theme(axis.text.y = element_blank()) +
    theme(legend.position = "none") 
  ggsave(paste0("cdf_", d, ".pdf"), width=12, height=10, units='cm')
}

## draw swarm for pareto_example
dat <- read.csv("pareto_example.csv")
swarm.plt <- ggplot(dat, aes(x=Algorithm, y=FrontPosition, color=Algorithm)) +
  geom_beeswarm(size=1, cex=1.5, priority = 'density') + 
  scale_color_manual(values=c("#FF8900", "#0774A9")) + 
  # ylim(0, 7) +
  scale_y_continuous(
    limits = c(0,6),
    breaks = round(seq(0,6, by = 1),1),
    minor_breaks = round(seq(0,6, by = 1),1)) +
  theme_bw()
ggsave(paste0("swarm_annotated.pdf"), width=15, height=8, units='cm')
swarm.plt + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_text(size=16, color='black')) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=16, color='black')) +
  theme(legend.position = "none") 
ggsave(paste0("swarm.pdf"), width=12, height=10, units='cm')  


## draw cdf for pareto_example
d <- "pareto_example"
dat <- read.csv(paste0("normalised_front_positions_", d,".csv"))
cdf.plt <- ggplot(dat, aes(NormalisedFrontPosition, colour = Algorithm)) + 
  # stat_ecdf(geom = 'step') +
  stat_myecdf() +
  scale_x_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
  scale_y_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
  scale_color_manual(values=c("#FF8900", "#0774A9")) +
  theme_bw()
ggsave(paste0("cdf_", d, "_annotated.pdf"), width=15, height=8, units='cm')

cdf.plt + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_text(size=16, color='black')) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=16, color='black')) +
  theme(legend.position = "none") 
ggsave(paste0("cdf_", d, ".pdf"), width=12, height=10, units='cm')





