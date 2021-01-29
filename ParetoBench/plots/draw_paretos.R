draw_cdf <- function(dataset, colours = NULL, blank_axis=FALSE, save_to_disk=TRUE, 
                     img_width=15, img_height=8,
                     file_extension = c("pdf", "png")) {
  
  require(ggplot2)
  
  file_extension <- match.arg(file_extension)
  
  dat <- read.csv(paste0("front_positions_", dataset, ".csv"))
  cdf.plt <- ggplot(dat, aes(NormalisedFrontPosition, colour = Algorithm)) + 
    stat_myecdf() +
    scale_x_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
    scale_y_continuous(breaks = round(seq(0, 1, by = 0.2),1)) +
    ylab("Cumulative Distribution") +
    xlab("Normalised Front Positions") + 
    theme_bw()
    
  if (!is.null(colours)) {
    cdf.plt <- cdf.plt + scale_color_manual(values=colours)
  }
  
  if (blank_axis) {
    cdf.plt <- cdf.plt + 
      theme(axis.title.x = element_blank()) +
      theme(axis.title.y = element_blank()) +
      theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
      theme(axis.text.y = element_blank()) +
      theme(legend.position = "none") 
  }
  
  if (save_to_disk) {
    filename = paste0("cdf_", dataset, ".", file_extension)
    if (blank_axis) {
      filename = paste0("cdf_blank", dataset, ".", file_extension)
    }
    ggsave(plot = cdf.plt, filename = filename, width=img_width, height=img_height, units='cm')
  }
  print(cdf.plt)
}

draw_swarm <- function(dataset, colours = NULL, blank_axis=FALSE, save_to_disk=TRUE, img_width=12, img_height=10,
                       use_quasi_random = FALSE, dot_size=1.0, file_extension = c("pdf", "png")) {
  
  require(ggbeeswarm)
  require(ggplot2)
  
  file_extension <- match.arg(file_extension)
  
  dat <- read.csv(paste0("front_positions_", dataset, ".csv"))
  dat$Algorithm <- as.factor(dat$Algorithm)
  
  swarm.plt <- ggplot(dat, aes(x=Algorithm, y=FrontPosition, color=Algorithm))
  
  if (use_quasi_random) {
    swarm.plt <- swarm.plt + geom_quasirandom(size=dot_size)
  } else {
    swarm.plt <- swarm.plt + geom_beeswarm(size=dot_size, cex=1.5)
  }
  swarm.plt <- swarm.plt +
    # facet_grid(~Algorithm) +
    ylab("Front Positions") + 
    xlab("Algorithm") +
    theme_bw()
  
  if (!is.null(colours)) {
    swarm.plt <- swarm.plt + scale_color_manual(values=colours)
  }
  
  if (blank_axis) {
    swarm.plt <- swarm.plt + 
      theme(axis.title.x = element_blank()) +
      theme(axis.title.y = element_blank()) +
      theme(axis.text.x = element_blank()) +  # Turn off tick label titles.
      theme(axis.text.y = element_blank()) +
      theme(legend.position = "none") 
  }
  
  if (save_to_disk) {
    filename = paste0("swarm_", dataset, ".", file_extension)
    if (blank_axis) {
      filename = paste0("swarm_blank", dataset, ".", file_extension)
    }
    ggsave(plot = swarm.plt, filename = filename, width=img_width, height=img_height, units='cm')  
  }
  print(swarm.plt)
}