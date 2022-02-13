# Standard Imports
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Project Imports
data_package_root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(data_package_root))
from common.config import Config as PipelineConfig
from common.image_utils import get_path_uri

# Spark
import findspark
findspark.init()

import pyspark
from pyspark.sql import SparkSession, Window
from pyspark.sql.types import *


spark = (
	SparkSession
	.builder
	.appName("CS329S_Project")
	.getOrCreate()
)


class Config:
	MODEL_VERSION = "1.0.0"

	DATA_HOME = Path(data_package_root)
	TMP_DATA_HOME = DATA_HOME / "tmp"
	os.makedirs(DATA_HOME, exist_ok=True)

	METADATA_DF_PATH_FN = lambda prefix, suffix, data_home=DATA_HOME: data_home / f"{prefix}metadata{suffix}"
	METADATA_DF_PATH = METADATA_DF_PATH_FN("", "")
	TMP_METADATA_DF_PATH = METADATA_DF_PATH_FN("", "_tmp", data_home=TMP_DATA_HOME)

	EMBEDDINGS_DF_PATH_FN = lambda prefix, suffix, data_home=DATA_HOME: data_home / f"{prefix}embeddings{suffix}"
	EMBEDDINGS_DF_PATH = EMBEDDINGS_DF_PATH_FN("", "")
	TMP_EMBEDDINGS_DF_PATH = EMBEDDINGS_DF_PATH_FN("", "_tmp", data_home=TMP_DATA_HOME)

	DEBUG = False #PipelineConfig.DEBUG


class Schema:
	METADATA_FALLBACK_FNS = {"timestamp": lambda: datetime.now()}
	METADATA_DF = StructType([
		StructField("uuid", StringType(), nullable=False),
		StructField("name", StringType(), nullable=True),
		StructField("uri", StringType(), nullable=True),
		StructField("timestamp", TimestampType(), nullable=True),
		StructField("label", StringType(), nullable=True),
		StructField("category", StringType(), nullable=True),
		StructField("sex", StringType(), nullable=True),
		StructField("rating", IntegerType(), nullable=True),
		StructField("price", StringType(), nullable=True),
		StructField("owner", StringType(), nullable=True),
	])

	EMBEDDINGS_DF = StructType([
		StructField("uuid", StringType(), nullable=False),
		StructField("embeddings_json", StringType(), nullable=False),
		StructField("model_version", StringType(), nullable=False),
	])


class Database:

	def __init__(self, path, tmp_path, path_fn, schema):
		self.path = path
		self.tmp_path = tmp_path
		self.path_fn = path_fn
		self.schema = schema
		self.init_df()


	def read_df(self):
		if Config.DEBUG:
			print("=" * 50, "START")
			print("READING PATH:", str(self.path / "*.parquet"))
		df = spark.read.parquet(str(self.path / "*"))
		if Config.DEBUG:
			print("=" * 50, "DONE")
		return df


	def write_df(self, df):
		if Config.DEBUG:
			print("=" * 50, "START")
			print("WRITING TO PATH:", str(self.path))
			print("COUNT:", df.count()) # remove from cache
		if self.path.exists():
			df.write.mode("overwrite").option("compression", "snappy").parquet(str(self.tmp_path))
			intermediate_tmp_path = self.path_fn("", f"_tmp_{datetime.now()}")
			os.rename(str(self.tmp_path), str(intermediate_tmp_path))
			os.rename(str(self.path), str(self.tmp_path))
			os.rename(str(intermediate_tmp_path), str(self.path))
		else:
			df.write.mode("overwrite").option("compression", "snappy").parquet(str(self.path))
		if Config.DEBUG:
			print("=" * 50, "DONE")


	def init_df(self):
		if Config.DEBUG:
			print("=" * 50, "START")
			print("INITIALIZING DF TO PATH:", str(self.path))
		if self.path.exists():
			try:
				df = self.read_df()
				count = df.count()
				if count > 0:
					if Config.DEBUG:
						print(f"Existing dataframe with {count} rows")
					return True
			except:
				pass
		if Config.DEBUG:
			print("=" * 50, "MAKING NEW ONE NOW")
		empty_rdd = spark.sparkContext.emptyRDD()
		df = spark.createDataFrame(data=empty_rdd, schema=self.schema)
		self.write_df(df)
		if Config.DEBUG:
			print(f"Created new dataframe with schema:\n")
			df.printSchema()
			df.show()
			print("=" * 50, "DONE")
		return True


	def add_row(self, row, df=None, save=False):
		if df is None:
			assert(self.path is not None)
			df = self.read_df()
		new_row = spark.createDataFrame([row], schema=self.schema)
		if Config.DEBUG:
			print("COUNT BEFORE ADD NEW ROW:", df.count())
		new_df = df.union(new_row)
		if Config.DEBUG:
			print("COUNT AFTER ADD NEW ROW:", new_df.count())
		if save:
			self.write_df(new_df)
			# new_df = self.read_df(self.path)
		return new_df


	def update_row(self, uuid, row, df=None, save=False):
		if df is None:
			assert(self.path is not None)
			df = self.read_df()
		new_df = self.add_row(
			row,
			df.filter(df.uuid != uuid),
			save = save,
		)
		return new_df


	def get_row(self, uuid, df=None):
		if df is None:
			assert(self.path is not None)
			df = self.read_df()
		uuid_subset = df.filter(df.uuid == uuid)
		if uuid_subset.count() == 0:
			return None
		uuid_row = uuid_subset.collect()[0]
		return uuid_row.asDict()


class MetadataDatabase(Database):

	def __init__(self, path, tmp_path, path_fn, schema):
		super().__init__(path, tmp_path, path_fn, schema)


class EmbeddingsDatabase(Database):

	def __init__(self, path, tmp_path, path_fn, schema):
		super().__init__(path, tmp_path, path_fn, schema)


class FashionDatabase:

	def __init__(self):
		self.metadata_database = MetadataDatabase(
			Config.METADATA_DF_PATH,
			Config.TMP_METADATA_DF_PATH,
			Config.METADATA_DF_PATH_FN,
			Schema.METADATA_DF,
		)
		self.embeddings_database = EmbeddingsDatabase(
			Config.EMBEDDINGS_DF_PATH,
			Config.TMP_EMBEDDINGS_DF_PATH,
			Config.EMBEDDINGS_DF_PATH_FN,
			Schema.EMBEDDINGS_DF,
		)


	def add_new_item(self, data, save=True):
		row_uuid = uuid4().hex
		
		def get_value(data, column):
			if column == "uuid":
				return row_uuid
			if column in data:
				return data[column]
			if column in Schema.METADATA_FALLBACK_FNS:
				return Schema.METADATA_FALLBACK_FNS[column]()
			return None
		
		metadata_row = [get_value(data, column) for column in Schema.METADATA_DF.names]
		self.metadata_database.add_row(metadata_row, save=save)
		if "embedding" in data:
			embedding_row = [row_uuid, data["embedding"], Config.MODEL_VERSION]
			self.embeddings_database.update_row(row_uuid, embedding_row, save=save)


	def get_images(self, uuids):
		img_uris = {}
		for uuid in uuids:
			uuid_row = self.metadata_database.get_row(uuid)
			img_uris[uuid] = get_path_uri(str(Path(data_package_root) / uuid_row["uri"]))
		return img_uris


if __name__ == "__main__":
	database = FashionDatabase()
	database.add_new_item({"embedding": ""})
	print(f"Metadata Database:\n")
	database.metadata_database.read_df().show()
	print(f"Embeddings Database:\n")
	database.embeddings_database.read_df().show()
