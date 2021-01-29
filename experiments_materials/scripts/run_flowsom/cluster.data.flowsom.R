# Cluster data using FlowSOM.
# FlowSOM is ran through Spectre package
# Spectre R package: https://sydneycytometry.org.au/spectre 
# by: Thomas Myles Ashhurst, Felix Marsh-Wakefield, Givanna Putri

##########################################################################################################
#### 1. Install packages, load packages, and set working directory
##########################################################################################################

### 1.1. Install 'Spectre' package (using devtools) and the dependencies that Spectre requires

## Install devtolls
if(!require('devtools')) {install.packages('devtools')}
library('devtools')

## Install Spectre
#install_github("sydneycytometry/spectre")
install_github("sydneycytometry/spectre", ref = 'development') # option to install the development verison if required
library("Spectre")

## Install BiocManager to download packages from Bioconductor
if (!requireNamespace("BiocManager", quietly = TRUE)){install.packages("BiocManager")}

## Download additional BioConductor packages
if(!require('flowCore')) {BiocManager::install('flowCore')}
if(!require('Biobase')) {BiocManager::install('Biobase')}
if(!require('flowViz')) {BiocManager::install('flowViz')}
if(!require('FlowSOM')) {BiocManager::install('FlowSOM')}

### 1.2. Load packages

library(Spectre)
Spectre::check.packages() # --> change so that message at the end is "All required packages have been successfully installed"
Spectre::load.packages() # --> change so that message at the end is "All required packages have been successfully loaded"

session_info()

### 1.3. Set number of threads for data.table functions

getDTthreads()

### 1.4. Set working directory

## Set working directory
dirname(rstudioapi::getActiveDocumentContext()$path)            # Finds the directory where this script is located
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))     # Sets the working directory to where the script is located
getwd()
PrimaryDirectory <- getwd()
PrimaryDirectory

##########################################################################################################
#### 2. Read and prepare data
##########################################################################################################

### Read SAMPLES (data) into workspace and review

## List of CSV files in PrimaryDirectory # HERE WE WANT ONE FILE PER SAMPLE
list.files(PrimaryDirectory, ".csv")

## Import samples (read files into R from disk)
data.list <- Spectre::read.files(file.loc = PrimaryDirectory,
                                 file.type = ".csv",
                                 do.embed.file.names = TRUE)

## Some checks
ncol.check    # Review number of columns (features, markers) in each sample
nrow.check    # Review number of rows (cells) in each sample
name.table    # Review column names and their subsequent values

head(data.list)
head(data.list[[1]])

## Save starting data
data.start <- data.list

head(data.list)

### Merge files

## Merge files and review
cell.dat <- Spectre::file.merge(x = data.list)

str(cell.dat)
head(cell.dat)
dim(cell.dat)

## Are there any NAs present in cell.dat? Yes if 'TRUE', no if 'FALSE'
any(is.na(cell.dat))

## Cleanup (not necessary, but recommended)
rm(data.list, data.start, ncol.check, nrow.check, all.file.names, all.file.nums)

##########################################################################################################
#### 3. Define data and sample variables for analysis
##########################################################################################################

### Define key columns

as.matrix(names(cell.dat))

## Define key columns that might be used or dividing data (samples, groups, batches, etc)
# exp.name <- "FlowSOMExp"

file.col <- "Filename"
sample.col <- "Sample"
group.col <- "Group"
batch.col <- "Batch"

## Create a list of column names
ColumnNames <- as.matrix(unname(colnames(cell.dat))) # assign reporter and marker names (column names) to 'ColumnNames'
ColumnNames

### Define columns for clustering

## Define columns that are 'valid' cellular markers (i.e. not live/dead, blank channels etc)
ColumnNames
ClusteringColNos <- c(1:13)
ClusteringCols <- ColumnNames[ClusteringColNos] # e.g. [c(11, 23, 10)] to include the markers corresponding to the column numbers 11, 23, 10

ClusteringCols  # check that the column names that appear are the ones you want to analyse
ColumnNames[-ClusteringColNos] # Check which columns are being EXCLUDED!

### Checks

head(cell.dat)
ClusteringCols

##########################################################################################################
#### 4. Perform clustering
##########################################################################################################
OutputDirectory <- "Output_CAPX_seed32"
dir.create(OutputDirectory)
setwd(OutputDirectory)
dir.create("Output-data")
setwd(PrimaryDirectory)

## Back up the data
cell.dat.bk <- cell.dat

### Run FlowSOM
source("run.flowsom.R")

params <- read.csv("lhc_parameters/LHC_Parameters_for_Runs.csv")

cluster <- function(row.index, cell.dat.input) {
  print(paste("Building", row.index))
  param <- params[row.index, ]
  exp.name <- paste0("FlowSOM_Param",row.index) 
  cell.dat <- cell.dat.input
  cell.dat <- run.flowsom(x = cell.dat,
                          clust.seed = 32,
                          meta.seed = 32,
                          clustering.cols = ClusteringCols,
                          meta.k = as.integer(param["num_cluster"]),
                          xdim = as.integer(param["xdim"]),
                          ydim = as.integer(param["ydim"]))
    
  
  ##########################################################################################################
  #### 6. Save data to disk
  ##########################################################################################################
  
  ### Save data (cell.dat) including clustering results
  setwd(OutputDirectory)
  # dir.create("Output-data")
  setwd("Output-data")
  
  # head(cell.dat)
  
  ## Write the clusters only
  Spectre::write.files(x = cell.dat[, c("FlowSOM_cluster", 'FlowSOM_metacluster')],
                       file.prefix= paste0("Clustered_", exp.name), # required
                       write.csv = TRUE,
                       write.fcs = FALSE)
  
  setwd(PrimaryDirectory)
  
  
}
param.count <- c(1:nrow(params))

library(parallel)
mclapply(param.count, FUN = cluster, mc.cores = 4, cell.dat.input = cell.dat.bk)



