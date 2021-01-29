# Import the packages
library(spartan)
# The folder where the parameter samples should be output to
FILEPATH <- "/Users/givanna/Dropbox (Sydney Uni)/lweber_dataset/analysis_post_SA/Samusik_all/lhc_parameters"
# Names of the parameters to generate values for.
PARAMETERS <- c("upsilon","epsilon", "delta")
# The number of parameter sample sets to create using the hypercube
NUMSAMPLES <- 100
# The minimum value in the range for each parameter
PMIN <- c(2, 0.443, 0.002)
# The maximum value in the range for each parameter
PMAX <- c(4, 0.573, 0.07)
# Algorithm to use to generate the hypercube. Can be normal (quick) or optimal,
# which can take a long time (especially for high number of parameters)
ALGORITHM <- "optimal"
sample<-lhc_generate_lhc_sample(FILEPATH, PARAMETERS, NUMSAMPLES, PMIN, PMAX, ALGORITHM)
