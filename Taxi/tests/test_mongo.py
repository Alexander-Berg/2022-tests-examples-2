import json
import pymongo
import logging


logger = logging.getLogger('suptech')

with open('/etc/yandex/taxi-secdist/taxi.json') as f:
    TOKENS = json.load(f)


def get_mongo_db():
    storage = pymongo.MongoClient(
        TOKENS['mongo_settings']['suptech-bot']['uri']
        )
    return storage.get_database()


db = get_mongo_db()

assert db.list_collection_names()

assert db.catbot_user_session.find_one(filter={'login': 'rostovsky'})
assert db.catbot_buttons.find_one(filter={'button': 'tagging'})
assert db.catbot_texts.find_one(filter={'key_text': 'chat'})
