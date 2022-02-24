import numpy as np
import torch
from sklearn.metrics import f1_score

def compute_imbalanced_class_weights(samples_per_cls, normalize=False, as_tensor=False):
    """Computes the weights for classification loss for imbalanced classes.
        Ref: https://arxiv.org/pdf/1901.05555.pdf
    Args:
        samples_per_cls: (int[]) number of samples per class
        normalize: (bool) Whether or not to normalize weights,
            such that weights sum to 1.
        as_tensor: (bool) To return the result as a tensor instead
            of a numpy array of floats.
    Returns:
        (float[] | Tensor) class weights with the same dim as samples_per_cls.
            normalized if normalize=True
    """

    N = sum(samples_per_cls)
    beta = (N - 1) / N
    effective_num = (1.0 - np.power(beta, samples_per_cls)) / (1.0 - beta)
    weights = 1 / (np.array(effective_num) + 1e-12)

    if normalize:
        weights = weights / np.sum(weights)

    if as_tensor:
        weights = torch.tensor(weights, dtype=torch.float)
    
    return weights


def compute_f1(targets, predictions, avg_per_attribute=True):
    if avg_per_attribute:
        attr_f1s = []

        # Iterate through each attribute and compute F1
        for target, pred in zip(targets.T, predictions.T):
            attr_f1s.append(f1_score(target, pred, zero_division=0))
        
        # Now average
        f1 = np.sum(attr_f1s) / len(attr_f1s)
    else:
        f1 = f1_score(targets.flatten(), predictions.flatten())
    
    return f1


def make_embedding_callback(model):
    def callback(inputs):
        return [model(img.img) for img in inputs]
    return callback
