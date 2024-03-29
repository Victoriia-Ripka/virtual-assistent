import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
mongoDB_connection = os.getenv("MONGODB_CONNECTION")

car_renting_service = pymongo.MongoClient(mongoDB_connection)
db = car_renting_service["CarRentings"]
cars = db["cars"]
all_cars = cars.find()

for car in all_cars:
    print(car)