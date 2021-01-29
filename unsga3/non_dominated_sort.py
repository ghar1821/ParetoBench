"""
Implements Fortin et al's 2013 Non-Dominated Sorting algortihm,
"Generalizing the improved run-time complexity algorithm for non-dominated sorting"
published in Proceedings of the 15th Annual Conference on Genetic and Evolutionary Computation 2013.
"""
import statistics
from collections import defaultdict

__author__ = 'Mark N. Read'


def non_dominated_sort(population):
    """
    Sort *individuals* in pareto non-dominated fronts using the Generalized
    Reduced Run-Time Complexity Non-Dominated Sorting Algorithm presented by
    Fortin et al. (2013).

    k is the number of objectives under active consideration.

    :param: individuals, a list of unsga3.Candidate objects.
    :returns: A list of Pareto fronts (lists), with the first list being the leading Pareto front.
    """
    if len(population) == 0:
        return []

    # obtain set of unique fitnesses (dictionary keys) and collect individuals possessing each fitness in a list
    # (values). Once fitnesses are assigned into fronts, this is used to link back to individuals.
    fitness_candidates_map = defaultdict(list)
    for candidate in population:
        fitness_candidates_map[candidate.fitness].append(candidate)  # multiple candidates can share a fitness

    number_of_objectives = len(population[0].fitness)
    fitnesses = fitness_candidates_map.keys()
    # each fitness is assigned a front ID, with zero being the leading (Pareto) front. Default to zero, incremented
    # later
    fitness_front_assignments = dict.fromkeys(fitnesses, 0)
    # in-place sorting, lexicographic by default [first item, then second if first ==, etc].
    fitnesses = sorted(fitnesses)

    if number_of_objectives > 1:
        """ this handles case of 2 or more objectives, but does not generalise to uses of U-NSGA-III for single
        objective optimisation; yet this flexibility is an explicit motivation for that algorithm. """
        nd_helper_A(fitnesses, number_of_objectives, fitness_front_assignments)
    else:
        """
        case if there is a single objective is easy. Assign each (unique!) fitness in fitnesses a successively
        increasing front ID.
        """
        for i, f in enumerate(fitnesses):
            fitness_front_assignments[f] = i

    # build Pareto fronts, each front is a list of individuals.
    number_of_fronts = max(fitness_front_assignments.values()) + 1  # 3 fronts would be numbered 0..2.
    # pareto_fronts = [[]] * number_of_fronts  # list of empty lists, one for each front.
    pareto_fronts = [[] for _ in range(number_of_fronts)]
    for fit in fitnesses:
        front_id = fitness_front_assignments[fit]
        pareto_fronts[front_id].extend(fitness_candidates_map[fit])  # extract all individuals with this fitness

    # record each candidate's Pareto front rank (0 = leading front), used elsewhere in UNSGA3
    for fit in fitnesses:
        pareto_rank = fitness_front_assignments[fit]
        for candidate in fitness_candidates_map[fit]:
            candidate.non_dominated_rank = pareto_rank
    return pareto_fronts


def f1_dominates_f2(f1, f2):
    strictly_better = False
    for val1, val2 in zip(f1, f2):
        if val2 < val1:
            # breaks the 'no worse' clause. To dominate F2, F1 must be no worse in all objectives
            return False
        if val1 < val2:
            # must find at least one value where F1 is strictly better than F2.
            strictly_better = True
    return strictly_better


def nd_helper_A(fitnesses, num_objectives, fitness_front_assignments):
    """ Create a non-dominated sorting of S on the first M objectives. Used recursively. """
    if len(fitnesses) < 2:
        return
    if len(fitnesses) == 2:
        f1, f2 = fitnesses[0], fitnesses[1]
        if f1_dominates_f2(f1=f1[:num_objectives], f2=f2[:num_objectives]):
            # f2 is either already a higher front id than f1, or we give it front id f1 + 1.
            fitness_front_assignments[f2] = max(fitness_front_assignments[f2], fitness_front_assignments[f1] + 1)

    elif num_objectives == 2:
        sweep_A(fitnesses, fitness_front_assignments)

    elif len(frozenset([f[num_objectives-1] for f in fitnesses])) == 1:
        # create immutable set of last objective values for all fitnesses. Are these unique?
        # all individuals share the same value for last objective. Recurse, ignoring last objective value.
        nd_helper_A(fitnesses, num_objectives-1, fitness_front_assignments)
    else:
        # >2 individuals, split list and recurse. Low is list containing fitnesses <= median in last objective value
        low, high = split_A(fitnesses, num_objectives-1)  # partition fitnesses around last objective index median
        nd_helper_A(low, num_objectives, fitness_front_assignments)
        nd_helper_B(low, high, num_objectives-1, fitness_front_assignments)
        nd_helper_A(high, num_objectives, fitness_front_assignments)


def sweep_A(fitnesses, fitness_front_assignments):
    """
    Sorting or fitnesses over just two objectives. `Fitnesses` is already sorted on first objective. This focusses
    on increasing fitnesses' front IDs if their second objective values are inferior.
    """
    T = [fitnesses[0]]  # can hold at most one fitness per front index
    for s in fitnesses[1:]:
        U = [t for t in T if t[1] <= s[1]]  # collect fitnesses with better or equal second objective values.
        if U:  # not empty. This contains fitnesses better than s
            r = max([fitness_front_assignments[u] for u in U])
            # either retain s's front id, or assign +1 from worse in u, whichever is bigger.
            fitness_front_assignments[s] = max(fitness_front_assignments[s], r + 1)
        # dealt with s's front id, so remove all matches for it.
        T = [t for t in T if fitness_front_assignments[t] != fitness_front_assignments[s]]
        T.append(s)


