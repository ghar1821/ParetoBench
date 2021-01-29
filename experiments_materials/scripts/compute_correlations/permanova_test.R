library(vegan)
library(data.table)

setwd("~/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/spearman_scores/")

# read data into data frame
algorithms <- c('chronoclust', 'flowsom', 'phenograph')
data <- lapply(algorithms, function(alg) {
  dat <- fread(paste0(alg, '/spearman_score_per_dataset.csv'))
  dat[, algorithm:=alg]
  return(dat)
})

dat <- rbindlist(data)
# combine the metric 1 and 2 columns into 1
dat[,metrics:=paste(Metric1, Metric2, sep = ' vs ')]

# check the data frame is ok
head(dat)
tail(dat)
as.matrix(names(dat))

### PERMANOVA TEST
## Dataset is not significant. So we remove in the next test
res.permanova <- adonis(
    CorrelationCoefficient ~ metrics + Dataset + algorithm + metrics:Dataset + metrics:algorithm + Dataset:algorithm, 
    data = dat, 
    method="euclidean")

sink("permanova.txt")
print(res.permanova)
sink()





