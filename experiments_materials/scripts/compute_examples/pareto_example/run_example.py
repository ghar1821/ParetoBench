import pandas as pd

from ParetoBench.analyse_pareto import normalise_fronts_and_compare
from ParetoBench.compare import count_proportion_of_solutions_on_each_front, create_summary

if __name__ == '__main__':
  dat = pd.read_csv("data/pareto_example.csv")

  # The following is essentially direct copy of compare method but without running the pareto front algorithm
  ks_score, norm_dat = normalise_fronts_and_compare(dat)

  norm_dat.to_csv('output/pareto_example/front_positions.csv', index=False)
  ks_score.to_csv('output/pareto_example/ks_pareto.csv', index=False)

  count_solution_per_front = count_proportion_of_solutions_on_each_front(norm_dat)
  count_solution_per_front.to_csv('output/pareto_example/proportion_solutions_per_front.csv', index=False)

  front_limits = [0.2, 0.4]
  summary_dataset = create_summary(norm_dat, front_limits)
  summary_dataset.to_csv('output/pareto_example/summary.csv', index=False)
