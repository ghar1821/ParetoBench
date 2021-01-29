import numpy as np
from coclust.evaluation.external import accuracy


def calculate_bias_example():
    # 1 = B cell, 2 = PDC
    label_true = [1] * 10000 + [2] * 10
    label_pred = [1] * 9950 + [2] * 50 + [1] * 9 + [2] * 1
    acc = accuracy(np.array(label_true), np.array(label_pred))
    print(acc)


def see_changes_in_accuracy():
    # 1 = B cell, 2 = PDC
    label_true = [1] * 10000 + [2] * 10
    label_pred = [1] * 9950 + [2] * 50 + [1] * 10 + [2] * 0
    # add 1 PDC to cluster A over time
    for i in range(1, 11):
        label_pred = [1] * 9950 + [2] * 50 + [1] * (10-i) + [2] * (0+i)
        print(i)
        acc = accuracy(np.array(label_true), np.array(label_pred))
        print(acc)




if __name__ == '__main__':
    see_changes_in_accuracy()



