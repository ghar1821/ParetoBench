#########################################################################################
# R script to load and evaluate results for ChronoClust

# Adapted from: Lukas Weber, August 2016
# https://github.com/lmweber/cytometry-clustering-comparison
# 
# Givanna Putri, January 2020
#########################################################################################

library(flowCore)
library(clue)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# helper functions to match clusters and evaluate
source("helper_match_evaluate_multiple.R")

datasets <- c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all")
for (dataset in datasets) {
  
  work_dir <- "~/Documents/phd/code/ParetoBench/experiments_materials/chronoclust"
  RES_DIR_CHRONOCLUST <- paste0(work_dir, '/raw_clusterings/', dataset)
  

  RDATA <- paste0(work_dir, "/clusterings_qualities/R-data-eval/", dataset)
  OUT_DIR <- paste0(work_dir, "/clusterings_qualities/F1-eval/", dataset)
  MAPPING_DIR <- paste0(work_dir, "/clusterings_qualities/cluster-mapping/", dataset)
  
  dir.create(RDATA, recursive = TRUE)
  dir.create(OUT_DIR, recursive = TRUE)
  dir.create(MAPPING_DIR, recursive = TRUE)
  
  # which data sets required subsampling for this method (see report)
  is_subsampled <- c(FALSE)
  
  # alternate FlowCAP results at the end
  is_rare <- c(FALSE)
  is_FlowCAP <- c(FALSE)
  n_FlowCAP <- 0
  
  
  
  
  ####################################################
  ### load truth (manual gating population labels) ###
  ####################################################
  
  # files with true population labels (subsampled labels if subsampling was required for
  # this method; see report)
  
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
  
  # tbl_truth
  # sapply(tbl_truth, length)
  
  # store named objects (for other scripts)
  
  files_truth_chronoclust <- files_truth
  clus_truth_chronoclust <- clus_truth
  
  ###############################
  ### load chronoclust results ###
  ###############################
  
  # load cluster labels
  
  params <- c(0:99)
  
  # find params that have clusters
  params_with_cluster <- sapply(params, function(param) {
    clus_label_file <- paste0(param, "_clusters.txt")
    
    files_out <- list()
    files_out[[dataset]] <- file.path(RES_DIR_CHRONOCLUST, clus_label_file)
    
    clus <- lapply(files_out, function(f) {
      read.table(f, header = TRUE, stringsAsFactors = FALSE)[, "label"]
    })
    
    # remove noise clusters
    # reset the truth first
    clus_truth <- clus_truth_chronoclust
    #assigned <- which(clus[["Levine_13dim"]] != 0)
    #clus[["Levine_13dim"]] <- clus[["Levine_13dim"]][assigned]
    #clus_truth[["Levine_13dim"]] <- clus_truth[["Levine_13dim"]][assigned]
    
    # map the data
    if (length(clus[[dataset]]) != 0) {
      # sapply(clus, length)
      
      # cluster sizes and number of clusters
      # (for data sets with single rare population: 1 = rare population of interest, 0 = all others)
      
      tbl <- lapply(clus, table)
      
      # tbl
      # sapply(tbl, length)
      
      # store named objects (for other scripts)
      
      files_chronoclust <- files_out
      clus_chronoclust <- clus
      
      
      print(paste0("Mapping sample ", param))
      
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
      
      res_chronoclust <- res
      
      saveRDS(res_chronoclust, file=paste0(RDATA, "/", param, "_res_chronoclust.RData"))
      
      # write out mean scores
      score <- data.frame(character(3), numeric(3), stringsAsFactors = FALSE)
      score[1,1] <- as.character("F1")
      score[2,1] <- as.character("Precision")
      score[3,1] <- as.character("Recall")
      score[1,2] <- res[[dataset]][["mean_F1"]]
      score[2,2] <- res[[dataset]][["mean_pr"]]
      score[3,2] <- res[[dataset]][["mean_re"]]
      names(score) <- c("Type", "Value")
      write.csv(score, file=paste0(OUT_DIR, "/", param, "_score.csv"))
      
      # write out scores per population
      populations <- names(res[[dataset]][['F1']])
      num_population <- length(populations)
      scores <- data.frame(Population=character(num_population), 
                           F1=numeric(num_population), 
                           Precision=numeric(num_population),
                           Recall=numeric(num_population))
      scores['Population'] <- populations
      scores['F1'] <- res[[dataset]][['F1']]
      scores['Precision'] <- res[[dataset]][['pr']]
      scores['Recall'] <- res[[dataset]][['re']]
      write.csv(scores, file=paste0(OUT_DIR, "/", param, "_score_per_population.csv"))
      
      # write out the mapping
      mapping <- data.frame(Population=character(num_population),
                            Cluster=character(num_population))
      mapping['Population'] <- populations
      mapping['Cluster'] <- res_chronoclust[[dataset]][["labels_matched"]]
      write.csv(mapping, file=paste0(MAPPING_DIR, "/", param, "_mapping.csv"))
      
      
      return(param)
    } else {
      return(-1)
    }
  })
}
