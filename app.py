import openai
import streamlit as st
from functions import *
import json
import streamlit_analytics

streamlit_analytics.start_tracking()

st.set_page_config(layout="wide")
st.markdown("""
<style>
    [data-testid=stSidebar] {background-color: #000000;}
</style>
""", unsafe_allow_html=True)

sys_msg = """Role: Expert coder
Tone: Casual
Format: Bullet points
Length of response: under 100 tokens"""



with st.sidebar:
    st.session_state.system_message = st.text_area("System message", height = 150, value = sys_msg)
    if st.button("Start new chat"):
        st.session_state.messages = [{"role":"system", "content":st.session_state.system_message}]
    st.session_state.openai_model = st.selectbox("Model", options = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"])
    st.session_state.max_history = st.slider("Max History", 2, 10, 2, 1)
    st.markdown(">## Created by AC ")
    

st.title("Agent C")

#Initialise session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":sys_msg}]
    st.session_state["openai_model"] = "gpt-3.5-turbo"

#Display messages in chat history
messages = st.session_state.messages
for message in messages:
    if message["role"] not in ["system", "function"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#Handle user input
if prompt := st.chat_input("What is up?"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=messages,
            functions = functions,
            function_call = "auto")
        while response.choices[0].finish_reason == "function_call" or len(messages) > 10:
            function_call = response.choices[0].message.function_call
            st.markdown(function_call)
            result = handle_function_call(function_call)
            st.json(result, expanded = False)
            messages.append({"role":"function", "name": function_call.name,
                "content": json.dumps(result)})
            response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=messages,
                functions = functions,
                function_call = "auto")   
        message = response.choices[0].get("message")
        st.markdown(message.content)
        st.json(response, expanded = False)
        messages.append(message)

with st.expander("messages"):
    st.write(messages)
#Keep the last messages according to max history limit
max_history = st.session_state.max_history 
if len(messages) > max_history:
    messages = [messages[0]] + messages[-max_history:]
st.session_state.messages = messages

streamlit_analytics.stop_tracking()


