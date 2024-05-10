import spacy
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv
from prettytable import PrettyTable
import json

from spacy.pipeline import EntityRuler


load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")
gpt_key = os.getenv("OPENAI_API_KEY")


feedback_actions = ['переглянути', 'перевірити', 'подивитися', "покажи"]
feedback_options = ['відгук', 'пропозиція', 'побажання', 'скарга', 'відгуки', 'пропозиції', 'скарги', 'фідбек']
verbs = ['замовити', 'орендувати', 'поїхати', 'винайняти', 'потребувати']
update_database_words = ["оновити", "поремонтувати", "полагодити"]
remont = ['ремонт']
manager = ['працювати', 'менеджер', 'адміністратор', 'працівник']


greetings = ['привіт', 'добрий день', 'добрий ранок', 'добрий вечір', 'добридень']
goodbyes = ['на все добре', 'допобачення', 'до зустрічі', 'бувай', 'прощавай']
models = ['cx-30', '6', 'q4', 'v40', 's90', '500', '500x']
brand_translations = {
    'Фіат': 'Fiat',
    'Мазда': 'Mazda',
    'Вольво': 'Volvo',
    'Ауді': 'Audi',
    'Форд': 'Ford',
    'Тойота': 'Toyota',
    'Шкода': 'Skoda',
    'БМВ': 'BMW',
    'Рено': 'Renault',
    'Пежо': 'Peugeot',
    'Опель': 'Opel',
    'Нісан': 'Nissan',
    'Мітсубісі': 'Mitsubishi',
    'Мерседес Бенц': 'Mercedes Benz',
    'Мерседес': 'Mercedes',
    'Лексус': 'Lexus',
    'Кіа': 'KIA',
    'Інфініті': 'Infinity',
    'Хундай': 'Hyundai',
    'Хонда': 'Honda',
    'Сітроєн': 'Citroen',
    'Шевролет': 'Chevrolet',
    'Альфа ромео': 'Alfa Romeo'
}
available = ['наявний', 'доступний', 'зайнятий', 'наявність', 'доступність']
order_object = ['авто', 'автівка', 'машина', 'автомобіль']
automatic = ['автомат', 'автоматичний', 'автоматична', 'автоматичне', "механіка", "механічна", "механічний", "механічне"]
no_word = ['не', 'ні', "крім", "окрім"]
and_word = ['і', 'й', 'та']
or_word = ['або']

# Створення власних іменованих сутностей
def load_data_from_file(file):
    with open (file, 'r', encoding="utf-8") as f:
        data = json.load(f)
        return data

def create_entities(file, type):
    data = load_data_from_file(file)
    patterns = []
    for item in data:
        pattern = {
            'label': type,
            "pattern": item
        }
        patterns.append(pattern)
    return patterns

