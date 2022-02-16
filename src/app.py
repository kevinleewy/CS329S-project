# Standard Imports
import json
from pathlib import Path

# Library Imports
import numpy as np
import pandas as pd
import streamlit as st
import torch

# Project Imports
from common.file_utils import read_df
from data.database import FashionDatabase
from frontend.landing import LandingPage
from models.dataloader import load_datasets, get_data_transforms
from models.dummy import Identity, Rotate
from models.model import ResnetDummy
from models.recommender import KNearestRecommender
from models.utils import make_embedding_callback


class Config:
	NUM_LABELS = 13
	WEIGHTS_PATH = Path("models") / "2022-02-08_23-53-14/best_model.pt"
	DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
	VOTES_DF_PATH = "votes.csv"


class App:

	@classmethod
	@st.cache(allow_output_mutation=True)
	def get_model_callback(cls):
		# Database
		database = FashionDatabase()
		print(f"Metadata Database: {database.metadata_database.read_df().count()}")
		print(f"Embeddings Database: {database.embeddings_database.read_df().count()}")

		recommender = KNearestRecommender()
		embeddings_df = database.embeddings_database.read_df()
		embeddings_pdf = embeddings_df.toPandas()
		embeddings_pdf["embeddings"] = embeddings_pdf.embeddings_json.apply(lambda embedding_json: np.array(json.loads(embedding_json), dtype="float"))
		embeddings_data = np.array(embeddings_pdf["embeddings"].values.tolist())
		recommender.fit(embeddings_data)

		model = ResnetDummy(Config.NUM_LABELS, freeze_pretrain=False)
		model.load_state_dict(torch.load(Config.WEIGHTS_PATH, map_location=torch.device(Config.DEVICE)))
		model = model.to(Config.DEVICE)
		model.eval()
		transforms = get_data_transforms()["test"]

		def get_img_embedding(img):
			img = transforms(img).unsqueeze(0).to(Config.DEVICE)
			embedding = model.embed(img).cpu().detach().numpy().flatten()
			return embedding

		embedding_callback = make_embedding_callback(get_img_embedding)

		def model_callback(inputs):
			input_embeddings = embedding_callback(inputs)
			input_embeddings = [input_embeddings[0]] # work on single image for now
			recommendation_uuids = recommender.get_recommendations(input_embeddings, embeddings_pdf)
			recommendation_uuids = recommendation_uuids[0]
			votes_df = pd.DataFrame({"recommendation_uuid": recommendation_uuids})
			votes_df.to_csv(Config.VOTES_DF_PATH)
			recommendation_images = database.get_images(recommendation_uuids)
			return list(recommendation_images.values())

		return model_callback


	@classmethod
	def votes_callback(cls, votes):
		votes_df = read_df(Config.VOTES_DF_PATH)
		votes_df["vote"] = votes
		votes_df.to_csv(Config.VOTES_DF_PATH)


	@classmethod
	def run(cls):
		st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
		model_callback = cls.get_model_callback()
		LandingPage.setup(model_callback, cls.votes_callback)


if __name__ == "__main__":
	App.run()
