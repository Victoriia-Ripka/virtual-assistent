import pymongo
import os
from dotenv import load_dotenv
import pymorphy2

load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")

greeting = ['привіт', 'добрий день', 'добрий ранок', 'добрий вечір', 'добридень']
goodbuy = ['на все добре', 'допобачення', 'до зустрічі', 'бувай', 'прощавай']
colors = ['білий', 'чорний', 'червоний', 'помаранчевий', 'жовтий', 'зелений', 'голубий', 'синій', 'фіолетовий']
brand = ['cx-30', '6', 'q4', 'v40', 's90', '500', '500x']
models = ['fiat', 'mazda', 'volvo', 'audi', 'ford']
available = ['у наявності', 'доступні', 'зайняті']
no = ['не', 'ні']
characteristic = ['бренд', 'фірма', 'марка', 'модель', 'колір', 'фірма', 'доступні', 'наявні', 'бренд', 'фірма', 'автомат', 'автоматична', 'мануальна', 'рік', 'ціна', 'вартість']
verb = ['хотіти', 'замовити', 'орендувати', 'купити', 'поїхати', 'виняйняти', 'потребувати']

class Assistent:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer(lang='uk')
        self.cars, self.managers, self.clients = self.connect_to_DB()


    def assist(self):
        self.greeting()
        while True:
            user_input = input()
            words = user_input.split()
            user_input_lemas = []
            query = []

            for word in words:
                try:
                    inflected_word = self.morph.parse(word)[0].inflect({'nomn'}).word
                    user_input_lemas.append(inflected_word)
                except AttributeError:
                    normalized_word = self.normalize_word(word)
                    if normalized_word in no or word in verb:
                        user_input_lemas.append(word)

            for word in user_input_lemas:
                if word in colors or word in brand or word in models or word in available or word in characteristic or word in no or word in verb:
                    query.append(word)


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