from calculate_accuracy import calculate_accuracy
from calculate_ari import calculate_ari
from calculate_v_measure import calculate_v_measure
from joblib import Parallel, delayed
import os


def calculate(param):
    calculate_accuracy(param)
    calculate_ari(param)
    calculate_v_measure(param)

if __name__ == '__main__':

    params = range(0, 99)
    # Parallel(n_jobs=4)(delayed(calculate_accuracy)(i) for i in params)
    for i in params:
    	calculate(i)
