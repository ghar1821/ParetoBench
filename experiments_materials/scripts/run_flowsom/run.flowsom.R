#' run.flowsom
#' Adapted from Spectre's run.flowsom
#' Spectre R package: https://sydneycytometry.org.au/spectre 
#'
#' @usage run.flowsom(x, ...)
#'
#' @param x data.frame. Input sample. No default.
#' @param clustering.cols Vector of column names to use for clustering. It is possible to use a vector of column numbers here but this is not recommended, as No default.
#' @param meta.k Numeric. Number of clusters to create. DEFAULT = 20.
#' @param xdim Numeric. Number of first level clusters across the x-axis. xdim x ydim = total number of first level FlowSOM clusters. DEFAULT = 10.
#' @param ydim Numeric. Number of first level clusters across the y-axis. xdim x ydim = total number of first level FlowSOM clusters. DEFAULT = 10.
#' @param clust.seed Numeric. Clustering seed for reproducibility. DEFAULT = 42
#' @param meta.seed Numeric. Metaclustering seed for reproducibility. DEFAULT = 42.
#' @param clust.name Character. Name of the resulting 'cluster' parameter. DEFAULT = "FlowSOM_cluster".
#' @param meta.clust.name Character. Name of the resulting 'metacluster' parameter. DEFAULT = "FlowSOM_metacluster".
#'
#' This function runs FlowSOM on a dataframe with cells (rows) vs markers (columns), and returns 'res' with result columns
#'
#' @export

run.flowsom <- function(x,
                        clustering.cols, # names of columns to cluster
                        meta.k = 20,
                        xdim = 10,
                        ydim = 10,
                        clust.seed = 42,
                        meta.seed = 42,
                        clust.name = "FlowSOM_cluster",
                        meta.clust.name = "FlowSOM_metacluster")
{
  
  ## Remove non-numeric
  head
  x.start <- x
  
  nums <- unlist(lapply(x, is.numeric))
  x <- x[ , nums, with=FALSE]
  x <- x[,clustering.cols, with = FALSE]
  
  ## Create FCS file metadata - column names with descriptions
  metadata <- data.frame(name=dimnames(x)[[2]], desc=paste('column',dimnames(x)[[2]],'from dataset'))
  
  ## Create flowframe with data
  x.ff <- new("flowFrame",
              exprs=as.matrix(x), # in order to create a flow frame, data needs to be read as matrix
              parameters=AnnotatedDataFrame(metadata))
  
  head(exprs(x.ff))
  
  x_FlowSOM <- x.ff
  
  # choose markers for FlowSOM analysis
  FlowSOM_cols <- clustering.cols
  
  ### 4.3. - Run FlowSOM
  
  ## set seed for reproducibility
  set.seed(clust.seed)
  
  ## run FlowSOM (initial steps prior to meta-clustering)
  FlowSOM_out <- FlowSOM::ReadInput(x_FlowSOM, transform = FALSE, scale = FALSE)
  
  FlowSOM_out <- FlowSOM::BuildSOM(FlowSOM_out,
                                   colsToUse = FlowSOM_cols,
                                   xdim = xdim,
                                   ydim = ydim)
  
  FlowSOM_out <- FlowSOM::BuildMST(FlowSOM_out)
  
  ## extract cluster labels (pre meta-clustering) from output object
  labels_pre <- FlowSOM_out$map$mapping[, 1]
  labels_pre
  length(labels_pre)
  nrow(x)
  
  flowsom.res.original <- labels_pre
  
  ## run meta-clustering
  FlowSOM_out_meta <- FlowSOM::metaClustering_consensus(FlowSOM_out$map$codes, k = meta.k, seed = meta.seed)
  
  ## extract META (?) cluster labels from output object
  labels <- FlowSOM_out_meta[labels_pre]
  
  ## summary of cluster sizes and number of clusters
  table(labels)
  length(table(labels))
  
  ## save ORIGINAL cluster labels
  flowsom.res.original <- data.frame("labels_pre" = labels_pre)
  colnames(flowsom.res.original)[grepl('labels_pre',colnames(flowsom.res.original))] <- clust.name
  
  dim(x)
  dim(flowsom.res.original)
  head(flowsom.res.original)
  
  ## save META cluster labels
  flowsom.res.meta <- data.frame("labels" = labels)
  colnames(flowsom.res.meta)[grepl('labels',colnames(flowsom.res.meta))] <- meta.clust.name
  
  dim(x)
  dim(flowsom.res.meta)
  head(flowsom.res.meta)
  
  x.start <- cbind(x.start, flowsom.res.original)   # Add results to x
  x.start <- cbind(x.start, flowsom.res.meta)       # Add results to x
  
  return(x.start)
  
}

