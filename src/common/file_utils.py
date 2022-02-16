# Library Imports
import pandas as pd


def read_df(path, default=None):
	try:
		return pd.read_csv(path)
	except Exception as e:
		print(f"Ran into error with file path {path}:\n{e}")
		pass
	assert default is not None
	df = pd.DataFrame(default)
	df.to_csv(path)
	return df
