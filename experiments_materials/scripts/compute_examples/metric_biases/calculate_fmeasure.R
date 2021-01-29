# for calculating F-measure of examples in paper
dirname(rstudioapi::getActiveDocumentContext()$path)            # Finds the directory where this script is located
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))     # Sets the working directory to where the script is located
getwd()
source('helper_match_evaluate_multiple.R')

# perfect, over, and under clustering
clus_truth <- vector("list", 3)
names(clus_truth) <- c('perfect', 'over', 'under')
# 1=sun, 2=tree, 3=bone
clus_truth[['perfect']] <- c(1,1,1,1,1,2,2,2,2,3,3,3,3)
clus_truth[['over']] <- c(1,1,1,1,1,2,2,2,2,3,3,3,3)
clus_truth[['under']] <- c(1,1,1,1,1,2,2,2,2,3,3,3,3)

clus <- vector("list", 3)
names(clus) <- c('perfect', 'over', 'under')
clus[['perfect']] <- c(1,1,1,1,1,2,2,2,2,3,3,3,3)
clus[['over']] <- c(1,1,4,4,4,2,2,5,5,3,3,6,6)
clus[['under']] <- c(1,1,1,1,1,2,2,2,2,1,1,2,2)

res <- vector("list", 3)
names(res)[1:length(clus)] <- names(clus)
for (i in 1:length(clus)) {
  res[[i]] <- helper_match_evaluate_multiple(clus[[i]], clus_truth[[i]])
}

### to ensure that F-measure capture clustering that poorly captures rare items
clus_truth <- vector("list", 1)
names(clus_truth) <- c('poor')
# 1=B cell, 2=PDC
clus_truth[['poor']] <- c(rep(1,10000), rep(2,10))

for (x in 0:10) {
  clus <- vector("list", 1)
  names(clus) <- c('poor')
  clus[['poor']] <- c(rep(1,9950), rep(2,50), rep(1,10-x), rep(2,0+x))
  
  res <- vector("list", 1)
  names(res)[1:length(clus)] <- names(clus)
  for (i in 1:length(clus)) {
    res[[i]] <- helper_match_evaluate_multiple(clus[[i]], clus_truth[[i]])
  }
  print(x)
  print(res$poor$labels_matched)
  print(paste(res$poor$mean_pr, res$poor$mean_re, res$poor$mean_F1))
  
}



### to find bias in mapping
clus_truth <- vector("list", 2)
names(clus_truth) <- c('scenario1', 'scenario2')
# 1=B cell, 2=T cell
clus_truth[['scenario1']] <- c(rep(1, 13), rep(2, 13))
clus_truth[['scenario2']] <- c(rep(1, 13), rep(2, 13))

clus <- vector("list", 2)
names(clus) <- c('scenario1', 'scenario2')
clus[['scenario1']] <- c(rep(1,5), rep(2,8), rep(1,4), rep(3,3), rep(4,4), rep(5,2))
clus[['scenario2']] <- c(rep(1,2), rep(2,1), rep(3,2), rep(4,3), rep(5,1), rep(6,4),
                         rep(2,1), rep(5,1), rep(7,3), rep(8,2), rep(9,2), rep(10,2),	rep(11,2))

res <- vector("list", 2)
names(res)[1:length(clus)] <- names(clus)
for (i in 1:length(clus)) {
  res[[i]] <- helper_match_evaluate_multiple(clus[[i]], clus_truth[[i]])
}