@spacy.Language.factory("car_brands_ruler")
def generate_rules(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/car_brands.json', 'CAR_BRANDS')
    ruler.add_patterns(patterns)
    return ruler


class Assistent:
    def __init__(self):
        # self.nlp = assemble("config.cfg")
        self.nlp = spacy.load("uk_core_news_lg")
        self.nlp.add_pipe("car_brands_ruler", before='ner')
        self.cars, self.managers, self.clients, self.feedback = self.connect_to_DB()
        self.questions_count = 0
        self.isManager = False
        self.order_query = {}
        self.cach = []


    def assist(self):
        self.greeting()

        while True:
            user_input = input("Ви: ")

            if user_input in goodbyes:
                print("Звертайтеся ще.")
                self.cach = []
                break

            doc = self.nlp(user_input)
            self.cach.append(user_input)
            intents = self.determinate_intent(doc)

            # згідно до наміру - щось робити
            print(intents)

            if not intents:
                print("Я можу вам допомогти орендувати машину для власних потреб. \nОсь що ми маємо:")
                result = self.cars.find({})
                count = self.cars.count_documents({})
                if count > 0:
                    self.show_cars(result)
            
            for intent in intents:
                if intent == 'make-order':
                    self.analize_order()
                # "update-database" "remont" "feedback" "manager"


            # for word in user_input_lemas: 
            #     if word in any(colors, brands, models, available, order_object):
            #         query.append(word)

            # if query:
            #         self.analize_query(query)
            # else:
            #     self.analize_input(user_input_lemas)
            

    # розпізнає намір клієнта / менеджера
    def determinate_intent(self, text):
        intents = []

        for token in text:
            # print(token.lemma_)
            if token.lemma_ in verbs:
                intents.append("make-order") 
            elif token.lemma_ in update_database_words:
                intents.append("update-database") 
            elif token.lemma_ in remont:
                intents.append("remont") 
            elif token.lemma_ in feedback_options or token.lemma_ in feedback_actions:
                intents.append("feedback") 
            elif token.lemma_ in manager:
                intents.append("manager") 
        
        return intents


    def greeting(self):
        print('Привіт, рад вас бачити. Чим вам допомогти?') 


    def ask_gpt(self, prompt):
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50 )
        return response.choices[0].text.strip()


    def connect_to_DB(self):
        car_renting_service = pymongo.MongoClient(mongoDB_connection)
        db = car_renting_service["CarRentings"]
        cars = db["cars"]
        managers = db["managers"]
        clients = db['clients']
        feedback = db['feedback']

        return cars, managers, clients, feedback
        

    # Feedback part
    def analize_feedback(self, words):
        for word in words:
            if word in feedback_options or word in feedback_actions:
                if word in feedback_actions:
                    self.review_feedback()
                    break
                else:
                    self.create_feedback()
    

    def create_feedback(self):
        title = input("Напишіть заголовок вашого зворотнього зв'язку: ")
        text = input("Напишіть коментар: ")
        
        feedback_data = {
            "title": title,
            "text": text,
            "timestamp": datetime.now()  
        }
        self.feedback.insert_one(feedback_data)
        print("Дякуємо за зворотній зв'язок. Ми робимо все можливе, щоб працювати краще і ви нам у цьому допомагаєте!")


    # Manager part
    def is_manager(self, manager_name):
        manager = self.managers.find_one({"name": manager_name})
        if manager is not None:
            self.isManager = True
        return self.isManager
        

    def close_manager_communication(self):
        answer = input("Чи менеджер закінчив свою роботу? так/ні: ")
        if answer.lower() == 'так':
            self.isManager = False


    def review_feedback(self):
        self.questions_count -= 1
        if not self.isManager:
            are_you_manager = input("Чи ви менеджер? (так/ні): ")
            if are_you_manager.lower() == "так":
                manager_name = input("Як вас звати?: ")
                if self.is_manager(manager_name):
                    print("Ось зворотній зв'язок від користувачів:")
                    for feedback in self.feedback.find():
                        print(feedback['title'], '\n', feedback['text'], '\n\n')
                    self.close_manager_communication()
                    # return True
                else:
                    print("Хтось тут мухлює. Ви не є менеджером нашої фірми.")
                    return False
            else:
                print("Вибачте, тільки менеджери мають доступ до даної інформації.")
                return False
        else:
            print("Ось зворотній зв'язок від користувачів:")
            for feedback in self.feedback.find():
                    print(feedback['title'], '\n', feedback['text'], '\n\n')
            self.close_manager_communication()
            # return True
       
           
    def check_cars_for_repair(self, words):
        self.questions_count -= 1

        if "ремонт" in words:
            if not self.isManager:
                are_you_manager = input("Чи ви менеджер? (так/ні): ")
                if are_you_manager.lower() == "так":
                    manager_name = input("Як вас звати?: ")

                    if self.is_manager(manager_name):
                        print("Ось список автомобілів, які потребують ремонту:")
                        repair_cars = self.cars.find({"neededRemont": True})
                        self.show_cars(repair_cars)
                        self.close_manager_communication()

                    else:
                        print("Хтось тут мухлює. Ви не є менеджером нашої фірми.")
                else:
                    print("Вибачте, тільки менеджери мають доступ до даної інформації.")

            else:
                print("Ось список автомобілів, які потребують ремонту:")
                repair_cars = self.cars.find({"neededRemont": True})
                self.show_cars(repair_cars)
                self.close_manager_communication()


    def update_car(self, words):
        self.questions_count -= 1

        for word in words:
            if word in update_database_words:
                if not self.isManager:
                    are_you_manager = input("Чи ви менеджер? (так/ні): ")
                    if are_you_manager.lower() == "так":
                        manager_name = input("Як вас звати?: ")

                        if self.is_manager(manager_name):
                            _, car_model = input("Введіть модель автомобіля, який потрібно оновити (наприклад, 'Fiat 500'): ").split()
                            car = self.cars.find_one({"model": car_model, "neededRemont": True})
                            if car:
                                self.cars.update_one({"_id": car["_id"]}, {"$set": {"neededRemont": False}})
                                self.cars.update_one({"_id": car["_id"]}, {"$set": {"available": True}})
                                print("Статус ремонту для автомобіля оновлено успішно. Авто знову доступне до аренди")
                            else:
                                print("Автомобіль з такою моделлю та потребою у ремонті не знайдено.")
                            self.close_manager_communication()

                        else:
                            print("Хтось тут мухлює. Ви не є менеджером нашої фірми.")
                    else:
                        print("Вибачте, тільки менеджери мають доступ до даної інформації.")

                else:
                    _, car_model = input("Введіть модель автомобіля, який потрібно оновити (наприклад, 'Fiat 500'): ").split()
                    car = self.cars.find_one({"model": car_model, "neededRemont": True})
                    if car:
                        self.cars.update_one({"_id": car["_id"]}, {"$set": {"neededRemont": False}})
                        self.cars.update_one({"_id": car["_id"]}, {"$set": {"available": True}})
                        print("Статус ремонту для автомобіля оновлено успішно. Авто знову доступне до аренди")
                    else:
                        print("Автомобіль з такою моделлю та потребою у ремонті не знайдено.")
                    self.close_manager_communication()


    # Order part for clients
    def analize_order(self):
        # print(self.cach)
        doc = self.nlp(self.cach[-1])
        mongo_query = {}

        for token in doc:
            # print(token.text, token.pos_, token.lemma_, token.ent_type_)
            if token.ent_type_ == 'CAR_BRANDS':
                brand = self.translate_brand(token.text)
                mongo_query['brand'] = brand
                print(mongo_query['brand'])

            # if token.lemma_ in colors:
            #     mongo_query['color'] = color
            if token.lemma_ in models:
                mongo_query['model'] = token
            if token.lemma_ in automatic:
                if token.lemma_ in ['автомат', 'автоматичний']:
                    mongo_query['automat'] = True
                else:
                    mongo_query['automat'] = False
            if token.lemma_ in available:
                if token.lemma_ in ['наявний', 'доступний', 'наявність', 'доступність'] :
                    mongo_query['available'] = True
                else:
                    mongo_query['available'] = False


        result = self.cars.find(mongo_query)
        count = self.cars.count_documents(mongo_query)
        if count > 0:
            print("Ми можемо запропонувати вам наступні варіанти:")
            self.show_cars(result)

            answer = input("Чи ви оформлюєте замовлення? так/ні: ")
            if answer.lower() == 'так':
                self.order_query = mongo_query
                self.make_order()
            else:
                print("Можете запитати про інші машини.")
        elif  count == 0:
            print("На разі ця машина у ремонті або її немає у наявності")
        else:
            print("Вибачте, за вашим запитом ми не знайшли відповідних машин. Спробуйте змінити якісь параметри пошуку!")


    def translate_brand(self, input):
        for brand in brand_translations:
            if brand in input.lower():
                return brand_translations[brand]
        return input 
    

    def show_cars(self, cars):
        table = PrettyTable()
        table.field_names = ["Brand", "Model", "Year", "Color", "Automatic", "Cost"]
        for car in cars:
                table.add_row([car['brand'], car['model'], car['year'], car['color'], car['automat'], car['cost']])

        print(table)


    def make_order(self):
        # ціна
        # порахувати вартість
        self.order_query['available'] = True
        result = self.cars.find(self.order_query)
        if not result:
            print("Вибачте, саме ця машина на разі зараз не доступна")
        else:
            age = int(input("Напишіть цифрою скільки вам років? "))
            if age >= 18 and age <= 65:
                license = input("Чи маєте ви водійське посвідчення? так/ні: ")
                if license.lower() == 'так':
                    car = self.cars.find_one(self.order_query)
                    if car:

                        self.cars.update_one({"_id": car["_id"]}, {"$set": {"available": False}})
                        self.cars.update_one({"_id": car["_id"]}, {"$set": {"neededRemont": True}})
                        self.order_query = {}
                        print("Вітаю, ви успішно орендували машину. Чи можу я вам ще чимсь допомогти?")
                    else:
                        print("Виникла помилка при оформленні замовлення. Спробуйте ще раз.")
                else:
                    print("Вибачте, ми не орендуємо машини особам, що не мають водійського права. ")
            else:
                print("Вибачте, ми не орендуємо машини особам молодшим 18 років, або старшим 65. ")

    # FAQ part
    def analize_input(self, input):
        self.analize_feedback(input)
        self.check_cars_for_repair(input)
        self.update_car(input)

        self.questions_count += 1
        responses = []
        greeting = self.analyze_greeting(input)
        goodbye = self.analyze_goodbye(input)
        colors = self.analyze_available_colors(input)
        models = self.analyze_available_models(input)
        brands = self.analyze_available_brands(input)
        available_cars = self.analyze_available_cars(input)
        automat = self.analyze_automatic_cars(input)
        prices = self.get_prices(input)

        if greeting:
            responses.append("Вітаю вас знову.")
        
        if colors:
            responses.append("У нас є машини у наступних кольорах: ")
            for color in colors:
                responses.append(f"{color}, ")
        if models:
            responses.append("У нас є наступні моделі машин: ")
            for brand, model in models:
                responses.append(f"{brand.capitalize()} {model}, ")
        if brands:
            responses.append("У нас є наступні марки машин: ")
            for brand in brands:
                responses.append(f"{brand.capitalize()}, ")
        if available_cars:
            responses.append("У нас є у наявності наступні машини: ")
            for brand, model in available_cars:
                responses.append(f"{brand.capitalize()} {model}, ")
        if automat:
            responses.append("Це те, що вам потрібно: ")
            for brand, model in automat:
                responses.append(f"{brand.capitalize()} {model}, ")
        if prices:
            responses.append("Ціна вказана у грн/год: ")
            if isinstance(prices, (int, float)):
                responses.append(str(prices))
            else:
                responses.append(", ".join(map(str, prices)))
            
        if goodbye:
            responses.append("Звертайтеся ще.")

        

        if responses:
            if self.questions_count % 3 == 2:
                responses.append("Може хочете орендувати одну із наших машин?")

            print(" ".join(responses))
            
        else:
            if not self.isManager:
                print("Я не зрозумів вашого повідомлення. Я можу допомогти вам обрати машину для оренди.")


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


    def analyze_available_colors(self, words):
        if "кольори" in words:
            colors = self.cars.distinct("color")
            return colors
        return False
    

    def analyze_available_models(self, words):
        if "модель" in words or "моделі" in words:
            car_models_with_brand = self.cars.find({}, {"_id": 0, "brand": 1, "model": 1})
            models = set((car["brand"], car["model"]) for car in car_models_with_brand)
            return models
        return False
    

    def analyze_available_brands(self, words):
        if "фірма" in words or 'бренд' in words or 'марка' in words or "фірми" in words or 'бренди' in words or 'марки' in words:
            brands = self.cars.distinct("brand")
            return brands
        return False
    

    def analyze_available_cars(self, words):
        if 'доступність' in words or 'наявність' in words or 'доступні' in words or 'наявні' in words:
            available_cars = self.cars.find({"available": True}, {"_id": 0, "brand": 1, "model": 1})
            available_cars = set((car["brand"], car["model"]) for car in available_cars)
            return available_cars 
        return False


    def analyze_automatic_cars(self, words):
        if 'автомат' in words or 'автоматичний' in words:      
            automatic_cars = self.cars.find({"automat": True}, {"_id": 0, "brand": 1, "model": 1})
            automatic_cars = set((car["brand"], car["model"]) for car in automatic_cars)
            return automatic_cars
        elif "механіка" in words or "механічна" in words:
            automatic_cars = self.cars.find({"automat": False}, {"_id": 0, "brand": 1, "model": 1})
            automatic_cars = set((car["brand"], car["model"]) for car in automatic_cars)
            return automatic_cars
        return False


    def get_prices(self, words): 
        if 'ціна' in words or 'діапазон' in words:
            prices = []
            for car in self.cars.find({}, {"_id": 0, "cost": 1}):
                prices.append(car['cost']['hour'])
            if 'мінімальна' in words or 'найнижча' in words or 'нийдешевша' in words:
                return self.get_minimum_price(prices)
            elif 'максимальна' in words or 'найвижча' in words or 'найдорожча' in words:
                return self.get_maximum_price(prices)
            elif 'середня' in words:
                return self.get_average_price(prices)
            elif 'діапазон' in words and 'ціньовий' in words:
                return self.get_price_range(prices)
            else:
                return prices
        return False


    def get_minimum_price(self, prices):
        return min(prices)


    def get_average_price(self, prices):
        return sum(prices) / len(prices)


    def get_maximum_price(self, prices):
        return max(prices)


    def get_price_range(self, prices):
        return f"від {min(prices)} до {max(prices)}"



def main():
    assistant = Assistent()
    assistant.assist()


main()