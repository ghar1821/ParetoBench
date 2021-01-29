"""

References used in this implementation:

Deb & Agrawal. (1999), A Niched-Penalty Approach for Constraint Handling in Genetic Algorithms. In: Artificial
Neural Nets and Genetic Algorithms, 235-243.

Mark N. Read, 2017
"""
# import matplotlib
# matplotlib.use('Agg')   # Force matplotlib to not use any Xwindows backend. Must be called before any pyplot import.
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import numpy as np
import random
from collections import Iterable
try:
    import lhsmdu  # Latin hypercube design. From https://github.com/sahilm89/lhsmdu
    latin_hypercube_population_seeding = True
except ImportError:
    print("lhsmdu cannot be found. This is used to seed the initial population using a latin hypercube."
          "It is non-essential, but the initial population will be generated using a uniform random "
          "distribution instead. If you wish to install lhsmdu, see:"
          "https://github.com/sahilm89/lhsmdu")
    latin_hypercube_population_seeding = False
from .reference_points import build_reference_points
from .non_dominated_sort import non_dominated_sort

__author__ = 'Mark N. Read'


class SolutionDimension:
    """
    Designed to be instantiated by user, and passed to UNSGA3. This represents dimensions of the solution space, that
    the optimisation process manipulates. Upper and lower bounds can be set, as can a granularity of possible values.
    The data store allows problem-specific data to be associated with each (not used within the UNSGA3 process).
    """
    def __init__(self, min_val, max_val, granularity=None, data_store=dict()):
        self.min_value = float(min_val)
        self.max_value = float(max_val)
        self.granularity = granularity
        # allows users to attach additional problem-specific information
        self.data_store = data_store

    def bind(self, putative_value):
        """ rounds the putative value to the nearest granularity-defined increment. """
        # ensure within valid ranges
        if putative_value > self.max_value:
            putative_value = self.max_value
        elif putative_value < self.min_value:
            putative_value = self.min_value

        if self.granularity is None:
            return putative_value
        return round(self.granularity * round(float(putative_value) / self.granularity), 10)


class Candidate:
    """
    Fitnesses should be provided as tuples. They are immutable, which is important for downstream algorithms that
    hash them.
    """
    def __init__(self, solution):
        self.training_fitness = ParetoFitness(())   # a ParetoFitness object
        self.validation_fitness = None   # a ParetoFitness object, left as None if validation fitnesses not used
        """
        used in non-dominated sorting, and is assigned either training or validation. This is minimise the number of
        external procedures requiring knowledge that Pareto fronts can be built based on training or validation
        fitnesses.
        """
        self.fitness = self.training_fitness
        self.fitness_normalised = None  # A ParetoFitness object. Normalisation in accordance with Deb 2014.
        self.solution = solution  # Point in problem space, a list.
        # Both of these are used in niching based on reference directions.
        self.closest_reference_direction = None
        self.closest_reference_direction_distance = None
        self.non_dominated_rank = None  # 0 = leading Pareto front.
        # this is supplied for storage of unanticipated data that does not pertain to UNSGA3, but may pertain to the
        # problem being optimised. For instance, the location of data on the file system or other metadata can be stored
        # here by the user.
        self.data_store = dict()

    def pareto_dominates(self, other, training_domination=True):
        """
        Pareto domination can be calculated with respect to training-dataset fitness values (default case) or
        validation dataset.
        """
        if training_domination:
            return self.training_fitness.dominates(other.training_fitness)
        else:
            return self.validation_fitness.dominates(other.validation_fitness)

    def activate_training_fitness(self):
        assert isinstance(self.fitness, ParetoFitness)
        self.fitness = self.training_fitness

    def activate_validation_fitness(self):
        assert isinstance(self.fitness, ParetoFitness)
        self.fitness = self.validation_fitness

    def clone_solution(self):
        """
        Only the solution should be cloned. Once mutated, crossovered, fitness assigned, all other data should be
        re-calculated
        :return: Clone of this candidate
        """
        return Candidate(list(self.solution))

    def bind(self, solution_dimensions):
        """
        Binds this candidate's solution to the granularity of permitted values.
        :param solution_dimensions: list of SolutionDimension objects
        :return:
        """
        for m, prob in enumerate(solution_dimensions):
            self.solution[m] = prob.bind(self.solution[m])

    def __str__(self):
        """
        Prepare the supplied individual as a string for writing to the terminal or a file.
        This will produce a line of this format:
           Candidate. Training: 66.5 285.5 54.5; validation: 37 32 31; solution: [1.1, 2.2, 3.3]
        """
        # this will produce a line of this format:
        # "66.5 285.5 54.5 7.0 12.0 0.0 : 37 32 31 505 78 10 41 102"
        line = 'Candidate. Training: [' + ' '.join('{:8.4f}'.format(objective) for objective in self.training_fitness) \
               + ']'
        if self.validation_fitness:
            line += '; validation: [' + ' '.join('{:8.4f}'.format(objective) for objective in self.validation_fitness) \
                    + ']'
        line += '; solution: [' + ' '.join('{:6.3f}'.format(sol_val) for sol_val in self.solution) + ']'
        return line


