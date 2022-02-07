# Standard Imports
import copy
import time

# Library Imports
import numpy as np


class Identity:
	def __call__(self, inputs, sleep=False, **kwargs):
		time.sleep(5)
		return inputs


class Rotate:
	def __init__(self, deg):
		self.deg = deg

	def __call__(self, inputs, **kwargs):
		# time.sleep(5)
		return [copy.copy(image).rotate(self.deg) for image in inputs]
