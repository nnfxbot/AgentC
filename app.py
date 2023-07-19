import openai
import streamlit as st
from functions import *

with st.sidebar:
  st.session_state.system_message = st.text_area("System message", height = 200, value = "You are AC")
  if st.button("Start new chat"):
    st.session_state.messages = [{"role":"system", "content":st.session_state.system_message}]
  st.session_state.openai_model = st.selectbox("Model", options = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"])

st.title("Agent C")

#Initialise session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system", "content":st.session_state.system_message}]
    st.session_state["openai_model"] = "gpt-3.5-turbo"

#Display messages in chat history
for message in st.session_state.messages:
    if message["role"] not in ["system", "function"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#Handle user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            functions = functions,
            function_call = "auto"
        )
        while response.choices[0].finish_reason == "function_call":
            function_call = response.choices[0].message.function_call
            st.write(function_call)
            result = handle_function_call(function_call)
            st.session_state.messages.append({"role":"function", "name": function_call.name,
                "content":result})
            response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=st.session_state.messages,
                functions = functions,
                function_call = "auto"
            )   
        message = response.choices[0].get("message")
        st.markdown(message.content)
        st.session_state.messages.append(message)

with st.expander("Chat History"):
  st.write(st.session_state.messages)

            
