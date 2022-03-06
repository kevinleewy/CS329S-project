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
	NUM_RECOMMENDATIONS = 2


class KNearestRecommender:

	def __init__(self, n_neighbors=Config.NUM_RECOMMENDATIONS):
		self.n_neighbors = n_neighbors
		self.recommender = NearestNeighbors(n_neighbors=n_neighbors)


	def fit(self, embeddings):
		self.recommender.fit(embeddings)


	def get_recommendations(self, query_embedding, catalog_df):
		distances, indices = self.recommender.kneighbors(query_embedding)
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
