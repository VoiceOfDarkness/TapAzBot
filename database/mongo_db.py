import os
from typing import List

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')


cluster = MongoClient(f'mongodb+srv://{username}:{password}@database.iirfppa.mongodb.net/?retryWrites=true&w=majority')
db = cluster['Tap_az']
collection = db['piano']


class Database:
    @staticmethod
    def insert_pianos(items: List):
        try:
            for item in items:
                filter_query = {'_id': item['_id']}
                update_data = {"$set": item}
                
                collection.update_one(filter_query, update_data, upsert=True)
                
        except Exception as e:
            return e

    @staticmethod
    def get_all_pianos():
        return collection.find({})
