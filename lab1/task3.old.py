import pyttsx3
import speech_recognition as sr
import streamlit as st
import uuid
import sys

class Echo_bot:

    def __init__(self):
        self.speaker = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.voices = self.speaker.getProperty('voices')
        # 3 and 4 are ukrainian voices
        self.selected_voice_index = 4
        self.set_voice(self.selected_voice_index)
        

    def goodbuy(self, text):
        valid_farewell_phrases = ['стоп', 'до зустрічі', 'на все добре']

        if text.lower() in valid_farewell_phrases:
            return 'Повертайся ще!'
        else:
            return text
    

    def listen_for_input(self):
        with self.microphone as source:
            self.speaker.say("Скажiть реплiку:")
            audio = self.recognizer.listen(source)
            try:
                user_input = self.recognizer.recognize_google(audio, language="uk-UA")
                st.write("Recognized:", user_input)
                # self.say(user_input)
                return user_input
            except sr.UnknownValueError:
                self.speaker.say("Не розпiзнано")
                return " "


    def get_available_voices(self):
        voices = self.speaker.getProperty('voices')
        for voice in voices:
            print(f"Voice: {voice.name}")
            print(f" - ID: {voice.id}")
            print(f" - Languages: {voice.languages}")
            print(f" - Gender: {voice.gender}")
            print(f" - Age: {voice.age}")
            print("\n")


    def set_voice(self, voice_index):
        if 0 <= int(voice_index) < len(self.voices):
            self.speaker.setProperty('voice', self.voices[int(voice_index)].id)
        else:
            self.write("Невiрний iндекс голосу")

    
    def say(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()

    
    def write(self, text):
        response = f"{text}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response}) 


    def handle_command_input(self):
        self.command_input = st.text_input("Оберіть яку команду виконати? Змінити швидкість, голос або гучність:")
        st.button("Виконати команду", on_click=self.execute_command)
        # st.chat_message("user").markdown(command)
        # st.session_state.messages.append({"role": "user", "content": command})
        # self.choose_command(command)


    def execute_command(self):
        if self.command_input:
            st.chat_message("user").markdown(self.command_input)
            st.session_state.messages.append({"role": "user", "content": self.command_input})
            self.choose_command(self.command_input)
            self.command_input = None


    def choose_command(self, input):
        if input == 'швидкість':
            self.change_tempo()
        elif input == 'голос':
            self.change_voice()
        elif input == 'гучність':
            self.change_loudness()
        else:
            self.write("команда не була обрана")
        # self.say("Оберіть яку команду виконати? Змінити формат, швидкість, голос або гучність?")
            

    def change_tempo(self):
        value = st.chat_input("Назвіть значення, на яке змінити швидкість голосу")

        if value:
            try:
                tempo_value = float(value)
                self.speaker.setProperty('rate', tempo_value)
                # st.chat_message("user").markdown(value)
                # st.session_state.messages.append({"role": "user", "content": value})
                self.write("Команда зміни швидкості виконана.")
            except ValueError:
                self.write("Невірний формат значення. Будь ласка, введіть число.")
        else:
            self.write("Команда зміни швидкості не виконана.")
        # self.say("Назвіть значення, на яке змінити швидкість голосу")
        # value = self.listen_for_input()
        # self.say("Команда зміни швидкості виконана.")


    def change_loudness(self):
        value = st.chat_input("Назвіть значення, на яке змінити гучність голосу")
        self.speaker.setProperty('volume', float(value))
        self.say("Команда зміни гучності виконана.")
        # self.say("Назвіть значення, на яке змінити гучність голосу")
        # value = self.listen_for_input()
        # self.speaker.setProperty('volume', value)
        # self.say("Команда зміни гучності виконана.")
    

    def change_voice(self):
        value = st.chat_input("Назвіть індекс, на який змінити голос")
        is_voice_changed = self.set_voice(int(value))
        if is_voice_changed:
            self.say("Команда зміни голосу виконана.")
        else:
            self.say("Команда зміни голосу не виконана.")
        # self.say("Назвіть індекс, на який змінити голос")
        # value = self.listen_for_input()
        # isVoiceChanged = self.set_voice(value)
        # if isVoiceChanged:
        #     self.say("Команда зміни голосу виконана.")
        # else:
        #     self.say("Команда зміни голосу не виконана.")


    def do_speaking_chat(self):
        self.say("Скажiть щось або 'стоп', щоб завершити.")
        self.choose_command(user_input)
        answer = self.goodbuy(user_input)
        self.say(answer)
        if answer == 'Повертайся ще!':
            sys.exit()
            

    def do_writing_chat(self):
        if user_input := st.chat_input("Введіть фразу або 'стоп', щоб завершити:"):
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            answer = self.goodbuy(user_input)

            if answer == 'Повертайся ще!':
                self.write(answer)
                self.should_stop = True
            
            # elif user_input.lower() == 'виконати команду':
            #     self.handle_command_input()
                
            else:
                self.write(answer)

            
    def run(self):
        st.title('Echo Bot')
        st.write('Привiт! Бот розробила студентка групи ТВ-13 Ріпка Вікторія')

        # available_voices = [voice.name for voice in self.voices]
        # voice_index = st.sidebar.selectbox("Обери голос", available_voices, index=available_voices.id)
        # self.set_voice(voice_index)

        # if "messages" not in st.session_state:
        #     st.session_state.messages = []

        # for message in st.session_state.messages:
        #     with st.chat_message(message["role"]):
        #         st.markdown(message["content"])

        # chat_type = st.radio("Оберіть формат спілкування:", ['Усний', 'Текстовий'])

        # if chat_type == 'Текстовий':
        #     self.do_writing_chat()
        # else:
        #     st.session_state.messages.append({"role": "user", "content": "Скажiть щось або 'стоп', щоб завершити."})
        #     self.speaker.say("Скажiть щось або 'стоп', щоб завершити.")

        #     with self.microphone as source:
        #         with st.chat_message("assistant"):
        #             st.markdown("Скажiть реплiку:")
        #         st.session_state.messages.append({"role": "assistant", "content": "Скажiть реплiку:"}) 
        #         self.speaker.say("Скажiть реплiку:")

        #         audio = self.recognizer.listen(source)
        #         try:
        #             user_input = self.recognizer.recognize_google(audio, language="uk-UA")
        #             st.write("Recognized:", user_input)
        #             self.speaker.say(user_input)
        #             # self.speaker.runAndWait()
                
        #         except sr.UnknownValueError:
        #             st.write("Не розпiзнано")
        #             self.speaker.say("Не розпiзнано")
        #             # self.speaker.runAndWait()


bot = Echo_bot()
bot.run()
    