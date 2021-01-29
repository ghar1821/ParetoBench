import numpy as np
from scipy.special import comb
from sklearn.metrics import adjusted_rand_score, v_measure_score, homogeneity_score, completeness_score
from sklearn import datasets
from sklearn.cluster import KMeans



def compute_perfect_clustering():
    n = np.array([5, 0, 0, 5, 0, 4, 0, 4, 0, 0, 4, 4, 5, 4, 4])

    k = np.array([2] * len(n))

    combination_of_two = calculate_combination(n, k)

    print("combination of two")
    print(combination_of_two)

    nij_sum = np.sum(np.array([10, 0, 0, 0, 6, 0, 0, 0, 6]))
    row_sum = np.sum(np.array([10, 6, 6]))
    col_sum = np.sum(np.array([10, 6, 6]))
    n_2 = calculate_combination(np.array([13]), np.array([2]))[0]

    print("nij_sum")
    print(nij_sum)
    print("row_sum")
    print(row_sum)
    print("col_sum")
    print(col_sum)
    print("n_2")
    print(n_2)

    ari = np.divide(
        nij_sum - np.divide(row_sum*col_sum, n_2),
        np.divide(row_sum+col_sum,2) - np.divide(row_sum*col_sum, n_2)
    )

    print("ARI manual: {}".format(ari))

    ground_truth = [1,1,1,1,1,2,2,2,2,3,3,3,3]
    clustering = [4,4,4,4,4,5,5,5,5,6,6,6,6]

    ari_sklearn = adjusted_rand_score(ground_truth, clustering)

    print("ARI sklearn: {}".format(ari_sklearn))


def compute_over_clustering():
    nij = np.array([2,3,0,0,0,0,0,0,2,2,0,0,0,0,0,0,2,2])
    row_sum = np.array([5,4,4])
    col_sum = np.array([2,3,2,2,2,2])

    nij_comb = calculate_combination(nij, np.array([2] * len(nij)))
    row_sum_comb = calculate_combination(row_sum, np.array([2] * len(row_sum)))
    col_sum_comb = calculate_combination(col_sum, np.array([2] * len(col_sum)))

    print("nij_comb")
    print(nij_comb)
    print("row_sum_comb")
    print(row_sum_comb)
    print("col_sum_comb")
    print(col_sum_comb)

    nij_sum = np.sum(nij_comb)
    row_sum = np.sum(row_sum_comb)
    col_sum = np.sum(col_sum_comb)
    n_2 = calculate_combination(np.array([np.sum(nij)]), np.array([2]))[0]

    print("nij_sum")
    print(nij_sum)
    print("row_sum")
    print(row_sum)
    print("col_sum")
    print(col_sum)
    print("n_2")
    print(n_2)

    ari = np.divide(
        nij_sum - np.divide(row_sum * col_sum, n_2),
        np.divide(row_sum + col_sum, 2) - np.divide(row_sum * col_sum, n_2)
    )
    print("ARI manual: {}".format(ari))

    labels_true = np.array([1,1,1,1,1,2,2,2,2,3,3,3,3])
    labels_pred = np.array([4,4,7,7,7,5,5,8,8,6,6,9,9])

    ari_sklearn = adjusted_rand_score(labels_true, labels_pred)

    print("ARI sklearn: {}".format(ari_sklearn))


def compute_under_clustering():
    nij = np.array([5,0,0,4,2,2])
    row_sum = np.array([5,4,4])
    col_sum = np.array([7,6])

    nij_comb = calculate_combination(nij, np.array([2] * len(nij)))
    row_sum_comb = calculate_combination(row_sum, np.array([2] * len(row_sum)))
    col_sum_comb = calculate_combination(col_sum, np.array([2] * len(col_sum)))

    print("nij_comb")
    print(nij_comb)
    print("row_sum_comb")
    print(row_sum_comb)
    print("col_sum_comb")
    print(col_sum_comb)

    nij_sum = np.sum(nij_comb)
    row_sum = np.sum(row_sum_comb)
    col_sum = np.sum(col_sum_comb)
    n_2 = calculate_combination(np.array([np.sum(nij)]), np.array([2]))[0]

    print("nij_sum")
    print(nij_sum)
    print("row_sum")
    print(row_sum)
    print("col_sum")
    print(col_sum)
    print("n_2")
    print(n_2)

    ari = np.divide(
        nij_sum - np.divide(row_sum * col_sum, n_2),
        np.divide(row_sum + col_sum, 2) - np.divide(row_sum * col_sum, n_2)
    )
    print("ARI manual: {}".format(ari))

    labels_true = np.array([1,1,1,1,1,2,2,2,2,3,3,3,3])
    labels_pred = np.array([4,4,4,4,4,5,5,5,5,4,4,5,5])

    ari_sklearn = adjusted_rand_score(labels_true, labels_pred)

    print("ARI sklearn: {}".format(ari_sklearn))


def calculate_combination(n, k):

    combination = comb(n, k, exact=False)

    return combination


def experiment_ari():
    """
    Kmeans stat:
    2 features
    2 clusters = 0.33
    3 clusters = 0.61
    4 clusters = 0.39
    5 clusters = 0.37
    6 clusters = 0.35
    7 clusters = 0.32
    8 clusters = 0.30

    3 features
    2 clusters = 0.53
    3 clusters = 0.70
    4 clusters = 0.60
    5 clusters = 0.58
    6 clusters = 0.42
    7 clusters = 0.41
    8 clusters = 0.43

    4 features
    2 clusters = 0.54
    3 clusters = 0.73
    4 clusters = 0.65
    5 clusters = 0.61
    6 clusters = 0.46
    7 clusters = 0.48
    8 clusters = 0.45
    """

    # ari: 0.387
    labels_true = [0,0,0,0,0,1,1,1,1,1,1,2,2]
    labels_pred = [3,3,3,3,4,4,4,5,5,5,6,6,6]

    # ari: 0.53
    labels_pred = [3,3,4,4,4,5,5,6,6,6,6,7,7]

    iris = datasets.load_iris()
    data = iris.data[:, :4]  # we only take the first two features.
    labels_true = iris.target

    for i in range(2, 9):
        kmeans = KMeans(n_clusters=i)
        labels_pred = kmeans.fit_predict(data)

        ari = adjusted_rand_score(labels_true, labels_pred)

        print(i)
        print(ari)


def simulate_rare_dataset():
    labels_true = np.concatenate((np.zeros(30000), np.ones(30)))
    labels_pred = np.concatenate((np.full((10000, 1), 0),
                                  np.full((5000,1), 1),
                                  np.full((5000, 1), 2),
                                  np.full((5000, 1), 3),
                                  np.full((2000, 1), 4),
                                  np.full((3000, 1), 5),
                                  np.full((10, 1), 6),
                                  np.full((20, 1), 7)))
    ari = adjusted_rand_score(labels_true.ravel(), labels_pred.ravel())
    vmeasure = v_measure_score(labels_true.ravel(), labels_pred.ravel())
    homogeneity = homogeneity_score(labels_true.ravel(), labels_pred.ravel())
    completeness = completeness_score(labels_true.ravel(), labels_pred.ravel())
    print(ari)
    print(vmeasure)
    print(homogeneity)
    print(completeness)


if __name__ == '__main__':
    simulate_rare_dataset()
