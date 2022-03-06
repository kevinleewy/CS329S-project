# Standard Imports
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Library Imports
from sklearn.neighbors import NearestNeighbors

# Project Imports
models_package_root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(models_package_root))
from common.config import Config as PipelineConfig


class Config:
	NUM_RECOMMENDATIONS = 10


class KNearestRecommender:

	def __init__(self, n_neighbors=Config.NUM_RECOMMENDATIONS):
		self.n_neighbors = n_neighbors
		self.recommender = NearestNeighbors(n_neighbors=n_neighbors)


	def fit(self, embeddings):
		self.recommender.fit(embeddings)


	def get_recommendations(self, query_embedding, catalog_df):
		distances, indices = self.recommender.kneighbors(query_embedding)
		return catalog_df.uuid.values[indices]
