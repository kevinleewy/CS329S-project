
import numpy as np
import torch

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