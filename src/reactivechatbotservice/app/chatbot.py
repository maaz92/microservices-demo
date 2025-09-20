import streamlit as st
from utils import write_message
from langgraph_agent import generate_response, clear_chat
import uuid

# Page Config
st.set_page_config(
    page_title="Online Boutique",
    page_icon="🛒",  # Emoji icon for a shopping cart
    layout="centered",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.image("./images/Hipster_HeroLogoMaroon.svg", width='stretch')

st.title("Rachel, your shopping assistant")


def get_bot_intro_message():
    return {
        "role": "assistant",
        "content": "I am Rachel, I can help you with your shopping. How can I assist you today?"
    }


def write_bot_intro_message():
    st.session_state.messages = [
        get_bot_intro_message()
    ]


def create_new_chat_if_required():
    if 'chat_id' in st.session_state and st.session_state.chat_id is not None:
        return False
    st.session_state.chat_id = (
        st.query_params["user_id"]
        if "user_id" in st.query_params
        else str(uuid.uuid1())
    )
    # crud.create_new_chat(ChatCreate(id = st.session_state.chat_id, user_id = st.session_state.current_user.id,
    #                                 messages=[st.session_state.messages[0]]))
    return True


def append_message_to_chat():
    return None
    # crud.append_message_to_chat(st.session_state.chat_id, st.session_state.messages[-1])


def handle_submit(message):
    """
    Submit handler:
    """
    with st.spinner('Thinking...'):
        # Call the agent
        append_message_to_chat()
        response = generate_response(message)
        write_message('assistant', response)
        append_message_to_chat()


if "messages" not in st.session_state or st.session_state.messages == []:
    write_bot_intro_message()

for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

if question := st.chat_input("Ask something..."):
    write_message('user', question)
    if create_new_chat_if_required():
        user_id = st.session_state.chat_id
        question += '\n' + str({'user_id': user_id})
    handle_submit(question)

# Add a button below the chat input
if st.button("New Chat"):
    st.session_state.messages = []
    clear_chat()
    st.session_state.chat_id = None
    write_bot_intro_message()
    st.rerun()
