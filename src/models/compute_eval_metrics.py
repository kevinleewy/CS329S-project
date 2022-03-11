from collections import Counter, defaultdict
import numpy as np

import os

import pickle5 as pickle
# import pickle



"""
ALL of the following must be directly in the BASE_PATH folder
- weights folders (all from the model_metadata)
- four catalogs
- webscraped images folder from drive
- embeddings folder from drive
- img folder for gallery (the URIs)
"""

BASE_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/deepfashion'
# # BASE_PATH = '/scratch/users/avento/deepfashion'

male_queries = [
    'express_111.jpg',
    'express_187.jpg',
    'gap_419.jpg',
    'ood_men_1.jpg',
    'ood_men_2.jpg',
    'zappos_112.jpg',
]

if __name__ == "__main__":

    obj = None
    data = defaultdict(lambda : {'y': 0, 'n': 0})

    with open(os.path.join(BASE_PATH, 'evals', 'eval_results_kevin.pickle'), 'rb') as handle:
        obj = pickle.load(handle)

    print(len(obj))

    for o in obj:
        img = o[0].split('/')[-1]
        if img not in male_queries:
            data[(o[1], o[3])][o[2]] += 1

    with open(os.path.join(BASE_PATH, 'evals', 'eval_results_anthony.pickle'), 'rb') as handle:
        obj = pickle.load(handle)

    print(len(obj))

    for o in obj:
        img = o[0].split('/')[-1]
        if img not in male_queries:
            data[(o[1], o[3])][o[2]] += 1

    for (model, dist), stats in sorted(data.items(), key=lambda x: x[0][0]):
        y_count = stats['y']
        n_count = stats['n']
        acc = y_count / (y_count + n_count) * 100
        print(f'{model} {dist} \'y\': {y_count} \'n\': {n_count} Acc: {acc:.2f}%')

# All queries
# Random in-distribution 'y': 13 'n': 117 Acc: 10.00%
# Random out-of-distribution 'y': 7 'n': 123 Acc: 5.38%
# model_13 in-distribution 'y': 44 'n': 86 Acc: 33.85%
# model_13 out-of-distribution 'y': 42 'n': 88 Acc: 32.31%
# model_36 in-distribution 'y': 35 'n': 95 Acc: 26.92%
# model_36 out-of-distribution 'y': 48 'n': 82 Acc: 36.92%
# model_36_aug in-distribution 'y': 43 'n': 87 Acc: 33.08%
# model_36_aug out-of-distribution 'y': 34 'n': 96 Acc: 26.15%
# unet_36_aug in-distribution 'y': 35 'n': 95 Acc: 26.92%
# unet_36_aug out-of-distribution 'y': 43 'n': 87 Acc: 33.08%

# Men queries only
# Random in-distribution 'y': 5 'n': 55 Acc: 8.33%
# Random out-of-distribution 'y': 4 'n': 56 Acc: 6.67%
# model_13 in-distribution 'y': 18 'n': 42 Acc: 30.00%
# model_13 out-of-distribution 'y': 16 'n': 44 Acc: 26.67%
# model_36 in-distribution 'y': 15 'n': 45 Acc: 25.00%
# model_36 out-of-distribution 'y': 22 'n': 38 Acc: 36.67%
# model_36_aug in-distribution 'y': 16 'n': 44 Acc: 26.67%
# model_36_aug out-of-distribution 'y': 12 'n': 48 Acc: 20.00%
# unet_36_aug in-distribution 'y': 9 'n': 51 Acc: 15.00%
# unet_36_aug out-of-distribution 'y': 18 'n': 42 Acc: 30.00%

# Women queries only
# Random in-distribution 'y': 8 'n': 62 Acc: 11.43%
# Random out-of-distribution 'y': 3 'n': 67 Acc: 4.29%
# model_13 in-distribution 'y': 26 'n': 44 Acc: 37.14%
# model_13 out-of-distribution 'y': 26 'n': 44 Acc: 37.14%
# model_36 in-distribution 'y': 20 'n': 50 Acc: 28.57%
# model_36 out-of-distribution 'y': 26 'n': 44 Acc: 37.14%
# model_36_aug in-distribution 'y': 27 'n': 43 Acc: 38.57%
# model_36_aug out-of-distribution 'y': 22 'n': 48 Acc: 31.43%
# unet_36_aug in-distribution 'y': 26 'n': 44 Acc: 37.14%
# unet_36_aug out-of-distribution 'y': 25 'n': 45 Acc: 35.71%

#                     |                 Accuracy (%)
#                     |      All      |     Men Only  |   Women Only  |
#                     |  ID   |  OOD  |  ID   |  OOD  |  ID   |  OOD  |
# ---------------------------------------------------------------------
# | baseline (random) | 10.00 |  5.38 |  8.33 |  6.67 | 11.43 |  4.29 |                 
# | model_13          | 33.85 | 32.31 | 30.00 | 26.67 | 37.14 | 37.14 |
# | model_36          | 26.92 | 36.92 | 25.00 | 36.67 | 28.57 | 37.14 |
# | model_36 (aug)    | 33.08 | 26.15 | 26.67 | 20.00 | 38.57 | 31.43 |
# | unet_36 (aug)     | 26.92 | 33.08 | 15.00 | 30.00 | 37.14 | 35.71 |