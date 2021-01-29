# Import the packages
library(spartan)
library(rstudioapi)
# The folder where the parameter samples should be output to
FILEPATH <- dirname(rstudioapi::getActiveDocumentContext()$path)
# Names of the parameters to generate values for.
PARAMETERS <- c("num_cluster", "grid_size")
# The number of parameter sample sets to create using the hypercube
NUMSAMPLES <- 100
# The minimum value in the range for each parameter
PMIN <- c(24, 10)
# The maximum value in the range for each parameter
PMAX <- c(72, 30)
# The increment value that should be applied for each parameter
PINC <- c(1, 1)
# Algorithm to use to generate the hypercube. Can be normal (quick) or optimal,
# which can take a long time (especially for high number of parameters)
ALGORITHM <- "optimal"
sample<-lhc_generate_lhc_sample(FILEPATH, PARAMETERS, NUMSAMPLES, PMIN, PMAX, ALGORITHM, PINC)

