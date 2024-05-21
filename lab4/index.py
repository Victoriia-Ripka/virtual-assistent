from spacy_llm.util import assemble # type: ignore
import logging
import spacy_llm # type: ignore
import pymongo # type: ignore
from prettytable import PrettyTable # type: ignore
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv # type: ignore
import time

load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")

# spacy_llm.logger.addHandler(logging.StreamHandler())
# spacy_llm.logger.setLevel(logging.DEBUG)

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

class Assistent:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.cfg")
    paths = {
        "components.llm_ner.task.examples.path": str(Path(__file__).parent / "ner_examples.yml"),
        "components.llm_textcat.task.examples.path": str(Path(__file__).parent / "textcat_examples.json")
    }
    

    def __init__(self):
        self.set_key_env_var()
        self.nlp = assemble(config_path=self.config_path, overrides=self.paths)
        self.cars, self.managers, self.clients, self.feedback = self.connect_to_DB()
        self.questions_count = 0
        self.isManager = False
        self.order_query = {}
        self.intent = ''
      

    def assist(self):
        self.greeting()

        while True:
            user_input = input("Ви: ")
            time.sleep(1)

            try:
                doc = self.nlp(user_input)
                cats = self.identify_intent(user_input)
                intent = cats

                print("[INFO cats]", self.intent)
                print(f"[INFO Enteties] {[(ent.text, ent.label_) for ent in doc.ents]}")
                # for token in doc:
                #     print("[INFO token] ", token.text, token.lemma_, token.ent_type_)
                
                # завершення комунікації
                if intent == 'прощання':
                    print("Звертайтеся ще.")
                    self.cach = []
                    return 0

                # згідно до наміру - щось робити
                elif intent == 'орендувати':
                    self.analize_order(doc)
                elif intent in ["привітання", 'додаткова_інформація'] :
                    self.analize_specific_request(doc)
                elif intent in ["переглянути_машини", "оновити_базу_даних"]:
                    self.do_manage(doc)
                elif intent in ["переглянути_відгуки", "залишити_відгук"]:
                    self.analize_feedback()
                elif intent == 'нічого':
                    print("Я можу вам допомогти орендувати машину для власних потреб. \nОсь що ми маємо:")
                    result = self.cars.find({})
                    count = self.cars.count_documents({})
                    if count > 0:
                        self.show_cars(result)
            
            except ConnectionError as e:
                print(f"Connection error: {e}")
                return 0


    def greeting(self):
        print('Привіт, радий Вас бачити. Чим Вам допомогти?') 


    def set_key_env_var(self):
        api_key = os.getenv("OPENAI_API_KEY")
        os.environ['OPENAI_API_KEY'] = api_key


    def connect_to_DB(self):
        car_renting_service = pymongo.MongoClient(mongoDB_connection)
        db = car_renting_service["CarRentings"]
        cars = db["cars"]
        managers = db["managers"]
        clients = db['clients']
        feedback = db['feedback']

        return cars, managers, clients, feedback
    

    def identify_intent(self, user_input):
        with self.nlp.select_pipes(enable="llm_textcat"):
            doc = self.nlp(user_input)
            if not doc.cats:
                return "нічого"

            key_with_highest_probability = max(doc.cats, key=doc.cats.get)
            selected_intent = key_with_highest_probability if doc.cats[key_with_highest_probability] > 0 else 0
            if selected_intent:
                self.intent = selected_intent
                return selected_intent
      

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
    

    def do_manage(self, doc):
        if not self.isManager:
            are_you_manager = input("Чи ви менеджер? (так/ні): ")
            if are_you_manager.lower() == "так":
                manager_name = input("Як вас звати?: ")
                if self.is_manager(manager_name):
                    if self.intent == "переглянути_машини":
                        return self.check_cars_for_repair()
                    elif self.intent == "оновити_базу_даних":
                        return self.update_car()

                else:
                    print("Хтось тут мухлює. Ви не є менеджером нашої фірми.")
            else:
                print("Вибачте, тільки менеджери мають доступ до даної інформації.")
        
        else: 
            if self.intent == "переглянути_машини":
                return self.check_cars_for_repair()
            elif self.intent == "оновити_базу_даних":
                return self.update_car()

           
    def check_cars_for_repair(self):
        self.questions_count -= 1

        print("Ось список автомобілів, які потребують ремонту:")
        repair_cars = self.cars.find({"neededRemont": True})
        self.show_cars(repair_cars)

        self.close_manager_communication()
        return True


    def update_car(self):
        self.questions_count -= 1

        try:
            _, car_model = input("Введіть модель автомобіля, який потрібно оновити (наприклад, 'Fiat 500'): ").split()
            car = self.cars.find_one({"model": car_model, "neededRemont": True})

            if car:
                self.cars.update_one({"_id": car["_id"]}, {"$set": {"neededRemont": False}})
                self.cars.update_one({"_id": car["_id"]}, {"$set": {"available": True}})
                print("Статус ремонту для автомобіля оновлено успішно. Авто знову доступне до аренди")
            else:
                print("Автомобіль з такою моделлю та потребою у ремонті не знайдено.")
        except:
            print("Помилка вводу. Спробуйте ще раз. Введіть бренд і модель машини коректно")

        self.close_manager_communication()
        return True


    # Feedback part
    def analize_feedback(self):
        if self.intent == "переглянути_відгуки":
                self.review_feedback()
        elif self.intent == "залишити_відгук":
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


    # Order part for clients
    def analize_order(self, doc):
        mongo_query = {}
        car_brands = []

        with self.nlp.select_pipes(enable=["lemmatizer", "llm_ner"]):
            for ent in doc.ents:
                if ent.label_ == 'бренд':
                    brand = self.translate_brand(ent.text)
                    car_brands.append(brand)
                elif ent.label_ == 'модель':
                    mongo_query['model'] = ent.text
                elif ent.label_ == 'автомат':
                    mongo_query['automat'] = True
                elif ent.label_ == 'механіка':
                    mongo_query['automat'] = False
                elif ent.label_ == 'доступність':
                    mongo_query['available'] = True
                elif ent.label_ == 'колір':
                    color_doc = self.nlp(ent.text)
                    lemmatized_color = [token.lemma_ for token in color_doc]
                    print(lemmatized_color)
                    mongo_query['color'] = lemmatized_color[0] if lemmatized_color else ent.text

            if car_brands:
                mongo_query['brand'] = {"$in": car_brands}

            # print(mongo_query)
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
            if self.analyze_greeting():
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

            price = self.get_prices(doc, token)
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


    def analyze_greeting(self):
        return 'привітання' in self.intent


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


    def get_prices(self, doc, token): 
        
        if token.lemma_ in ['ціна', 'ціни', 'діапазон', 'ціньова']:
            prices = []
            for car in self.cars.find({}, {"_id": 0, "cost": 1}):
                prices.append(car['cost']['hour'])

            for token in doc:
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