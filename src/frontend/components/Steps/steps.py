import os
import streamlit.components.v1 as components
from enum import Enum

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "steps",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "design/build")
    _component_func = components.declare_component("steps", path=build_dir)


class StepStatus(str, Enum):
    WAIT = "wait"
    PROCESS = "process"
    FINISH = "finish"


def steps(choose_status, find_status, explore_status, rate_status, key=None):
    component_value = _component_func(
        choose_status = choose_status, 
        find_status = find_status, 
        explore_status = explore_status, 
        rate_status = rate_status,
        key = key,
    )
    return component_value


if not _RELEASE:
    import streamlit as st

    st.subheader("Component with constant args")

    with st.container():
        st.markdown("---")
        _ = steps(
            choose_status = StepStatus.FINISH,
            find_status = StepStatus.FINISH,
            explore_status = StepStatus.PROCESS,
            rate_status = StepStatus.WAIT,
        )
        st.markdown("---")
    
    st.markdown("---")
    st.subheader("Component with variable args")

    find_status_input = st.text_input("Enter a status", value=StepStatus.FINISH.value)
    _ = steps(
        choose_status = StepStatus.FINISH,
        find_status = find_status_input,
        explore_status = StepStatus.PROCESS,
        rate_status = StepStatus.WAIT,
        key="variable_args"
    )
