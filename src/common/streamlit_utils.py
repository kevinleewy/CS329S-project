# Library Imports
import streamlit as st


def read_from_session(name, default=None):
	if name not in st.session_state:
		st.session_state[name] = default
	return st.session_state[name]
