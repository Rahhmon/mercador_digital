import pandas as pd
from pymongo import MongoClient
from enum import Enum
from settings import Settings


MONGO_URI = Settings.MONGO_URI

class EnumCollectionNames(Enum):
    FACEBOOK_MARKET_PLACE = "FACEBOOK_MARKET_PLACE"

class EnumDatabaseNames(Enum):
    DIGITAL_MARKETPLACE = "DIGITAL_MARKETPLACE"


class Agent:
    def __init__(self, database_name:str):
        self.database_uri = MONGO_URI
        self.client = self.instance_client()
        self.database_name = database_name
        self.database = self.client[self.database_name]

    def instance_client(self):
        try:
            client = MongoClient(self.database_uri)
            return client
        except Exception as e:
            print(e)