class ParetoFitness(tuple):
    """
    Represents a point in Fitness-space, which can be multi-dimensional. Has operators for contrasting two objects
    for Pareto-dominance. This is minimisation-only; maximisation problems can be converted to minimisation problems
    by negating or inverting (1/x) fitness values for each objective.

    Note that Pareto-domination is NOT symmetric. If x does not dominate y, that does NOT mean y dominates x. They can
    be Pareto equivalent, either if they represent the exact same point in objective space, or if x has a better
    value for one objective, but y has a better value for some other objective (in this case they are
    Pareto-equivalent and are both members of the Pareto front).

    Implemented as a subclass of Tuple, to be immutable.
    """
    def dominates(self, other, fitness_slice=None):
        """
        True if this object Pareto-dominates `other`. For this solution to Pareto-dominate `other`, it must be no
        worse than `other` on all objective scores, and better on at least one. A slice of the fitness vector,
        from zero, can be specified. This is useful for Fortin's 2013 non-dominated search implementation.
        """
        no_worse = True
        better = False
        if fitness_slice is None:
            fitness_slice = len(self)
        # set up for minimisation problems
        for s, o in zip(self[:fitness_slice], other[:fitness_slice]):  # compare this and other
            if o < s:  # a single example where other has a strictly-better fitness value than this object
                no_worse = False
                break  # no need to continue, this object does not dominate `other`.
            elif s < o:
                better = True
            else:
                # their values are equal. This is allowed, means that the solutions are Pareto-equal in that objective
                pass
        return no_worse and better  # must be no worse in all objective scores, and better in at least one.


