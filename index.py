import pyttsx3
import speech_recognition as sr

class Echo_bot:
    chat_type = None

    def __init__(self):
        self.speaker = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.voices = self.speaker.getProperty('voices')
        # 3 and 4 are ukrainian voices
        self.selected_voice_index = 4


    def goodbuy(self, text):
        valid_farewell_phrases = ['до побачення', 'до зустрічі', 'на все добре']

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


    def listen_for_input(self):
        with self.microphone as source:
            print("Скажiть реплiку:")
            audio = self.recognizer.listen(source)
            try:
                user_input = self.recognizer.recognize_google(audio, language="uk-UA")
                return user_input
            except sr.UnknownValueError:
                print("Не розпiзнано")
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
            if self.chat_type == 1:
                command = input("Оберіть яку команду виконати? Змінити формат, швидкість, голос або гучність?")
            else :
                self.say("Оберіть яку команду виконати? Змінити формат, швидкість, голос або гучність?")
                command = self.listen_for_input()
            
            match command:
                case 'формат':
                    self.change_format()
                case 'швидкість':
                    self.change_tempo()
                case 'голос':
                    self.change_voice()
                case 'гучність':
                    self.change_loudness()
                case _:
                    self.say("команда не була обрана")
            

    def change_tempo(self):
        self.say("Назвіть значення, на яке змінити швидкість голосу")
        value = self.listen_for_input()
        self.speaker.setProperty('rate', value)
        self.say("Команда зміни швидкості виконана.")


    def change_loudness(self):
        self.say("Назвіть значення, на яке змінити гучність голосу")
        value = self.listen_for_input()
        self.speaker.setProperty('volume', value)
        self.say("Команда зміни гучності виконана.")
    

    def change_voice(self):
        self.say("Назвіть індекс, на який змінити голос")
        value = self.listen_for_input()
        isVoiceChanged = self.set_voice(value)
        if isVoiceChanged:
            self.say("Команда зміни голосу виконана.")
        else:
            self.say("Команда зміни голосу не виконана.")


    def change_format(self):
        if self.chat_type == '1':
            self.do_speaking_chat()
            self.say("Формат змінений на усний.")
        else:
            self.do_writting_chat()
            self.write("Формат змінений на письмовий.")


    def do_speaking_chat(self):
        while True:
            print("Скажiть щось або 'До побачення', щоб завершити.")
            user_input = self.listen_for_input()
            self.choose_command(user_input)
            answer = self.goodbuy(user_input)
            self.say(answer)
            if answer == 'Повертайся ще!':
                sys.exit()
            


    def do_writting_chat(self):
        while True:
            user_input = input("Введіть фразу або 'До побачення', щоб завершити: ")
            self.choose_command(user_input)
            answer = self.goodbuy(user_input)
            self.say(answer)
            if answer == 'Повертайся ще!':
                sys.exit()


    def run(self):
        print('Привiт!')

        if not self.chat_type:
            self.chat_type = input("Оберіть формат спілкування: 1 - текстовий, 2 - усний. ")

        while True:
            match self.chat_type:
                case '1': 
                    self.do_writting_chat()
                case '2':
                    self.do_speaking_chat()
                case _:
                    print("Оберіть формат спілкування (1 або 2)")
        


bot = Echo_bot()
bot.set_voice(bot.selected_voice_index)
bot.run()




    