import pyttsx3
import speech_recognition as sr
import streamlit as st
import time


class Echo_bot:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        

    def goodbuy(self, text):
            if text.lower() == 'стоп':
                return 'Повертайся ще!'
            else:
                return text


    def write_request(self, text):
        with st.chat_message("user"):
            st.markdown(text)
        st.session_state.messages.append({"role": "user", "content": text}) 


    def write_response(self, text):
        time.sleep(1)

        if text.lower() == 'до побачення' or  text.lower() == 'стоп':
            with st.chat_message("assistant"):
                st.markdown("Повертайся ще!")
            st.session_state.messages.append({"role": "assistant", "content": "Повертайся ще!"})
        else:
            with st.chat_message("assistant"):
                st.markdown(text)
            st.session_state.messages.append({"role": "assistant", "content": text}) 


    def recognize_audio(self, audio):
        try:
            return self.recognizer.recognize_google(audio, language="uk-UA")
        except sr.UnknownValueError:
            return "Не розпiзнано"
    

    def say_request(self):
        with self.microphone as source:
            audio = self.recognizer.listen(source)
            user_input = self.recognize_audio(audio)
            return user_input


    def say_response(self, text):
        time.sleep(1)

        if self.engine._inLoop:
            self.engine.endLoop()

        if text.lower() == 'до побачення' or  text.lower() == 'стоп':
            self.engine.say("Повертайся ще!")
            with st.chat_message("assistant"):
                st.markdown("Повертайся ще!")
            st.session_state.messages.append({"role": "assistant", "content": "Повертайся ще!"})
        else:
            self.engine.say(text)
            with st.chat_message("assistant"):
                st.markdown(text)
            st.session_state.messages.append({"role": "assistant", "content": text})
            
        self.engine.runAndWait()


    def run(self):
        match bot_type:
            case 'текст-текст':
                if prompt := st.chat_input("Введіть фразу або 'стоп', щоб завершити:"):
                    self.write_request(prompt)

                    if prompt.lower() == 'стоп':
                        with st.chat_message("assistant"):
                            st.markdown("Повертайся ще!")
                        st.session_state.messages.append({"role": "assistant", "content": "Повертайся ще!"})
                        
                    else:
                        self.write_response(prompt)

            case 'текст-мова':
                if prompt := st.chat_input("Введіть фразу або 'стоп', щоб завершити:"):
                    self.write_request(prompt)
                    self.say_response(prompt)

            case 'мова-текст':
                st.write("Натисніть кнопку для запису")
                if st.button("Говоріть"):
                    user_input = self.say_request()
                    self.write_response(user_input)

            case 'мова-мова':
                st.write("Натисніть кнопку для запису")
                if st.button("Говоріть"):
                    user_input = self.say_request()
                    self.say_response(user_input)


st.title("Ехо-бот")
st.write('Привiт! Бот розробила студентка групи ТВ-13 Ріпка Вікторія')

bot_type = st.radio('Оберіть тип спілкування з ботом', ['текст-текст', 'текст-мова', 'мова-текст', 'мова-мова'])
volume = st.sidebar.slider(label="Гучність", value=0.5, min_value=0.0, max_value=1.0)
speed = st.sidebar.slider(label="Швидкість", value=150, min_value=100, max_value=300)
selected_voice_name = st.sidebar.radio("Голос", ['Anatol', 'Natalia'])

bot = Echo_bot()
bot.run()
bot.engine.setProperty('volume', volume)
bot.engine.setProperty('rate', speed)

voices = bot.engine.getProperty('voices')  
if selected_voice_name == 'Anatol':
    bot.engine.setProperty('voice', voices[3].id)
else:
    bot.engine.setProperty('voice', voices[4].id)

if st.sidebar.button("Застосувати налаштування"):
    bot.engine.stop()
    bot.engine = pyttsx3.init()
    voices = bot.engine.getProperty('voices')  

    bot.engine.setProperty('volume', volume)
    bot.engine.setProperty('rate', speed)
    if selected_voice_name == 'Anatol':
        bot.engine.setProperty('voice', voices[3].id)
    else:
        # st.write("Natalia", selected_voice_name, voices[4].id)
        bot.engine.setProperty('voice', voices[1].id)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
