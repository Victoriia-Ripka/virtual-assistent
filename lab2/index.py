import pymongo
import os
from dotenv import load_dotenv
import pymorphy2

load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")

greetings = ['привіт', 'добрий день', 'добрий ранок', 'добрий вечір', 'добридень']
goodbyes = ['на все добре', 'допобачення', 'до зустрічі', 'бувай', 'прощавай']
colors = ['білий', 'чорний', 'червоний', 'помаранчевий', 'жовтий', 'зелений', 'голубий', 'синій', 'фіолетовий']
brands = ['cx-30', '6', 'q4', 'v40', 's90', '500', '500x']
models = ['fiat', 'mazda', 'volvo', 'audi', 'ford']
available = ['наявний', 'доступний', 'зайнятий', 'наявність', 'доступність']
no = ['не', 'ні']
order_object = ['авто', 'автівка', 'машина', 'автомобіль']
characteristics = ['бренд', 'фірма', 'марка', 'модель', 'колір', 'доступність', 'наявність', 'автомат', 'автоматичний', 'мануальний', 'рік', 'ціна', 'вартість']
verbs = ['хотіти', 'замовити', 'орендувати', 'купити', 'поїхати', 'виняйняти', 'потребувати']

class Assistent:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer(lang='uk')
        self.cars, self.managers, self.clients = self.connect_to_DB()


    def assist(self):
        self.greeting()
        while True:
            user_input = input()
            translation_table = str.maketrans("", "", ",.!?')")
            cleaned_input = user_input.translate(translation_table)
            words = cleaned_input.split()
            user_input_lemas = []
            query = []

            for word in words:
                try:
                    inflected_word = self.morph.parse(word)[0].inflect({'nomn'}).word
                    user_input_lemas.append(inflected_word)
                except AttributeError:
                    normalized_word = self.normalize_word(word)
                    if normalized_word in no or normalized_word in verbs or word in goodbyes:
                        user_input_lemas.append(word)

            for word in user_input_lemas:
                if word in colors or word in brands or word in models or word in available or word in characteristics or word in no or word in verbs or word in order_object:
                    query.append(word)

            if query:
                contains_other_words = any(word not in no for word in query)
                if contains_other_words:
                    self.analize_query(query)
                else:
                    self.analize_input(user_input_lemas)
            else:
                self.analize_input(user_input_lemas)


    def normalize_word(self, word):
        parsed_word = self.morph.parse(word)
        return parsed_word[0].normal_form


    def connect_to_DB(self):
        car_renting_service = pymongo.MongoClient(mongoDB_connection)
        db = car_renting_service["CarRentings"]
        cars = db["cars"]
        managers = db["managers"]
        clients = db['clients']

        return cars, managers, clients


    def greeting(self):
        print('Привіт, рад вас бачити. Чим вам допомогти?') 


    def analize_query(self, query):
        pass


    def analize_input(self, input):
        responses = []
        greeting = self.analyze_greeting(input)
        goodbye = self.analyze_goodbye(input)

        if greeting:
            responses.append("Вітаю вас знову.")
        if goodbye:
            responses.append("Звертайтеся ще.")


        if responses:
            print(" ".join(responses))
        else:
            print("Я не зрозумів вашого повідомлення. Я можу допомогти вам обрати машину для оренди")
    

    def analyze_greeting(self, words):
        for word in words:
            for greeting in greetings:
                if word in greeting.split():
                    return True
        return False
    

    def analyze_goodbye(self, words):
        for word in words:
            for goodbye in goodbyes:
                if word in goodbye.split():
                    return True
        return False


class Car:
    def __init__(self, brand, model, year, automat, color, available, cost):
        self.brand = brand
        self.model = model
        self.year = year
        self.automat = automat
        self.color = color
        self.available = available
        self.cost = cost

    def __str__(self):
        return f'{self.brand} {self.model}: {self.year}, {self.color}, {self.cost}'


def main():
    assistent = Assistent()
    assistent.assist()

main()