class UNSGA3:
    def __init__(self, solution_dimensions, fitness_evaluator, num_objectives, max_generations,
                 reference_point_increments=10,
                 population_size=None,
                 terminate_overfitted=None,
                 generatonal_inspector_function=None):
        """
        :param solution_dimensions: a tuple containing (user) instantiated SolutionDimension objects
        :param fitness_evaluator: a procedure of method that takes a list (the population) and returns two lists as a
        tuple: (training dataset fitnesses, validation dataset fitnesses). The latter can instead be None if no
        validation dataset exists for this optimisation problem. Order in supplied population members must match the
        order of fitnesses returned in the list(s).
        :param reference_point_increments:
        :param population_size: size of population in GA. May be increased if user-specified value is not multiple of 4
        :param terminate_overfitted: Only relevant if the optimisation problem has both training and validation
        datasets. Overfitting is determined to be the proportion of training-dataset Pareto candidates that are NOT
        members of the validation dataset Pareto front. A value of 1 means none of the training dataset Pareto front
        sits on the validation dataset Pareto front, and the population is completely overfitted. None if the
        optimisation problem has no validation dataset, otherwise a value from 0..1.
        :param generatonal_inspector_function:
        :return:
        """
        self.population_size = population_size
        if population_size is not None and self.population_size % 4 != 0:
            raise Exception("Population size must be a multiple of 4. For more details, see: Seada & Deb"
                            "(2016). A Unified Evolutionary Optimization.... IEEE Trans Evol Com, 20, "
                            "358-369. Page 361")
        self.max_generations = max_generations
        if not isinstance(solution_dimensions, tuple):
            raise Exception("argument `solution_dimensions` must be of type tuple and contain only SolutionDimension "
                            "objects")
        for pd in solution_dimensions:
            if not isinstance(pd, SolutionDimension):
                raise Exception("argument `solution_dimensions` must contain only SolutionDimension objects.")
            if pd.max_value == pd.min_value:
                raise Exception("SolutionDimension object has same value for upper and lower bound. Hence, "
                                "this variable can only take one value. There is point including it in calibration "
                                "problem if it's value is already known.")
        self.solution_dimensions = solution_dimensions  # a list of SolutionDimension objects
        self.fitness_evaluator = fitness_evaluator
        self.generational_inspector_function = generatonal_inspector_function
        self.num_objectives = num_objectives
        self.reference_point_increments = reference_point_increments

        self.current_generation = 0
        # list of candidates comprising the Pareto fronts as assessed on training and validation datasets respectively
        self.training_pareto_front = []
        self.overfitted = []  # overfitteness of optimisation process, one item per generation
        self.currently_overfitted = False  # boolean, if True optimisation would have stopped
        self.validation_pareto_front = None  # a list, or left as None if validation fitnesses not used in problem
        self.current_population = None
        self.reference_directions = {}  # stored as a set
        # Threshold proportion of training dataset-Pareto front that is absent from the validation dataset Pareto-front
        # at which calibration effort is considered overfitted and U-NSGA-III is terminated.
        self.terminate_overfitted = terminate_overfitted
        self.sbx_nc = None  # set at run

    def run(self, sbx_nc=0.8):
        """
        Called externally to launch the optimisation process.
        :param sbx_nc: used in simulated binary crossover routine. 0..1, large value favours children resembling
        parents.
        :return: the final generation's population of Candidate objects, the Pareto front of candidates from the
        final generation, and the Pareto front of solutions based on validation fitnesses (if used), in that order as a
        tuple containing three lists.
        """
        self.sbx_nc = sbx_nc  # Used in crossover
        self.current_generation = 0
        # Create the reference vectors
        self.reference_directions = build_reference_points(dimensions=self.num_objectives,
                                                           increments=self.reference_point_increments)
        if not self.population_size:  # If not set by user
            # If not supplied, this calculates population size according to principle of Seada & Deb (2016): "The
            # population size N is chosen to be the smallest multiple of four grater than H, with the idea that for every
            # reference direction, one population member is expected to be found."
            self.population_size = len(self.reference_directions)
            while self.population_size % 4 != 0:
                self.population_size += 1
            print('Population size not specified by user. Setting to {:d}, based on number of reference '
                  'directions'.format(self.population_size))
        else:
            if self.population_size <= len(self.reference_directions):
                raise Exception("Population must be larger than number of reference directions (with current settings, "
                                "there are {:d} reference directions). See Seada 2016 paper, page 361."
                                .format(len(self.reference_directions)))
        # Initialise the population
        if latin_hypercube_population_seeding:
            self.current_population = self._initialise_population_latin_hypercube()
        else:
            self.current_population = self._initialise_population_uniform()
        for cand in self.current_population:
            cand.bind(self.solution_dimensions)
        validation_pareto_front = []
        # Stopping condition
        while self.current_generation < self.max_generations and not self.currently_overfitted:
            print('entering generation {:d}'.format(self.current_generation))
            # Create offspring based on supplied parents. Returned list contains both
            Rt = self._propagate_generation(self.current_population)
            for cand in self.current_population:
                cand.bind(self.solution_dimensions)
            self._assign_fitnesses(Rt)
            for candidate in Rt:
                candidate.activate_training_fitness()
            self.current_population = self._select_population(Rt=Rt)

            # Candidates selected in `_select_population` may not all be Pareto front members
            self.training_pareto_front = [cand for cand in self.current_population if cand.non_dominated_rank == 0]
            # If optimisation problem has validation component, calculate the validation dataset Pareto front.
            if self.current_population[0].validation_fitness is not None:
                # Validation Pareto front is added to the current population. As population becomes overfitted
                # validation Pareto front members will cease to be members of `self.current_population`.
                popn = self.current_population + validation_pareto_front
                for cand in popn:
                    cand.activate_validation_fitness()
                popn = self._select_population(Rt=popn)
                # The population returned can contain non-Pareto front individuals, remove these
                self.validation_pareto_front = [cand for cand in popn if cand.non_dominated_rank == 0]
                self.overfitted.append(self._measure_overfitting(self.validation_pareto_front,
                                                                   self.training_pareto_front))
                # Termination condition based on overfittedness
                if self.terminate_overfitted is not None and self.overfitted[-1] >= self.terminate_overfitted:
                    self.currently_overfitted = True  # will cause termination
                    print('Terminating optimistion process due to detection of overfitting')

            self.current_generation += 1
            # recommend checking for overfitting before overwriting data with inspectors - is the desired result that
            # before or after overfitting?
            if self.generational_inspector_function is not None:
                # allow outside inspection of what's going on, by passing this object. This assumes the user is not
                # going to do anything stupid to destroy internal state!
                self.generational_inspector_function(self)
        return self.current_generation, self.training_pareto_front, self.validation_pareto_front

    def _assign_fitnesses(self, population):
        """
        Calls the external hook to assign fitness values for members of the supplied population
        :param population: a list of Candidate objects
        :return:
        """
        def type_conversion(fit):
            if isinstance(fit, ParetoFitness):
                return fit  # unlikely to happen, as I've tried to hide ParetoFitness from the user.
            else:
                if not isinstance(fit, Iterable):
                    raise Exception("Fitnesses must be supplied as iterable objects (e.g., lists or tuples). "
                                    "Supplied fitness was:\n{:s}".format(str(fit)))
                return ParetoFitness(fit)

        # assign fitness only for those candidates that don't already have one. ParetoFitness(()), used in Candidate
        # instantiation, evaluates to False
        popn = [p for p in population if not p.training_fitness]
        training_fitnesses, validation_fitnesses = self.fitness_evaluator(popn, self.current_generation)
        # assign fitnesses to candidates, note that validation assignment is contingent on the problem format
        # some problems don't employ validation data sets
        for i, (candidate, tr) in enumerate(zip(popn, training_fitnesses)):
            candidate.training_fitness = type_conversion(tr)
            if validation_fitnesses is not None:
                candidate.validation_fitness = type_conversion(validation_fitnesses[i])

    def _propagate_generation(self, parents):
        """
        Corresponds to Algorithm 4 and lines 2 to 3 of Algorithm 1 in Seada 2016 paper.

        :param parents: list of Canddiate objects
        :return: list of Candidate objects, including both parents and offspring.
        """
        selected_parents = self._niching_based_selection(parents)
        offspring = self._simulated_binary_crossover_parents(selected_parents, self.sbx_nc)
        offspring = self._mutation_bounded_polynomial(offspring)
        Rt = parents + offspring
        return Rt

    def _select_population(self, Rt):
        """
        Corresponds to Algorithm 1, with the modification outlined in Alg 4, of Sed 2016 paper.
        Logic pertaining to offspring generation (crossover and mutation) have been extracted, they are only relevant
        for the training dataset, yet selection must be performed for both training and validation based
        Seada, H. and Deb, K. (2016) A unified evolutionary optimization procedure for single, multiple, and many
        objectives. IEEE Transactions of Evolutionary Computation 20:358-369.

        :return: the current population as a list of candidates
        """
        # returns a list of lists containing the supplied population. First item is the leading Pareto front.
        fronts = non_dominated_sort(Rt)
        i = 0  # i=1 in the paper, but in python lists start from 0 not 1
        St = []
        while len(St) < self.population_size and i < len(fronts):
            St.extend(fronts[i])
            i += 1
        # `i` holds the ID of the last front to be included
        Fl = fronts[i-1]  # last front to be included in St
        if len(St) == self.population_size:
            return St
        Pt = []  # equivalent to St/Fl (set notation, St with Fl removed), frequently referred to in Seada paper
        for j in range(i-1):  # iterates up to, but not including, last front to be included into St
            Pt.extend(fronts[j])
        # must pick k items from Fl, last front to be included in St
        k = self.population_size - len(Pt)
        # normalise objectives. This implementation uses supplied (Zs) reference set, does not compute (no Za here)
        self._normalise_candidate_fitnesses(St)  # in-place calculations, nothing to return
        # associate each member s of St with a reference direction
        # pi and d are implemented as dictionaries using candidates as keys. pi[cand] returns cand's nearest ref dir
        # d[cand] is the distance to that same reference direction
        pi, d = self._associate(St, self.reference_directions)
        # rho stores number of candidates associated with each ref direction. rho[ref dir] = count
        rho = dict((j, 0) for j in self.reference_directions)  # dictionary comprehension, assign rho[j] = 0 for all j
        # compute niche count of reference directions, based on already selected candidates
        for s in Pt:
            rho[pi[s]] += 1
        # choose K members one at a time from Fl to construct Pt+1
        self._niching(k, rho, pi, d, self.reference_directions, Fl, Pt)
        return Pt

    def _minimum_fitness_point(self, population):
        """
        Finds the point in fitness space defined by the minimum observed across entire population for each
        objective.
        :param population: list of Candidate objects.
        :return: list containing the smallest value seen for each objective anywhere in the population.
        """
        min_pt = [float('Inf')] * self.num_objectives  # start with [Inf, Inf, ..., Inf]
        for i in range(self.num_objectives):
            min_pt[i] = min([candidate.fitness[i] for candidate in population])
        return min_pt

    def _fitnesses_with_extreme_objective_values(self, fitnesses):
        """
        Finds those fitnesses possessing the extreme value for each objective. If there are 3 objectives,
        this will return a list with 3 fitnesses (though some of these can be the same object, if that fitness was the
        worst on more than one objective).
        :param fitnesses: list of lists (not Candidates)
        :return: list of lists (fitnesses), one item per objective.
        """
        extremes = []  # List of Candidate objects.
        for i in range(self.num_objectives):  # Sort fitnesses by each item in turn.
            # Get last item, that with the biggest objective value
            e = sorted(fitnesses, key=lambda fit: fit[i])[-1]
            extremes.append(e)
        return extremes

    def _determine_hyperplane(self, extreme_fitness_points):
        """
        Provides implementation of Deb 2014, part 4.C and Figure 2.
        Implementation is based on that of the lmarti-nsgaiii python package.

        :param extreme_fitness_points:
        :return: list of intercepts where hyperplane intersects each objective. Special case if problem is degenerate.
        Ie, for a four dimensional problem, the return list would contain four values: e.g. [11, 8, 9, 2]. These are
        the values where the hyperplane intercepts each dimension's axis.
        """
        def duplicate_fitnesses(fitnesses):
            """ Check whether the supplied population contains candidates with duplicate fitnesses (same in all
            objectives values. """
            for i in range(len(fitnesses)):
                for j in range(i + 1, len(fitnesses)):
                    # Returns true only if all items in each fitness vector are identical.
                    if np.all(fitnesses[i] == fitnesses[j]):  # Boolean "all".
                        return True
            return False

        num_objectives = len(extreme_fitness_points[0])
        if not duplicate_fitnesses(extreme_fitness_points):
            """ uses linear algebra to find the intercepts of where the hyperplane connecting these candidates
            intersects each objective dimension. If there are candidates with identical fitness vectors, then this is a
            degenerate problem, and can't be solved (can't construct a hyperplane of dimensionality 1-num_objectives.
            Imagine it in 2D, you can find the intercepts of a line on x and y axes (assuming it's not vertical or
            horizontal), but you can't do it if you only have a point. """
            b = np.ones(num_objectives)
            x = np.linalg.solve(extreme_fitness_points, b)  # extreme_fitness_points = A in typical matrix terminology
            intercepts = 1. / x
        else:
            # Degenerate problem
            intercepts = [extreme_fitness_points[o][o] for o in range(num_objectives)]
        return intercepts

    def _normalise_candidate_fitnesses(self, population):
        """
        Normalises the finesses of the supplied population such that all fitness points lie between the origin and
        a hyperplane of extreme value that intersects each objective axis at 1.
        :param population: list of Candidate objects.
        :return: nothing, population is modified in place.
        """
        minimum_point = self._minimum_fitness_point(population)
        translated_fitnesses = []  # temporary variable, store population's fitnesses in here whilst calculating
        for candidate in population:
            # translate all points in fitness space around the minimum point (ie, minimum point is now the origin)
            translated_fit = [candidate.fitness[m] - minimum_point[m] for m in range(self.num_objectives)]
            translated_fitnesses.append(translated_fit)
        # Determine the hyperplane of the now-translated population's fitness values.
        extreme_fitnesses = self._fitnesses_with_extreme_objective_values(translated_fitnesses)
        hyperplane_intercepts = self._determine_hyperplane(extreme_fitnesses)
        for candidate, translated in zip(population, translated_fitnesses):
            # normalised fitness is fitness shifted such that minimum point is origin, and then scaled such the
            # hyperplane of normalised extreme fitness values has intercepts of 1 on each axis.
            norm_fit = []
            for m in range(self.num_objectives):
                # guard against div by zero. This can happen if all candidates have the same value for a given
                # objective, and both the minimum and extreme values for that objective are zero.
                if hyperplane_intercepts[m] != 0:
                    norm_fit.append(translated[m] / hyperplane_intercepts[m])
                else:
                    norm_fit.append(1.)
            candidate.fitness_normalised = ParetoFitness(norm_fit)

    def _associate(self, St, reference_directions):
        """
        Associates candidates with their closest reference directions in fitness space. Corresponds to algorithm 3 in
        Deb 2014. Nomenclature follows that algorithm.
        :param St: a list of Candidate objects, these are already selected for inclusion in next generation
        :param reference_directions: a list of ReferenceDirection objects.
        :return:
        """
        def perpendicular_distance(vector, point):
            # borrowed from the lmarti nsga-iii implementation. Implementation has been checked. I changed the order
            # of operands in the np.subtract term, as they are written the other way around in the Deb 2014 paper. At
            # the very least this makes it more consistent with the source, and controls for a potential error if
            # order of subtraction before working out vector magnitude impacts the result (I think it doesn't).
            k = np.dot(vector, point) / np.sum(np.power(vector, 2))
            d = np.sum(np.power(np.subtract(point, np.multiply(vector, [k] * len(vector))), 2))
            return np.sqrt(d)

        pi = dict()  # keys are candidates, values are the reference directions they are associated with
        d = dict()  # keys are candidates, values are distance to reference direction (the closest one)
        for s in St:
            # tuple of reference dir, and perpendicular distance of candidate s from it. Iteratively updated.
            closest = (None, float('Inf'))
            for ref_dir in reference_directions:
                dist = perpendicular_distance(ref_dir, s.fitness_normalised)
                if dist < closest[1]:
                    closest = (ref_dir, dist)
            pi[s] = closest[0]
            d[s] = closest[1]
        return pi, d

    def _niching(self, num_to_select, rho, pi, d, Zr, Fl, Pt):
        """
        Nomenclature largely follows Deb 2014 Algorithm 4, except in places where I find that downright unhelpful.
        :param num_to_select: called "K" in Deb 2014. Number of candidates to select from Fl
        :param rho: map, keys are reference directions, values are number of (already) selected candidates associated
        with each reference direction
        :param pi: map, keys are candidates, values are the reference direction each candidate is associated with
        :param d: map, keys are candidates, values are distance of candidate to its associated reference direction
        :param Zr: list of reference directions (tuples)
        :param Fl: the non-dominated front from which `num_to_select` candidates must be selected
        :param Pt: the list of selected candidates
        :return: the list of, not expanded, selected candidates
        """
        # create copy, as we will remove selected reference directions to avoid picking twice
        unrepresented_reference_directions = list(Zr)
        k = 1
        while k <= num_to_select:
            # Deb 2014 Alg 3 randomly selects amongst reference directions sharing the same number of associated
            # candidates. To do this, we sort on tuples, the first item is a reference direction's number of associated
            # candidates, the second is a random number. Tuple sorting defers to the second item if the first are equal.
            ref_dirs = sorted(unrepresented_reference_directions,
                              key=lambda rd: (rho[rd], random.random()))
            j = ref_dirs[0]  # assign (randomly, see line above) ref dir with smallest number of associated candidates
            # list candidates associated with this ref dir that are not already selected
            I = [s for s in Fl if pi[s] == j]
            if I:
                # I is not empty
                if rho[j] == 0:
                    # j isn't associated with any already-selected candidates, but is with some unselected (those in I)
                    # select the closest candidate in I, that with min d[cand] value. Do this by sorting.
                    selected = sorted(I, key=lambda cand: d[cand])[0]
                else:
                    selected = random.choice(I)  # select random candidate from I
                Pt.append(selected)
                rho[j] += 1  # because we just selected this candidate associated with j
                Fl.remove(selected)  # candidate has been selected
                k += 1
            else:
                # I is empty, all candidates associated with this ref dir have already been selected
                unrepresented_reference_directions.remove(j)
        return Pt

    def _simulated_binary_crossover_parents(self, parents, nc):
        """
        Nomenclateur follows that of Deb 1999, Appendix A. Performs SBX crossover on two values. produces two children
        for each parent pairing. If you supply 8 parents, 16 children are generated, as parents are used in (on average)
        two pairings.
        :param parents: list of Candidate objects
        :param nc: distribution index, float. Larger values generate offspring lying nearer their parents.
        :return:
        """
        def sbx_helper(y1, y2, nc, lower, upper):
            """
            Performs SBX crossover on two values.
            :param y1: first parent value to be used in crossover
            :param y2: second parent value.
            :param nc: sbx distribution index. Large values promote children with similar values to their parents.
            :param lower: lower bound of valid values for this parameter
            :param upper: upper bound of valid values for this parameter
            :return:
            """
            if y2 < y1:  # implementation assumes y1 < y2; switch if needed
                y1, y2 = y2, y1
            # avoid div by zero if y1 == y2 (or near enough)
            if abs(y1 - y2) < 1e-14:
                return y1, y2

            beta = 1. + (2. / (y2 - y1)) * min((y1 - lower), (upper - y2))
            alpha = 2. - (beta ** -(nc + 1))
            u = np.random.uniform()
            if u <= 1. / alpha:
                beta_q = (u * alpha) ** (1. / (nc + 1))
            else:
                beta_q = (1. / (2. - u * alpha)) ** (1. / (nc + 1))
            # Deb 1999 has needless abs operator here; y1<y2 asserted above
            c1 = 0.5 * ((y1 + y2) - beta_q * (y2 - y1))
            c2 = 0.5 * ((y1 + y2) + beta_q * (y2 - y1))
            # ensure values remain within bounds
            c1 = min(max(c1, lower), upper)
            c2 = min(max(c2, lower), upper)
            if np.random.uniform() < 0.5:
                # swap values, ensuring a mix of "chromosomes" from parents to children.
                c1, c2 = c2, c1
            return c1, c2

        assert(nc >= 0.)
        # parents randomly selected for use in crossover.
        # this ensure each parent is used at least one.
        p1_indices = list(range(len(parents))[0::2])  # every second index, starting 0, for `parents` list.
        p2_indices = list(range(len(parents))[1::2])  # every second index, starting 1, for `parents` list.
        # the remaining tournaments (of which there is half the population size) are assigned parents randomly.
        p1_indices.extend(np.random.randint(low=0, high=len(parents), size=self.population_size // 2))
        p2_indices.extend(np.random.randint(low=0, high=len(parents), size=self.population_size // 2))
        children = []
        for index1, index2 in zip(p1_indices, p2_indices):
            parent1, parent2 = parents[index1], parents[index2]
            child1 = parent1.clone_solution()
            child2 = parent2.clone_solution()
            for i, (y1, y2, dimension) in enumerate(zip(parent1.solution,
                                                        parent2.solution, self.solution_dimensions)):
                lower = dimension.min_value
                upper = dimension.max_value
                c1, c2 = sbx_helper(y1, y2, nc, lower, upper)
                child1.solution[i] = c1
                child2.solution[i] = c2
            children.append(child1)
            children.append(child2)
        return children

    def _mutation_bounded_polynomial(self, parents):
        """
        Nomenclateur follows that of Deb 1999, Appendix A. Mutates each value in a candidate according to a
        polynomial distribution. Following that same paper, mutation_probability (probability that a given value is
        mutated) and nm (mutation rate) have been set up to give a 1% mutation, which in early generations mutates
        few values by 1%, but in later generations mutates more values by a smaller amount.
        :param parents: list of Candidates.
        :param mutation_probability: probability that mutation operator is applied to each value in each Candidate.
        :return: list of mutated Candidates.
        """
        def mutation_helper(y, lower, upper, nm):
            u = np.random.uniform()
            delta = min((y - lower), (upper - y)) / (upper - lower)

            if u <= 0.5:
                delta_q = 2. * u + (1. - 2. * u) * ((1. - delta) ** (nm + 1.))
                delta_q = (delta_q ** (1. / (nm + 1.))) - 1.
            else:
                delta_q = 1. - ((2 * (1 - u)) + 2 * (u - 0.5) * (1 - delta) ** (nm + 1.)) ** (1. / (nm + 1.))
            c = y + delta_q * (upper - lower)
            return c

        one_n = 1. / self.population_size  # 1 over n
        mutation_probability = one_n + (self.current_generation / self.max_generations) * (1. - one_n)
        for candidate in parents:
            for i, (y, dimension) in enumerate(zip(candidate.solution, self.solution_dimensions)):
                if np.random.uniform() <= mutation_probability:
                    nm = 100. + float(self.current_generation)
                    y_mutated = mutation_helper(y, lower=dimension.min_value, upper=dimension.max_value, nm=nm)
                    candidate.solution[i] = y_mutated
        return parents

    def _niching_based_selection(self, parents):
        def niching_helper(p1, p2):
            """ Corresponds with Algorithm 2 in the Seada paper. """
            # ensure these have been assigned, which they may not be at algorithm start.
            if p1.closest_reference_direction is not None and p2.closest_reference_direction is not None and \
                            p1.closest_reference_direction == p2.closest_reference_direction:
                if p1.non_dominated_rank < p2.non_dominated_rank:
                    return p1
                if p2.non_dominated_rank < p1.non_dominated_rank:
                    return p2
                if p1.distance_to_closest_niching_direction < p2.distance_to_closest_niching_direction:
                    return p1
                else:
                    return p2
            else:
                # each candidate is associated with a different reference direction, select at random.
                return p1 if np.random.uniform() < 0.5 else p2

        # parents randomly selected from list for use in niching-based tournament selection.
        # this ensures each parent is used at least one.
        p1_indices = list(range(len(parents))[0::2])  # every second index, starting 0, for `parents` list.
        p2_indices = list(range(len(parents))[1::2])  # every second index, starting 1, for `parents` list.
        # the remaining tournaments (of which there is half the population size) are assigned parents randomly.
        p1_indices.extend(np.random.randint(low=0, high=len(parents), size=self.population_size // 2))
        p2_indices.extend(np.random.randint(low=0, high=len(parents), size=self.population_size // 2))
        selected = [niching_helper(p1=parents[i], p2=parents[j]) for i, j in zip(p1_indices, p2_indices)]
        return selected

    def _initialise_population_uniform(self):
        """
        Seed the population using a uniform random distribution.
        :return: a list of Candidate objects (with no assigned fitnesses)
        """
        population = []
        for c in range(self.population_size):
            solution = np.random.uniform(size=len(self.solution_dimensions))
            for i, dim in enumerate(self.solution_dimensions):
                dimension_range = dim.max_value - dim.min_value
                solution[i] = (solution[i] * dimension_range) + dim.min_value
            population.append(Candidate(solution=solution))
        return population

    def _initialise_population_latin_hypercube(self):
        """
        Use a latin hypercube to seed the population of solutions.
        :return: a list of Candidate objects (with no assigned fitnesses)
        """
        k = lhsmdu.sample(len(self.solution_dimensions), self.population_size)  # returns numpy matrix
        # scale the design for each dimension onto the correct range
        for i, dim in enumerate(self.solution_dimensions):
            dimension_range = dim.max_value - dim.min_value
            k[i] = (k[i] * dimension_range) + dim.min_value  # operates on entire slice at once
        # bind each dimension's putative value to valid intervals (granularity)
        for i, dim in enumerate(self.solution_dimensions):
            for c in range(self.population_size):
                k[i, c] = dim.bind(k[i, c])
        population = []  # a list of lists, each inner list being a candidate
        # convert into format needed, a list of lists.
        for c in range(self.population_size):
            candidate_solution = [k[d, c] for d in range(len(self.solution_dimensions))]
            candidate = Candidate(solution=candidate_solution)
            population.append(candidate)
        return population

    @staticmethod
    def _measure_overfitting(validation_front, target_front):
        """
        Provides a measure of how much the current target data set-optimised pareto front is over-fitted to the target
        set, by comparing its performance against the validation data set-optimised front.
        :param validation_front:
        :param target_front:
        :return:
        """
        combined = validation_front + target_front
        # set up assessment on the validation data set.
        for candidate in combined:
            candidate.activate_validation_fitness()

        fronts = non_dominated_sort(combined)
        pareto_front = fronts[0]  # work on the leading front
        # count the number of target_archive items that appear on the front
        included = 0
        for candidate in target_front:
            if candidate in pareto_front:
                included += 1
        # gives value between 0 and 1. 0 = all target solutions lie on front; 1 = none do.
        overfitted = 1.0 - (float(included) / len(target_front))
        return overfitted

    def plot_overfitted(self, direc):
        """ Reporter method. """
        plt.clf()
        generations = range(0, len(self.overfitted))
        plt.plot(generations, self.overfitted)
        plt.ylim((0.0, 1.0))
        plt.xlabel('Generation')
        plt.ylabel('Overfitted')
        plt.gca().grid(True)   # turn on grid lines.
        font = {'size': 18}
        plt.rc('font', **font)
        filename = direc + '/pareto_overfitted.png'
        plt.savefig(filename, dpi=300)
