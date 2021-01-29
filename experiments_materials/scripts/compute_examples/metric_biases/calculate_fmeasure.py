from sklearn.metrics import f1_score


def scenario_1():
    true_labels = ['B cell'] * 13 + ['T cell'] * 13
    clusters = ['A'] * 5 + ['B'] * 8 + ['A'] * 4 + ['C'] * 3 + ['D'] * 4 + ['E'] * 2
    pred_labels = {
        'A': 'B cell',
        'B': 'B cell',
        'C': 'T cell',
        'D': 'T cell',
        'E': 'T cell'
    }
    pred_clusters = [pred_labels[x] for x in clusters]
    fscore = f1_score(true_labels, pred_clusters, average='micro')
    print(fscore)


def scenario_2():
    true_labels = ['B cell'] * 13 + ['T cell'] * 13
    clusters = ['A', 'A', 'B', 'C', 'C', 'D', 'D', 'D', 'E', 'F', 'F', 'F', 'F',
                'B', 'E', 'G', 'G', 'G', 'H', 'H', 'I', 'I', 'J', 'J', 'K', 'K']
    pred_labels = {
        'A': 'B cell',
        'B': 'T cell',
        'C': 'B cell',
        'D': 'B cell',
        'E': 'B cell',
        'F': 'B cell',
        'G': 'T cell',
        'H': 'T cell',
        'I': 'T cell',
        'J': 'T cell',
        'K': 'T cell'
    }
    pred_clusters = [pred_labels[x] for x in clusters]

    fscore = f1_score(true_labels, pred_clusters, average='micro')
    print(fscore)


scenario_1()

