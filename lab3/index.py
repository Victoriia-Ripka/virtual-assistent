import spacy
from spacy.pipeline import EntityRuler
import pymongo
from prettytable import PrettyTable
import os
from datetime import datetime
from dotenv import load_dotenv
import json


load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")
gpt_key = os.getenv("OPENAI_API_KEY")


update_database_words = ["оновити", "поремонтувати", "полагодити"]
remont = ['ремонт']
# no_word = ['не', 'ні', "крім", "окрім"]
# and_word = ['і', 'й', 'та']
# or_word = ['або']
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
def generate_rules1(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/car_brands.json', 'BRAND')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("car_ruler")
def generate_rules2(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/car.json', 'CAR')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("car_models_ruler")
def generate_rules2(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/car.json', 'MODEL')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("car_characteristics_ruler")
def generate_rules3(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/characteristics.json', 'CHARACTERISTIC')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("greetings_ruler")
def generate_rules4(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/greetings.json', 'GREETING')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("goodbyes_ruler")
def generate_rules4(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/goodbyes.json', 'GOODBYE')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("f_act_ruler")
def generate_rules2(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/f_act.json', 'F_ACT')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("f_opt_ruler")
def generate_rules3(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/f_opt.json', 'F_OPT')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("order_ruler")
def generate_rules4(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/order.json', 'ORDER')
    ruler.add_patterns(patterns)
    return ruler

@spacy.Language.factory("manager_ruler")
def generate_rules4(nlp, name):
    ruler = EntityRuler(nlp)
    patterns = create_entities('data/manager.json', 'MANAGE')
    ruler.add_patterns(patterns)
    return ruler

class Assistent:
    def __init__(self):
        # self.nlp = assemble("config.cfg")
        self.nlp = spacy.load("uk_core_news_lg")
        self.nlp.add_pipe("car_brands_ruler", before='ner')
        self.nlp.add_pipe("car_models_ruler", before='ner')
        self.nlp.add_pipe("car_ruler", before='ner')
        self.nlp.add_pipe("car_characteristics_ruler", before='ner')
        self.nlp.add_pipe("greetings_ruler", before='ner')
        self.nlp.add_pipe("goodbyes_ruler", before='ner')
        self.nlp.add_pipe("f_act_ruler", before='ner')
        self.nlp.add_pipe("f_opt_ruler", before='ner')
        self.nlp.add_pipe("order_ruler", before='ner')
        self.nlp.add_pipe("manager_ruler", before='ner')
        self.cars, self.managers, self.clients, self.feedback = self.connect_to_DB()
        self.questions_count = 0
        self.isManager = False
        self.order_query = {}
        self.cach = []


    def assist(self):
        self.greeting()

        while True:
            user_input = input("Ви: ")
            doc = self.nlp(user_input)

            for token in doc:
                print("[INFO] ", token.text, token.pos_, token.lemma_, token.ent_type_)

            # завершення комунікації
            for token in doc:
                if token.ent_type_ == 'GOODBYE':
                    print("Звертайтеся ще.")
                    self.cach = []
                    return 0

            self.cach.append(user_input)
            intents = self.determinate_intent(doc)

            # згідно до наміру - щось робити
            print("[INFO intents] ", intents)

            if not intents:
                print("Я можу вам допомогти орендувати машину для власних потреб. \nОсь що ми маємо:")
                result = self.cars.find({})
                count = self.cars.count_documents({})
                if count > 0:
                    self.show_cars(result)
            
            for intent in intents:
                if intent == 'make-order':
                    self.analize_order(doc)
                if intent == 'specific-request':
                    self.analize_specific_request(doc)
                if intent == 'manager':
                    self.analize_specific_request(doc)
                if intent == 'feedback':
                    self.analize_feedback(doc)


    # розпізнає намір клієнта / менеджера
    def determinate_intent(self, text):
        intents = []

        for token in text:
            if token.ent_type_ == 'ORDER':
                # for word in user_input_lemas: 
                #     if word in any(colors, brands, models, available, order_object):
                #         query.append(word)
                intents.append("make-order") 
            elif token.lemma_ in ['який', 'ціна', 'діапазон'] or token.ent_type_ in ['GREETING', 'BRAND', 'MODEL', 'CHARACTERISTIC', 'CAR']:
                # COLORS?
                intents.append("specific-request") 
            elif token.ent_type_ in ['F_OPT', 'F_ACT']:
                intents.append("feedback") 
            elif token.ent_type_ == 'MANAGE' or token.lemma_ in remont or token.lemma_ in update_database_words:
                intents.append("manager") 
        
        return list(set(intents))


    def greeting(self):
        print('Привіт, рад вас бачити. Чим вам допомогти?') 


    # не працює на разі
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
    def analize_feedback(self, doc):
        for token in doc:
            if token.ent_type_ == 'F_ACT':
                self.review_feedback()
                break
            elif token.ent_type_ == 'F_OPT':
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
    def analize_order(self, doc):
        mongo_query = {}
        car_brands = []

        for token in doc:
            # print(token.text, token.pos_, token.lemma_, token.ent_type_)
            if token.ent_type_ == 'BRAND':
                brand = self.translate_brand(token.text)
                car_brands.append(brand)
            if token.pos_ == 'ADJ':
                mongo_query['color'] = token.lemma_
            if token.ent_type == 'MODEL':
                mongo_query['model'] = token
            if token.ent_type ==  'CHARACTERISTIC':
                if token.lemma_ in ['автомат', 'автоматичний']:
                    mongo_query['automat'] = True
                elif token.lemma_ in ['механіка', 'механічний']:
                    mongo_query['automat'] = False
                elif token.lemma_ in ['наявний', 'доступний', 'наявність', 'доступність'] :
                    mongo_query['available'] = True
                elif token.lemma_ in ['зайнятий']:
                    mongo_query['available'] = False

        if car_brands:
            mongo_query['brand'] = {"$in": car_brands}

        print(mongo_query)
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


    def make_order(self):

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


    def translate_brand(self, input):
        for brand in brand_translations:
            if brand == input.capitalize():
                return brand_translations[brand]
        return input 
    

    def show_cars(self, cars):
        table = PrettyTable()
        table.field_names = ["Brand", "Model", "Year", "Color", "Automatic", "Cost"]
        for car in cars:
                table.add_row([car['brand'], car['model'], car['year'], car['color'], car['automat'], car['cost']])

        print(table)


    # FAQ part
    def analize_specific_request(self, doc):
        self.questions_count += 1
        responses = []
        greeting = False
        colors = []
        models = []
        brands = []
        available_cars = []
        automatic_cars = []
        prices = None 

        for token in doc:
            if self.analyze_greeting(token):
                greeting = True

            color = self.analyze_available_colors(token)
            if color:
                colors.extend(color)

            model = self.analyze_available_models(token)
            if model:
                models.extend(model)

            brand = self.analyze_available_brands(token)
            if brand:
                brands.extend(brand)

            available = self.analyze_available_cars(token)
            if available:
                available_cars.extend(available)

            automatic = self.analyze_automatic_cars(token)
            if automatic:
                automatic_cars.extend(automatic)

            price = self.get_prices(token)
            if price:
                prices = price

        if greeting:
            responses.append("Вітаю вас знову.")
        if colors:
            responses.append("У нас є машини у наступних кольорах: ")
            for color in colors:
                responses.append(f"{color}, ")
            responses[-1] = responses[-1][:-2] + "."
        if brands:
            responses.append("У нас є наступні марки машин: ")
            for brand in brands:
                responses.append(f"{brand.capitalize()}, ")
            responses[-1] = responses[-1][:-2] + "."
        if models:
            responses.append("У нас є наступні моделі машин: ")
            for brand, model in models:
                responses.append(f"{brand.capitalize()} {model}, ")
            responses[-1] = responses[-1][:-2] + "."
        if available_cars:
            responses.append("У нас є у наявності наступні машини: ")
            for brand, model in available_cars:
                responses.append(f"{brand.capitalize()} {model}, ")
            responses[-1] = responses[-1][:-2] + "."
        if automatic_cars:
            responses.append("Це те, що вам потрібно: ")
            for brand, model in automatic_cars:
                responses.append(f"{brand.capitalize()} {model}, ")
            responses[-1] = responses[-1][:-2] + "."
        if prices:
            responses.append("Ціна вказана у грн/год: ")
            if isinstance(prices, (int, float)):
                responses.append(str(prices))
            elif isinstance(prices, str):
                responses.append(prices)
            else:
                responses.append(", ".join(map(str, prices)))

        if responses:
            if self.questions_count % 5 == 0:
                responses.append("Може хочете орендувати одну із наших машин?")
            print(" ".join(responses))
        else:
            if not self.isManager:
                print("Я не зрозумів вашого повідомлення. Я можу допомогти вам обрати машину для оренди.")


    def analyze_greeting(self, token):
        return token.ent_type_ == 'GREETING'


    def analyze_available_colors(self, token):
        if token.lemma_ == "колір":
            colors = self.cars.distinct("color")
            return colors
        return False
    

    def analyze_available_models(self, token):
        if token.lemma_ in ["модель", "моделі"]:
            car_models_with_brand = self.cars.find({}, {"_id": 0, "brand": 1, "model": 1})
            models = set((car["brand"], car["model"]) for car in car_models_with_brand)
            return models
        return False
    

    def analyze_available_brands(self, token):
        if token.lemma_ in ["фірма", 'бренд', 'марка', "фірми", 'бренди', 'марки']:
            brands = self.cars.distinct("brand")
            return brands
        return False
    

    def analyze_available_cars(self, token):
        if token.lemma_ in ['доступність', 'наявність', 'доступний', 'наявний']:
            available_cars = self.cars.find({"available": True}, {"_id": 0, "brand": 1, "model": 1})
            available_cars = set((car["brand"], car["model"]) for car in available_cars)
            return available_cars 
        return False


    def analyze_automatic_cars(self, token):
        if token.lemma_ in ['автомат', 'автоматичний']:      
            automatic_cars = self.cars.find({"automat": True}, {"_id": 0, "brand": 1, "model": 1})
            automatic_cars = set((car["brand"], car["model"]) for car in automatic_cars)
            return automatic_cars
        elif token.lemma_ in ['механіка', 'механічний']:
            automatic_cars = self.cars.find({"automat": False}, {"_id": 0, "brand": 1, "model": 1})
            automatic_cars = set((car["brand"], car["model"]) for car in automatic_cars)
            return automatic_cars
        return False


    def get_prices(self, token): 
        
        if token.lemma_ in ['ціна', 'діапазон']:
            prices = []
            for car in self.cars.find({}, {"_id": 0, "cost": 1}):
                prices.append(car['cost']['hour'])

            for token in self.nlp(self.cach[-1]):
                if token.lemma_ in ['мінімальний', 'найнижча', 'нийдешевша', "найнижчий"]:
                    return self.get_minimum_price(prices)
                elif token.lemma_ in ['максимальний', 'найвижча', 'найдорожча']:
                    return self.get_maximum_price(prices)
                elif token.lemma_ == 'середній':
                    return self.get_average_price(prices)
                elif token.lemma_ in ['діапазон', 'ціньовий', 'ціньова']:
                    return self.get_price_range(prices)
                
            return list(set(prices))
        return False


    def get_minimum_price(self, prices):
        return min(prices)


    def get_average_price(self, prices):
        return round(sum(prices) / len(prices), 2)


    def get_maximum_price(self, prices):
        return max(prices)


    def get_price_range(self, prices):
        return f"від {min(prices)} до {max(prices)}."



def main():
    assistant = Assistent()
    assistant.assist()


main()