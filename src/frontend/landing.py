# Standard Imports
import os
import sys
import random
import time
from datetime import datetime
from enum import Enum

# Library Imports
import numpy as np
import streamlit as st

# Project Imports
from common.config import Config as PipelineConfig
from common.image_utils import get_uri, InputImage
from common.streamlit_utils import read_from_session
from .components import image_carousel, steps, StepStatus, swipable_cards


class DisplayDirections(str, Enum):
  HORIZONTAL = "horizontal"
  VERTICAL = "vertical"


class Config:
  DEBUG = PipelineConfig.DEBUG
  MULTIPLE_IMAGES = False
  IMAGE_CAROUSELS_DIRECTION = DisplayDirections.VERTICAL


class LandingPage:
  UPDATE_INPUT_CONTAINER = False
  RUN_BUTTON = None
  RATE_BUTTON = None
  RESTART_BUTTON = None

  STEPS_STATUSES = {
    "choose_status": StepStatus.PROCESS,
    "find_status": StepStatus.WAIT,
    "explore_status": StepStatus.WAIT,
    "rate_status": StepStatus.WAIT,
  }


  @classmethod
  def set_current_step(cls, current_step):
    order, found_current_step = ["choose_status", "find_status", "explore_status", "rate_status"], False
    for step in order:
      if not found_current_step and (step == current_step):
        found_current_step = True
        cls.STEPS_STATUSES[step] = StepStatus.PROCESS
      elif not found_current_step:
        cls.STEPS_STATUSES[step] = StepStatus.FINISH
      elif found_current_step:
        cls.STEPS_STATUSES[step] = StepStatus.WAIT


  @classmethod
  def build_steps_header(cls):
    cls.steps_placeholder.empty()
    cls.update_steps_header()
    with cls.steps_placeholder:
      _ = steps(
        choose_status = cls.STEPS_STATUSES["choose_status"],
        find_status = cls.STEPS_STATUSES["find_status"],
        explore_status = cls.STEPS_STATUSES["explore_status"],
        rate_status = cls.STEPS_STATUSES["rate_status"],
        key = f'{cls.STEPS_STATUSES["choose_status"]}_{cls.STEPS_STATUSES["find_status"]}_{cls.STEPS_STATUSES["explore_status"]}_{cls.STEPS_STATUSES["rate_status"]}',
      )


  @classmethod
  def update_steps_header(cls, current_step_override=None):
    current_step = current_step_override
    if current_step is None:
      if "current_step" in st.session_state:
        current_step = st.session_state.current_step
      else:
        current_step = "choose_status"
    st.session_state.current_step = current_step
    cls.set_current_step(st.session_state.current_step)


  @classmethod
  def update_image_row(cls, placeholder, img_uris, key, texts=None, build_header_fn=lambda: None):
    with placeholder.container():
      build_header_fn()
      # img_uris = [get_uri(img) for img in imgs]
      image_carousel(img_uris, texts=texts, key=key)


  @classmethod
  def build_input_row_header(cls):
    st.write("##### Input Images")
    # cls.RUN_BUTTON = st.button("Run Model", key="run_model")


  @classmethod
  def build_output_row_header(cls):
    st.write("##### Output Images")
    # cls.RATE_BUTTON = st.button("Rate Recommendations", key="rate_fits")


  @classmethod
  def build_input_component(cls, upload_placeholder, input_placeholder, input_imgs):
    with upload_placeholder.container():
      upload_columns = st.columns(2)
      if Config.MULTIPLE_IMAGES:
        with upload_columns[0].empty():
          uploaded_files = st.file_uploader("", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
          for uploaded_file in uploaded_files:
            img = InputImage(uploaded_file.getvalue(), uploaded_file.name)
            input_imgs.append(img)
        with upload_columns[1].empty():
          picture = st.camera_input("", key="input_camera")
          if picture:
            img = InputImage(picture.getvalue(), f"camera_picture_{datetime.now()}")
            input_imgs.append(img)
      else:
        with upload_columns[0].empty():
          uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])
          if uploaded_file is not None:
            img = InputImage(uploaded_file.getvalue(), uploaded_file.name)
            input_imgs.append(img)
    return input_imgs


  @classmethod
  @st.cache
  def get_output_images(cls, input_imgs, model_callback):
    output_imgs = model_callback(input_imgs)
    return output_imgs


  @classmethod
  def restart_pipeline(cls):
    st.session_state.current_step = "choose_status"
    st.session_state.output_imgs = []
    st.session_state.votes = []


  @classmethod
  def setup(cls, model_callback, votes_callback):
    st.title("🧥 FashFlix")
    cls.steps_placeholder = st.empty()
    if "current_step" not in st.session_state:
      cls.update_steps_header(current_step_override="choose_status")
    cls.build_steps_header()

    button_columns = st.columns(5)
    st.write(" ")
    
    main_placeholder = st.empty()
    if st.session_state.current_step in ["choose_status", "find_status", "explore_status"]:
      main_placeholder.empty()
      with main_placeholder.container():
        image_carousels_placeholder = st.empty()
        with image_carousels_placeholder.container():
          if Config.IMAGE_CAROUSELS_DIRECTION == DisplayDirections.HORIZONTAL:
            input_placeholder_col, _, output_placeholder_col = st.columns([7, 1, 7])
            with input_placeholder_col:
              input_placeholder = st.empty()
            with output_placeholder_col:
              output_placeholder = st.empty()
          elif Config.IMAGE_CAROUSELS_DIRECTION == DisplayDirections.VERTICAL:
            input_placeholder = st.empty()
            output_placeholder = st.empty()
          else:
            raise Exception(f"Undefined IMAGE_CAROUSELS_DIRECTION = {Config.IMAGE_CAROUSELS_DIRECTION}, please fix in Config.")
        upload_placeholder = st.empty()

    # Get Inputs
    if st.session_state.current_step in ["choose_status"]:
      st.session_state.input_imgs = cls.build_input_component(upload_placeholder, input_placeholder, [])

    if st.session_state.current_step in ["choose_status"]:
      with button_columns[0]:
        cls.RUN_BUTTON = st.button(
          "Run Model",
          key = "run_model",
          on_click = lambda: cls.update_steps_header(current_step_override="find_status"),
          disabled = (len(read_from_session("input_imgs", [])) <= 0) or (len(read_from_session("output_imgs", [])) > 0),
        )

    # Visualize Inputs
    if st.session_state.current_step in ["choose_status", "find_status", "explore_status"]:
      if len(read_from_session("input_imgs", [])) > 0:
        cls.update_image_row(
          input_placeholder,
          [get_uri(img) for img in st.session_state.input_imgs],
          key="input_imgs_row",
          build_header_fn = cls.build_input_row_header,
        )
    
    # Get Model Outputs
    if st.session_state.current_step in ["find_status"]:
      st.session_state.output_imgs = cls.get_output_images(st.session_state.input_imgs, model_callback)
      cls.update_steps_header(current_step_override="explore_status")

    # Visualize Model Outputs
    if st.session_state.current_step in ["explore_status"]:
      cls.build_steps_header()
      img_details = [(img["uri"], img["price"]) for img in st.session_state.output_imgs]
      img_uris, details_texts = zip(*img_details)
      with output_placeholder.container():
        cls.update_image_row(
          output_placeholder,
          img_uris,
          key = "output_imgs_row",
          texts = details_texts,
          build_header_fn = cls.build_output_row_header,
        )

    if st.session_state.current_step in ["explore_status"]:
      with button_columns[3]:
        cls.RATE_BUTTON = st.button(
          "Rate Recommendations",
          key = "rate_fits",
          on_click = lambda: cls.update_steps_header(current_step_override="rate_status"),
          disabled = (len(read_from_session("output_imgs", [])) <= 0) or (st.session_state.current_step in ["rate_status"]),
        )
    
    # Rate Model Outputs
    if st.session_state.current_step in ["rate_status"]:
      read_from_session("votes", [])
      main_placeholder.empty()
      img_uris = [img["uri"] for img in st.session_state.output_imgs[::-1]] # currently ordered by recommendation score
      with main_placeholder.container():
        vote = swipable_cards(
          img_uris,
          last_card_emoji = "🧥",
          key = "output_swipable_cards",
        )
        if vote is not None:
          st.session_state.votes += [vote]
          if Config.DEBUG:
            st.write(f"votes: {st.session_state.votes}")

      if len(st.session_state.votes) == len(st.session_state.output_imgs):
        votes_callback(st.session_state.votes)
        # Rated all images
        with button_columns[0]:
          cls.RESTART_BUTTON = st.button(
            "Back Home",
            key = "restart_process",
            on_click = lambda: cls.restart_pipeline(),
          )
