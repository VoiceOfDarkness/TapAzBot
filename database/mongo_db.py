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
users_collection = db['users']


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
users_collection = db['users']


class Database:
    @staticmethod
    def insert_items(user_id, items: List):
        try:
            for item in items:
                item['user_id'] = user_id
                filter_query = {'_id': item['_id'], 'user_id': user_id}
                update_data = {"$set": item}
                
                collection.update_one(filter_query, update_data, upsert=True)
                
        except Exception as e:
            return e

    @staticmethod
    def get_all_items(user_id):
        return collection.find({'user_id': user_id})
    
    @staticmethod
    def delete_all_items(user_id):
        collection.delete_many({'user_id': user_id})

    @staticmethod
    def get_user_last_viewed_index(user_id):
        user_data = users_collection.find_one({"user_id": user_id})
        return user_data.get("last_viewed_index", 0)

    @staticmethod
    def set_user_last_viewed_index(user_id, last_viewed_index):
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_viewed_index": last_viewed_index}},
            upsert=True,
        )
