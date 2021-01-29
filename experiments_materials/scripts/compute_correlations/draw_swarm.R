library(ggbeeswarm)
library(data.table)

setwd("~/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/spearman_scores/")

algorithms <- c('chronoclust', 'flowsom', 'phenograph')
data <- lapply(algorithms, function(alg) {
  dat <- fread(paste0(alg, '/spearman_score_per_dataset.csv'))
  dat[, algorithm:=alg]
  return(dat)
})

dat <- rbindlist(data)
# combine the metric 1 and 2 columns into 1
dat[, metrics:=paste(Metric1, Metric2, sep = ' vs ')]

# check the data frame is ok
head(dat)
tail(dat)
as.matrix(names(dat))

## Swarm plots ----

dir.create("swarm_plots")
setwd("swarm_plots")
# for metrics ----
p <- ggplot2::ggplot(dat, aes(x=metrics, y=CorrelationCoefficient)) +
  geom_beeswarm(cex=2.5, priority='density', dodge.width=1.0, size=2, color="#9F3548") + 
  # ylim(0.5, 1.0) +
  theme_bw() + 
  theme(legend.position = "none", axis.text.x = element_text(angle=45, vjust = 1, hjust=1)) 
ggsave("rs_metrics_annotated.pdf", width=15, height=8, units='cm')

# Version for the paper, detailed added in illustrator. 
p + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=14))
ggsave("rs_metrics.pdf", width=15, height=8, units='cm')

# for datasets ----
p <- ggplot2::ggplot(dat, aes(x=Dataset, y=CorrelationCoefficient)) +
  geom_beeswarm(cex=2.5, priority='density', dodge.width=1.0, size=2, color="#3b55ff") + 
  # ylim(0.5, 1.0) +
  theme_bw() + 
  theme(legend.position = "none", axis.text.x = element_text(angle=45, vjust = 1, hjust=1)) 
ggsave("rs_dataset_annotated.pdf", width=15, height=8, units='cm')

# Version for the paper, detailed added in illustrator. 
p + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=14))
ggsave("rs_dataset.pdf", width=15, height=8, units='cm')

# for algorithm ----
p <- ggplot2::ggplot(dat, aes(x=algorithm, y=CorrelationCoefficient)) +
  geom_beeswarm(cex=2.5, priority='density', dodge.width=1.0, size=2, color="#4E9231") + 
  # ylim(0.5, 1.0) +
  theme_bw() +
  theme(legend.position = "none", axis.text.x = element_text(angle=45, vjust = 1, hjust=1)) 
ggsave("rs_algo_annotated.pdf", width=10, height=8, units='cm')

# Version for the paper, detailed added in illustrator. 
p + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=14))
ggsave("rs_algo.pdf", width=15, height=8, units='cm')

# for metrics/algorithm ----
# combine the metric and algorithm columns into 1
dat.comb <- data.table::copy(dat)
dat.comb[, metrics_algorithm:=paste(metrics, algorithm, sep = ' | ')]
head(dat.comb)
as.matrix(names(dat.comb))

p <- ggplot2::ggplot(dat.comb, aes(x=metrics_algorithm, y=CorrelationCoefficient, shape=algorithm,
                                   color=algorithm)) +
  # geom_beeswarm(cex=2.5, priority='density', dodge.width=0.1, size=2) + 
  geom_quasirandom(cex=2.5, dodge.width=0.1) + 
  # ylim(0.5, 1.0) +
  theme_bw() +
  scale_color_manual(values=c("#2A4D6E", "#AA7C39", "#3be351")) + 
  theme(legend.position = "none", axis.text.x = element_text(angle=45, vjust = 1, hjust=1)) 
ggsave("rs_algo_metrics_annotated.pdf", width=20, height=15, units='cm')

# Version for the paper, detailed added in illustrator. 
p + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=14))
ggsave("rs_algo_metrics.pdf", width=15, height=8, units='cm')

# Combine dataset and algorithm into 1 ----
dat.comb.2 <- data.table::copy(dat)
dat.comb.2[, dataset_algorithm:=paste(Dataset, algorithm, sep = ' | ')]
head(dat.comb.2)
as.matrix(names(dat.comb.2))
p <- ggplot2::ggplot(dat.comb.2, aes(x=dataset_algorithm, y=CorrelationCoefficient, shape=algorithm,
                                   color=algorithm)) +
  # geom_beeswarm(cex=2.5, priority='density', dodge.width=1.0, size=2) + 
  geom_quasirandom(cex=2.5, dodge.width=0.1) + 
  # ylim(0.5, 1.0) +
  theme_bw() +
  scale_color_manual(values=c("#84B925", "#A22065", "#0b12db")) + 
  theme(legend.position = "none", axis.text.x = element_text(angle=45, vjust = 1, hjust=1)) 
ggsave("rs_algo_dataset_annotated.pdf", width=20, height=15, units='cm')

# Version for the paper, detailed added in illustrator. 
p + theme(axis.title.x = element_blank()) +
  theme(axis.title.y = element_blank()) +
  theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
  theme(axis.text.y = element_text(size=14))

ggsave("rs_algo_dataset.pdf", width=15, height=8, units='cm')
