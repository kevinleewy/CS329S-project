# Standard Imports
import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

# Library Imports
import numpy as np
from tqdm import tqdm

# Project Imports
data_package_root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(data_package_root))
from data.database import FashionDatabase


class Config:
	DATA_HOME = Path(data_package_root)
	IMG_DIR = DATA_HOME / "img"
	METADATA_PATH = DATA_HOME / "catalog.json"
	EMBEDDINGS_PATH = DATA_HOME / "catalog_embeds.npy"


def init_database():
	database = FashionDatabase()

	with open(str(Config.METADATA_PATH), "r") as f:
		metadata = json.load(f)

	embeddings = np.load(str(Config.EMBEDDINGS_PATH))
	
	for item_metadata, item_embedding in tqdm(list(zip(metadata, embeddings))):
		data = {
			"name": item_metadata["Label"],
			"uri": item_metadata["URI"],
			"label": item_metadata["Label"],
			"category": item_metadata["Category"],
			"sex": item_metadata["Sex"],
			"rating": item_metadata["Rating"],
			"price": item_metadata["Price"],
			"owner": "app",
			"embedding": json.dumps(item_embedding.tolist()),
		}
		database.add_new_item(data)

	metadata_db = database.metadata_database.read_df()
	print(f"Metadata Database: {metadata_db.count()}\n")
	metadata_db.show(5)

	embeddings_db = database.embeddings_database.read_df()
	print(f"Embeddings Database: {embeddings_db.count()}\n")
	embeddings_db.show(5)


if __name__ == '__main__':
	init_database()
