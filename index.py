import pyttsx3
import speech_recognition as sr

class Echo_bot:
    input_type = '1' # текстовий (усний)
    chat_type = '3'  # змішаний (усний, письмовий)

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
    
    
    def say(self, text):
        self.speaker.say('Ехо-бот говорить!')
        self.speaker.say(text)
        self.speaker.runAndWait()

    
    def write(self, text):
        print("Ехо-бот пише: ", text)


    def bot_answer(self, text):
        if self.chat_type == '1':
            self.write(text)
        elif self.chat_type == '2':
            self.say(text)
        elif self.chat_type == '3':
            self.write(text)
            self.say(text)


    def listen_for_input(self):
        if self.input_type == '1':
            text = input()
            return text
        else:
            with self.microphone as source:
                audio = self.recognizer.listen(source)
                try:
                    user_input = self.recognizer.recognize_google(audio, language="uk-UA")
                    return user_input
                except sr.UnknownValueError:
                    self.bot_answer("Не розпiзнано")
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
        if 0 <= voice_index < len(self.voices):
            self.speaker.setProperty('voice', self.voices[voice_index].id)
            return 1
        else:
            print("Невiрний iндекс голосу")
            return 0


    def choose_command(self, input):
        if input == 'виконати команду':
            if self.chat_type == '1':
                self.write("Оберіть яку команду виконати? Змінити формат, ввід, швидкість, голос або гучність?")
                command = self.listen_for_input()
            elif self.chat_type == '2':
                self.write("Оберіть яку команду виконати? Змінити формат, ввід, швидкість, голос або гучність?")
                command = self.listen_for_input()
            else:
                self.say("Оберіть яку команду виконати? Змінити формат, ввід, швидкість, голос або гучність?")
                self.write("Оберіть яку команду виконати? Змінити формат, ввід, швидкість, голос або гучність?")
                command = self.listen_for_input()

            match command:
                case 'формат':
                    self.change_chat_format()
                case 'ввід':
                    # не розпізнає слово "ввід"
                    self.change_input_format()
                case 'швидкість':
                    self.change_tempo()
                case 'голос':
                    self.change_voice()
                case 'гучність':
                    self.change_loudness()
                case _:
                    self.bot_answer("Команда обрана не була.")
    

    def change_tempo(self):
        self.bot_answer("Назвіть значення, на яке змінити швидкість голосу")
        value = self.listen_for_input()
        self.speaker.setProperty('rate', value)
        self.bot_answer("Команда зміни швидкості виконана.")


    def change_loudness(self):
        self.bot_answer("Назвіть значення, на яке змінити гучність голосу")
        value = self.listen_for_input()
        self.speaker.setProperty('volume', value)
        self.bot_answer("Команда зміни гучності виконана.")
    

    def change_voice(self):
        self.bot_answer("Назвіть індекс, на який змінити голос")
        value = self.listen_for_input()
        isVoiceChanged = self.set_voice(int(value))
        if isVoiceChanged:
            self.bot_answer("Команда зміни голосу виконана.")
        else:
            self.bot_answer("Команда зміни голосу не виконана.")


    def change_input_format(self):
        if self.input_type == '1':
            self.input_type = '2'
        else:
            self.input_type = '1'

        self.bot_answer("Змінений спосіб вводу")
    

    def change_chat_format(self):
        if self.chat_type == '1':
            self.write("Оберіть формат: текстовий, усний, змішаний")
            type = self.listen_for_input()
        elif self.chat_type == '2':
            self.write("Оберіть формат: текстовий, усний, змішаний")
            type = self.listen_for_input()
        else:
            self.say("Оберіть формат: текстовий, усний, змішаний")
            self.write("Оберіть формат: текстовий, усний, змішаний")
            type = self.listen_for_input()

        match type:
            case 'текстовий':
                self.bot_answer("Формат змінений на письмовий.")
                self.do_writting_chat()
                
            case 'усний':
                self.bot_answer("Формат змінений на усний.")
                self.do_speaking_chat()
                
            case 'змішаний':
                self.bot_answer("Формат змінений на змішаний.")
                self.do_mixed_chat()
                

    def do_speaking_chat(self):
        while True:
            if self.input_type == '1':
                self.say("Введіть фразу або 'стоп', щоб завершити.")
            else:
                self.say("Скажiть щось або 'стоп', щоб завершити.")

            user_input = self.listen_for_input()

            answer = self.goodbuy(user_input)
            self.bot_answer(answer)
            self.choose_command(user_input)
            
            if answer == 'Повертайся ще!':
                break


    def do_mixed_chat(self):
        while True:
            if self.input_type == '1':
                self.write("Введіть фразу або 'стоп', щоб завершити.")
                self.say("Введіть фразу або 'стоп', щоб завершити.")
            else:
                self.write("Скажiть щось або 'стоп', щоб завершити.")
                self.say("Скажiть щось або 'стоп', щоб завершити.")

            user_input = self.listen_for_input()
            
            answer = self.goodbuy(user_input)
            self.bot_answer(answer)
            self.choose_command(user_input)
            
            if answer == 'Повертайся ще!':
                break

            
    def do_writting_chat(self):
        while True:
            if self.input_type == '1':
                self.write("Введіть фразу або 'стоп', щоб завершити: ")
            else:
                self.write("Скажiть щось або 'стоп', щоб завершити.")

            user_input = self.listen_for_input()

            answer = self.goodbuy(user_input)
            self.bot_answer(user_input)
            self.choose_command(user_input)

            if answer == 'Повертайся ще!':
                break


    def run(self):
        print('Привiт!')

        match self.chat_type:
            case '1': 
                self.do_writting_chat()
            case '2':
                self.do_speaking_chat()
            case '3':
                self.do_mixed_chat()


bot = Echo_bot()
bot.run()

    