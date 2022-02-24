# Standard Imports
import base64
from io import BytesIO

# Library Imports
import numpy as np
from PIL import Image

# Project Imports
from common.config import Config as PipelineConfig


def get_data(img):
  data = BytesIO()
  img.save(data, "png")
  return data.getvalue()


def get_uri(image):
  try:
    uri_data = base64.b64encode(image.img_data)
  except:
    uri_data = base64.b64encode(image)
  uri_data = uri_data.decode()
  return f"data:image/png;base64,{uri_data}"


def read_image(path):
  return Image.open(path)


def get_path_uri(path):
  image = read_image(path)
  image_data = get_data(image)
  uri = get_uri(image_data)
  return uri


class ImagePreprocessor:

  @classmethod
  def build_image_from_bytes(cls, img_data):
    return Image.open(BytesIO(img_data))


  @classmethod
  def run(cls, img_data, img_size):
    img = cls.build_image_from_bytes(img_data)
    return img.resize(img_size)


class InputImage:

  def __init__(self, img_data, filename):
    self.filename = filename
    self.orig_img_data = img_data
    self.img = ImagePreprocessor.run(img_data, PipelineConfig.INPUT_IMAGE_SIZE)
    self.img_data = get_data(self.img)


  def rotate(self, deg):
    self.img = self.img.rotate(deg)
    self.img_data = get_data(self.img)
    return self
