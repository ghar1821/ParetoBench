## See: https://github.com/tidyverse/ggplot2/issues/1467

stat_myecdf <- function(mapping = NULL, data = NULL, geom = "step",
                        position = "identity", n = NULL, na.rm = FALSE,
                        show.legend = NA, inherit.aes = TRUE, direction="vh", ...) {
  layer(
    data = data,
    mapping = mapping,
    stat = StatMyecdf,
    geom = geom,
    position = position,
    show.legend = show.legend,
    inherit.aes = inherit.aes,
    params = list(
      n = n,
      na.rm = na.rm,
      direction=direction,
      ...
    )
  )
}

StatMyecdf <- ggproto("StatMyecdf", Stat,
                      compute_group = function(data, scales, n = NULL) {
                        
                        # If n is NULL, use raw values; otherwise interpolate
                        if (is.null(n)) {
                          # Dont understand why but this version needs to sort the values
                          xvals <- sort(unique(data$x))
                        } else {
                          xvals <- seq(min(data$x), max(data$x), length.out = n)
                        }
                        
                        y <- ecdf(data$x)(xvals)
                        x1 <- max(xvals)
                        y0 <- 0                      
                        data.frame(x = c(xvals, x1), y = c(y0, y))
                      },
                      
                      default_aes = aes(y = ..y..),
                      
                      required_aes = c("x")
)
