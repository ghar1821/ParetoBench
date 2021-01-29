library(ggplot2)
library(data.table)

setwd("~/Documents/phd/code/ParetoBench/experiments_materials/compute_correlations/best_param_per_metric/")

dat_files = list.files(pattern = ".csv")

dat = lapply(dat_files, function(f) {
  data = fread(f)
  data$algorithm = f
  return(data)
})

dat = rbindlist(dat)
metrics = unique(dat$best_metric_by)
dat_best = lapply(metrics, function(met) {
  return(dat[dat$best_metric_by == met,])
})
names(dat_best) = metrics
dat_best_melt = lapply(metrics, function(met) {
  dat_met = dat_best[[met]]
  
  measure_vars = met
  if (met == 'v_measure') {
    measure_vars = "vmeasure"
  }
  
  dat_melt = melt(dat_met, id.vars = c('dataset', 'algorithm'),
                     measure.vars = c(measure_vars),
                     variable.name = 'metric',
                     value.name = 'score')
})
dat_melt = rbindlist(dat_best_melt)

dat_dataset_mapping = data.table(dataset=c("Levine_13dim", "Levine_32dim", "Samusik_01", "Samusik_all"),
                                 abbrv=c("L13", "L32", "S01", "SA"))
dat_metric_mapping = data.table(metric=c('accuracy', 'ari', 'f1', 'vmeasure'),
                                mapping=c('Accuracy', 'ARI', 'F1-score', 'V-measure'))

dat_melt[dat_dataset_mapping, dataset_abbrv := abbrv, on = c(dataset="dataset")]
dat_melt[dat_metric_mapping, metric_name := mapping, on = c(metric="metric")]
dat_melt$metric_name = factor(dat_melt$metric_name, levels=c('F1-score', 'Accuracy', 'ARI', 'V-measure'))

ggplot(dat_melt, aes(x=dataset_abbrv, y=score))+
  geom_bar(aes(fill=algorithm), position = "dodge", stat='identity') +
  facet_wrap(~metric_name,  ncol=4) +
  scale_y_continuous(breaks = scales::pretty_breaks(n = 5)) +
  scale_fill_manual(values=c("#ff653b", "#3b55ff", "#3cc23a")) +
  theme(axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        axis.text.x = element_text(size=16, color='black'),
        axis.text.y = element_text(size=16, color='black'),
        strip.text.x = element_text(size = 16, colour = "black"),
        legend.position = "bottom") 
ggsave("bar_best_metric_withLegend.png")

ggplot(dat_melt, aes(x=dataset_abbrv, y=score))+
  geom_bar(aes(fill=algorithm), position = "dodge", stat='identity') +
  facet_wrap(~metric_name,  ncol=4) +
  scale_y_continuous(breaks = scales::pretty_breaks(n = 5)) +
  scale_fill_manual(values=c("#ff653b", "#3b55ff", "#3cc23a")) +
  scale_color_manual(values=c('black', 'white', 'black')) +
  theme(axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        axis.text.x = element_text(size=16, color='black'),
        axis.text.y = element_text(size=16, color='black'),
        strip.text.x = element_text(size = 16, colour = "black"),
        legend.position = "none") 
ggsave("bar_best_metric_noLegend.png", limitsize = FALSE, dpi=1200,
       height = 3, width=15)

