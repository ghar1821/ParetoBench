import numpy as np


__author__ = 'Mark N. Read'


def ncr(n, r):
    """ Calculates combinatorics. How many ways of selecting r items from n. """
    r = min(r, n - r)
    if r == 0:
        return 1
    numer = np.prod(range(n, n - r, -1))  # returns product of all items in list/array
    denom = np.prod(range(1, r + 1))
    return numer // denom  # integer division


def build_reference_points(dimensions, increments):
    """
    Increments includes zero. E.g., value of 5 will result in increments at 0, 0.25, 0.5, 0.75, 1.
    Returns a numpy matrix, [reference point, dimension].

    Implementation is from Das & Dennis, 1998, Normal-Boundary intersection: A new method for generating the Pareto surface
    in non-linear multicriteria optimization problems. Society for Indistural and Applied Mathematics Journal of
    Optimisation.

    Reference points are built through recursion, population values in a predefined numpy matrix (rather than compiling
    points during the recursive process; this was the initial implementation, but involved a lot of list cloning which
    is computationally inefficient. Instead, each recursion to the subsequent dimension being populated records how many
    references points should be assigned the value under current consideration.

    All dimensions utilise the same number of divisions/increments, which are all equally spaced.

    :return: list containing reference points, each of which is a tuple of values for each dimension.
    """
    def build_reference_points_recursively(dimension_being_processed, increments_remaining):
        # special case, tree leaf
        if dimension_being_processed == 0:
            reference_points[point_to_write[dimension_being_processed], dimension_being_processed] \
                = increments_remaining - 1
            point_to_write[dimension_being_processed] += 1
            return 1

        # node in tree, not a leaf
        cumulative_points_written = 0
        for i in range(increments_remaining):
            # recursion
            points_written = build_reference_points_recursively(dimension_being_processed=dimension_being_processed - 1,
                                                                increments_remaining=increments_remaining - i)
            j = point_to_write[dimension_being_processed]
            k = j + points_written
            reference_points[j:k, dimension_being_processed] = i  # slice, assign increment index
            point_to_write[dimension_being_processed] = k  # update how many reference points have been written
            cumulative_points_written += points_written
        return cumulative_points_written

    p = increments - 1  # includes zero. Hence, p from Das & Dennis paper is this -1.
    number_of_points = ncr(dimensions + p - 1, p)
    print("Number of reference points (or directions) to generate = {:d}".format(number_of_points))
    # set values to -1, a nonsensical value that can be used to ensure all cells in matrix are written to
    reference_points = np.ones([number_of_points, dimensions]) * -1.
    # used in the recursive process to write values to reference_points. Starting at zero, this refers to the next
    # reference point to be written, and is incremented accordingly once writing completes.
    point_to_write = [0] * dimensions
    # start the recursion. Rather than calculate the exact increment size (which is a fraction <1), the denominators
    # (integers) are recorded. This is more accurate. Thereafter increment indexes are converted to fractions.
    build_reference_points_recursively(dimension_being_processed=dimensions-1, increments_remaining=increments)
    reference_points /= float(p)  # convert increment indexes to fraction (0, 1)
    reference_points_tuples = list(tuple(rp) for rp in reference_points)
    return reference_points_tuples


