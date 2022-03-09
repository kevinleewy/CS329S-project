# Standard Imports
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Library Imports
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Project Imports
models_package_root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(models_package_root))
from common.config import Config as PipelineConfig


class Config:
	NUM_RECOMMENDATIONS = 200


class KNearestRecommender:

	def __init__(self, n_neighbors=Config.NUM_RECOMMENDATIONS):
		self.n_neighbors = n_neighbors
		self.recommender = NearestNeighbors(n_neighbors=2*n_neighbors)


	def fit(self, embeddings):
		self.recommender.fit(embeddings)


	def get_recommendations(self, query_embedding, catalog_df, eps=1e-8):
		distances, indices = self.recommender.kneighbors(query_embedding)
		final_indices, prev_distance = [], None
		for distance, index in zip(distances[0], indices[0]):
			if abs(distance - prev_distance) >= eps: # To ensure no catalog dupes
				prev_distance = distance
				final_indices.append(index)
				if len(final_indices) == self.n_neighbors:
					break
		return catalog_df.uuid.values[final_indices]


class KNearestRecommender2:

	def __init__(self, n_neighbors=Config.NUM_RECOMMENDATIONS):
		self.n_neighbors = n_neighbors


	def fit(self, embeddings):
		self.embeddings = embeddings


	def get_recommendations(self, query_embedding, catalog_df, eps=1e-8):
		distances = np.sum((self.embeddings - query_embedding.flatten()) ** 2, axis=0)
		distances[distances <= eps] = float("inf")
		sort_idxs, indices, prev_dist = np.argsort(distances), [], None
		for sort_idx in sort_idxs:
			curr_dist = distances[sort_idx]
			if curr_dist != prev_dist: # To ensure no catalog dupes
				prev_dist = curr_dist
				indices.append(sort_idx)
				if len(indices) == self.n_neighbors:
					break
		return catalog_df.uuid.values[indices]


class NoopPreferenceOptimizer:

	def __init__(self, *args, **kwargs):
		pass


	def optimize(self, preference_vector, *args, **kwargs):
		return preference_vector


class WeightedPreferenceOptimizer:

	def __init__(self, alpha=0.01):
		self.alpha = alpha
		self.one_min_alpha = 1. - alpha


	def optimize(self, preference_vector, image_embeddings, votes):
		preference_vector = np.array(preference_vector)
		for vote, embedding in zip(votes, image_embeddings):
			coeff = 1 if vote else -1
			preference_vector = self.one_min_alpha * preference_vector + self.alpha * np.array(embedding)
		return preference_vector.tolist()


# class SupervisedRecommender:
