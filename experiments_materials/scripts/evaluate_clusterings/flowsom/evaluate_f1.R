#########################################################################################
# R script to load and evaluate results for FlowSOM
#
# Adapted from: Lukas Weber, August 2016
# https://github.com/lmweber/cytometry-clustering-comparison
# 
# Givanna Putri, January 2020
#########################################################################################


library(flowCore)
library(clue)
library(rstudioapi)

# set working directory
dirname(rstudioapi::getActiveDocumentContext()$path)            # Finds the directory where this script is located
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))     # Sets the working directory to where the script is located
getwd()
PrimaryDirectory <- getwd()
PrimaryDirectory

# helper functions to match clusters and evaluate
source("helper_match_evaluate_multiple.R")

DATA_DIR <- "~/Documents/phd/code/ParetoBench/experiments_materials/flowsom"

datasets <- c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all")

for (dataset in datasets) {
  
  
  # to store the R data object containing the evaluation of FlowSOM result
  RDATA_DIR_FLOWSOM <- paste0(DATA_DIR, "/clusterings_qualities/R-data-eval/", dataset)
  dir.create(RDATA_DIR_FLOWSOM, recursive = TRUE)
  
  # to store the overall F1-score of FlowSOM result
  F1_DIR_FLOWSOM <- paste0(DATA_DIR, "/clusterings_qualities/F1-eval/", dataset)
  dir.create(F1_DIR_FLOWSOM, recursive = TRUE)
  
  # to store the cluster label mapping of FlowSOM result
  MAP_DIR_FLOWSOM <- paste0(DATA_DIR, "/clusterings_qualities/cluster-mapping/", dataset)
  dir.create(MAP_DIR_FLOWSOM, recursive = TRUE)
  
  RES_DIR_FLOWSOM <- paste0(DATA_DIR, "/raw_clusterings/", dataset)
  
  # which data sets required subsampling for this method (see parameters spreadsheet)
  is_subsampled <- c(FALSE)
  
  # alternate FlowCAP results at the end
  is_rare    <- c(FALSE)
  is_FlowCAP <- c(FALSE)
  n_FlowCAP <- 0
  
  
  
  
  ####################################################
  ### load truth (manual gating population labels) ###
  ####################################################
  
  # files with true population labels (subsampled labels if subsampling was required for
  # this method; see parameters spreadsheet)
  
  files_truth <- list()
  files_truth[[dataset]] = file.path(paste0("~/dropbox/pareto_bench/dataset/fcs_files/", dataset, ".fcs"))
  
  # extract true population labels
  
  clus_truth <- vector("list", length(files_truth))
  names(clus_truth) <- names(files_truth)
  
  for (i in 1:length(clus_truth)) {
    if (!is_subsampled[i]) {
      data_truth_i <- flowCore::exprs(flowCore::read.FCS(files_truth[[i]], transformation = FALSE, truncate_max_range = FALSE))
    } else {
      data_truth_i <- read.table(files_truth[[i]], header = TRUE, stringsAsFactors = FALSE)
    }
    clus_truth[[i]] <- data_truth_i[, "label"]
  }
  
  sapply(clus_truth, length)
  
  # cluster sizes and number of clusters
  # (for data sets with single rare population: 1 = rare population of interest, 0 = all others)
  
  tbl_truth <- lapply(clus_truth, table)
  
  tbl_truth
  sapply(tbl_truth, length)
  
  # store named objects (for other scripts)
  
  files_truth_FlowSOM <- files_truth
  clus_truth_FlowSOM <- clus_truth
  
  
  
  
  ############################
  ### load FlowSOM results ###
  ############################
  # list all csv files in the result directory
  params <- c(1:100)
  
  sapply(params, FUN = function(param_idx) {
    # load cluster labels
    # try one first
    files_out <- list()
    files_out[[dataset]] <- file.path(RES_DIR_FLOWSOM, paste0("Clustered_FlowSOM_Param", param_idx, ".csv"))
    
    clus <- lapply(files_out, function(f) {
      read.csv(f, header = TRUE)[, "FlowSOM_metacluster"]
    })
    
    sapply(clus, length)
    
    # cluster sizes and number of clusters
    # (for data sets with single rare population: 1 = rare population of interest, 0 = all others)
    
    tbl <- lapply(clus, table)
    
    tbl
    sapply(tbl, length)
    
    # contingency tables
    # (excluding FlowCAP data sets since population IDs are not consistent across samples)
    
    # for (i in 1:length(clus)) {
    #   if (!is_FlowCAP[i]) {
    #     print(table(clus[[i]], clus_truth[[i]]))
    #   }
    # }
    
    # store named objects (for other scripts)
    
    files_FlowSOM <- files_out
    clus_FlowSOM <- clus
    
    ###################################
    ### match clusters and evaluate ###
    ###################################
    
    # see helper function scripts for details on matching strategy and evaluation
    
    res <- vector("list", length(clus) + n_FlowCAP)
    names(res)[1:length(clus)] <- names(clus)
    names(res)[-(1:length(clus))] <- paste0(names(clus)[is_FlowCAP], "_alternate")
    
    for (i in 1:length(clus)) {
      if (!is_rare[i] & !is_FlowCAP[i]) {
        res[[i]] <- helper_match_evaluate_multiple(clus[[i]], clus_truth[[i]])
        
      } else if (is_rare[i]) {
        res[[i]] <- helper_match_evaluate_single(clus[[i]], clus_truth[[i]])
        
      } else if (is_FlowCAP[i]) {
        res[[i]]             <- helper_match_evaluate_FlowCAP(clus[[i]], clus_truth[[i]])
        res[[i + n_FlowCAP]] <- helper_match_evaluate_FlowCAP_alternate(clus[[i]], clus_truth[[i]])
      }
    }
    
    # store named object (for plotting scripts)
    save(res, file = paste0(RDATA_DIR_FLOWSOM, '/FlowSOM_Param', param_idx, '.RData'))
    
    # save F1-score as text
    write(res[[dataset]][["mean_F1"]], file = paste0(F1_DIR_FLOWSOM, '/FlowSOM_Param', param_idx, '.txt'))
    
    # save the mapping
    mapping <- data.frame(
      res[[dataset]][["labels_matched"]],
      c(1:length(res[[dataset]][["labels_matched"]])))
    names(mapping) <- c("FlowSOM_metacluster", "Population")
    write.csv(mapping, file = paste0(MAP_DIR_FLOWSOM, '/FlowSOM_Param', param_idx, '.csv'), 
              row.names = FALSE)
    print(paste0("DONE:", "Clustered_FlowSOM_Param", param_idx, ".csv"))
  })
  setwd(PrimaryDirectory)
  
  
}
