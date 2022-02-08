# Library Imports
import numpy as np
import streamlit as st

# Project Imports
from frontend.landing import LandingPage
from models.dummy import Identity, Rotate


def main():
	st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
	model_callback = Rotate(45)
	LandingPage.setup(model_callback)


if __name__ == "__main__":
	main()
