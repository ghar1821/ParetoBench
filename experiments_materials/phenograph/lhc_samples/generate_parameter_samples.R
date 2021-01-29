# Import the packages
library(spartan)
library(rstudioapi)

setwd(FILEPATH)

datasets = c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all")
min_k = c(5, 7, 5, 6)
max_k = c(80, 250, 80, 80)

# The folder where the parameter samples should be output to
FILEPATH <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Names of the parameters to generate values for.
PARAMETERS <- c("k")
# The number of parameter sample sets to create using the hypercube
NUMSAMPLES <- 100

# The increment value that should be applied for each parameter
PINC <- c(1)

# Algorithm to use to generate the hypercube. Can be normal (quick) or optimal,
# which can take a long time (especially for high number of parameters)
ALGORITHM <- "optimal"

for (i in c(1:length(datasets))) {
  # The minimum value in the range for each parameter
  PMIN <- c(min_k[i])
  # The maximum value in the range for each parameter
  PMAX <- c(max_k[i])
  
  dataset = datasets[i]
  
  lhc_generate_lhc_sample(FILEPATH, PARAMETERS, NUMSAMPLES, PMIN, PMAX, ALGORITHM, PINC)
  file.rename(from = "LHC_Parameters_for_Runs.csv", to = paste0("LHC_", dataset, ".csv"))
}



