from openai import OpenAI
import streamlit as st 

api_key = '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' # 
client = OpenAI(api_key=api_key)

st.title("Бот для спілкування")

if "openai_model" not in st.session_state:
  st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
  st.session_state["messages"] = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
     st.markdown(message["content"])


if prompt := st.chat_input("Введіть питання"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
  