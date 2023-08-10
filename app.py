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

sys_msg = """Role: Investment portfolio manager,
Tone: Casual,
Format: Bullet,
Length: Concise,
Audience: CEO
"""

with st.sidebar:
    st.session_state.system_message = st.text_area("System message", height = 150, value = sys_msg)
    if st.button("Start new chat"):
        st.session_state.messages = [{"role":"system", "content":st.session_state.system_message}]
    st.session_state.openai_model = st.selectbox("Model", options = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"])
    st.session_state.max_history = st.slider("Max History", 2, 10, 2, 1)
    st.session_state.enable_functions = st.checkbox("Enable functions", value = False)
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
        model = "gpt-3.5-turbo-16k" if len(str(messages)) > 12000 else st.session_state.openai_model
        response = get_completion(model = model, messages = messages, enable_functions = st.session_state.enable_functions)
        while response.choices[0].finish_reason == "function_call" or len(messages) > 10:
            function_call = response.choices[0].message.function_call
            st.text(function_call)
            result = handle_function_call(function_call)
            st.json(result, expanded = False)
            messages.append({"role":"function", "name": function_call.name,
                "content": result})
            model = "gpt-3.5-turbo-16k" if len(str(messages)) > 12000 else st.session_state.openai_model
            response = get_completion(model = model, messages = messages, enable_functions = st.session_state.enable_functions)  
        message = response.choices[0].get("message")
        st.markdown(message.content)
        st.json(response, expanded = False)
        messages.append(message)

#Keep the last messages according to max history limit
max_history = st.session_state.max_history 
if len(messages) > max_history:
    messages = [messages[0]] + messages[-max_history:]

with st.expander("messages"):
    st.session_state.messages = messages
    st.write(st.session_state.messages)
    
streamlit_analytics.stop_tracking()