def split_A(fitnesses, objective_index):
    """
    Partition the set of fitnesses in two lists around the median value of the `objective_index` objective. Fitnesses
    representing the median value are assigned to one of these lists to try and retain equal list sizes.
    The split is done in a manner that preserves the original lexicographic ordering.
    """
    median_value = statistics.median([f[objective_index] for f in fitnesses])
    """ items holding the median value are all to be added either to low or high, to best maintain equal sizes between
    the two lists. However, this must also be done in a manner that preserves the lexicographic ordering of the original
    sorted `fitnesses`. Hence, these additions must be done in place (as the loop will process fitneses in lexicographic
    order). To manage this, we build low and high lists for both scenarios (a and b) and choose to return either the
    a or b scenarios at the end """
    low_a, high_a = [], []
    low_b, high_b = [], []

    for fit in fitnesses:
        if fit[objective_index] < median_value:
            low_a.append(fit)
            low_b.append(fit)
        elif fit[objective_index] > median_value:
            high_a.append(fit)
            high_b.append(fit)
        else:  # holds the median value
            low_a.append(fit)
            high_b.append(fit)

    difference_a = abs(len(low_a) - len(high_a))  # calculate difference in list lengths
    difference_b = abs(len(low_b) - len(high_b))

    if difference_a <= difference_b:
        return low_a, high_a
    else:
        return low_b, high_b


def nd_helper_B(low, high, number_objectives, fitness_front_assignments):
    if not low or not high:  # if either list empty
        return
    obj_index = number_objectives - 1  # index of last objective under consideration (may not be all of them)
    if len(low) == 1 or len(high) == 1:
        for l in low:
            for h in high:
                if f1_dominates_f2(l[:number_objectives], h[:number_objectives])\
                        or l[:number_objectives] == h[:number_objectives]:
                    # if l dominates, h front id must be at least 1 greater than l front id.
                    # same is true if l and h are equal on all objectives under consideration, as previous recursive
                    # calls established l to dominate h on every objective greater than number_objectives.
                    fitness_front_assignments[h] = max(fitness_front_assignments[h], fitness_front_assignments[l] + 1)
    elif number_objectives == 2:
        sweep_B(low, high, fitness_front_assignments)
    # if true, then all of low's values for last objective under consideration are smaller than high's
    elif max(l[obj_index] for l in low) <= min(h[obj_index] for h in high):
        nd_helper_B(low, high, number_objectives - 1, fitness_front_assignments)
    # for last objective under consideration, is low's best value smaller than high's worst?
    elif min(l[obj_index] for l in low) <= max(h[obj_index] for h in high):
        # at this point there is overlap in l and h's range of values for obj_index.
        low1, low2, high1, high2 = split_B(low, high, number_objectives-1)
        nd_helper_B(low1, high1, number_objectives, fitness_front_assignments)
        nd_helper_B(low1, high2, number_objectives-1, fitness_front_assignments)
        nd_helper_B(low2, high2, number_objectives, fitness_front_assignments)


def split_B(low, high, objective_index):
    """
    This employs the exact same logic as split_A, but operates on two lists (low and high) simultaneously. It returns
    four lists, splits of low and high.
    """
    if len(low) > len(high):
        pivot = statistics.median([l[objective_index] for l in low])
    else:
        pivot = statistics.median([h[objective_index] for h in high])

    low1_a, low2_a, low1_b, low2_b = [], [], [], []
    for fit in low:
        if fit[objective_index] < pivot:
            low1_a.append(fit)
            low1_b.append(fit)
        elif fit[objective_index] > pivot:
            low2_a.append(fit)
            low2_b.append(fit)
        else:
            low1_a.append(fit)
            low2_b.append(fit)

    high1_a, high2_a, high1_b, high2_b = [], [], [], []
    for fit in high:
        if fit[objective_index] < pivot:
            high1_a.append(fit)
            high1_b.append(fit)
        elif fit[objective_index] > pivot:
            high2_a.append(fit)
            high2_b.append(fit)
        else:
            high1_a.append(fit)
            high2_b.append(fit)

    difference_a = abs((len(low1_a) - len(low2_a)) + (len(high1_a) - len(high2_a)))
    difference_b = abs((len(low1_b) - len(low2_b)) + (len(high1_b) - len(high2_b)))

    if difference_a <= difference_b:
        return low1_a, low2_a, high1_a, high2_a
    else:
        return low1_b, low2_b, high1_b, high2_b


def sweep_B(low, high, fitness_front_assignments):
    T = []
    i = 0
    for h in high:
        while i < len(low) and low[i][:2] <= h[:2]:  # contrast over first two objectives
            R = [t for t in T
                 if fitness_front_assignments[t] == fitness_front_assignments[low[i]] and t[1] < low[i][1]
                 ]
            if not R:
                T = [t for t in T if fitness_front_assignments[t] != fitness_front_assignments[low[i]]]
                T.append(low[i])
            i += 1
        U = [t for t in T if t[1] <= h[1]]
        if U:  # not empty
            r = max(fitness_front_assignments[u] for u in U)
            fitness_front_assignments[h] = max(fitness_front_assignments[h], r + 1)
