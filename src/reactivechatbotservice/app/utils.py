import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})
    # Write to UI
    with st.chat_message(role):
        st.markdown(content, unsafe_allow_html=True)

def get_session_id():
    return get_script_run_ctx().session_id

def get_user_id():
    return st.session_state.chat_id
