import datetime
import json
import uuid

import create_personal_driver_licenses
import create_personal_phones


def create_car(park_id):
    return {
        'booster_count': 1,
        'brand': 'BMW',
        'callsign': uuid.uuid4().hex[:5],
        'car_id': uuid.uuid4().hex,
        'category': {
            'business': True,
            'comfort': True,
            'comfort_plus': True,
            'econom': True,
            'limousine': True,
            'minibus': True,
            'minivan': True,
            'pool': True,
            'trucking': True,
            'vip': True,
            'wagon': True,
        },
        'chairs': [
            {'brand': 'Яндекс', 'categories': [1, 2, 3], 'isofix': True},
        ],
        'charge_confirmed': True,
        'color': 'Желтый',
        'confirmed_boosters': 1,
        'confirmed_chairs': [
            {
                'brand': 'Яндекс',
                'categories': [1, 2, 3],
                'confirmed_categories': [1, 2, 3],
                'is_enabled': True,
                'isofix': True,
            },
        ],
        'created_date': {'$date': datetime.datetime.utcnow().timestamp()},
        'lightbox_confirmed': True,
        'mileage': 0,
        'model': '7er',
        'modified_date': {'$date': datetime.datetime.utcnow().timestamp()},
        'number': uuid.uuid4().hex[:10].upper(),
        'number_normalized': uuid.uuid4().hex[:10].upper(),
        'park_id': park_id,
        'rug_confirmed': True,
        'service': {
            'animals': True,
            'bicycle': True,
            'booster': True,
            'charge': True,
            'child_seat': True,
            'conditioner': True,
            'delivery': True,
            'extra_seats': True,
            'franchise': True,
            'lightbox': True,
            'pos': True,
            'print_bill': True,
            'rug': True,
            'ski': True,
            'smoking': True,
            'sticker': True,
            'vip_event': True,
            'wagon': True,
            'wifi': True,
            'woman_driver': True,
            'yandex_money': False,
        },
        'status': 'working',
        'sticker_confirmed': True,
        'tariffs': ['Эконом'],
        'transmission': 'unknown',
        'year': 2017,
    }


def create_driver(phone, car, park_id):
    license_series = uuid.uuid4().hex[:10].upper()
    license_number = uuid.uuid4().hex[:20].upper()
    return {
        'balance': 1000000,
        'balance_deny_onlycard': False,
        'balance_limit': 0,
        'car_id': car['car_id'],
        'created_date': {'$date': datetime.datetime.utcnow().timestamp()},
        'dkk_counter': 0,
        'driver_id': uuid.uuid4().hex,
        'first_name': 'Иван',
        'hire_date': {'$date': datetime.datetime.utcnow().timestamp()},
        'last_name': 'Иванов',
        'license': license_series + license_number,
        'license_normalized': license_series + license_number,
        'license_expire_date': {
            '$date': datetime.datetime(2100, 12, 31).timestamp(),
        },
        'license_issue_date': {
            '$date': datetime.datetime(2017, 1, 1).timestamp(),
        },
        'license_number': license_number,
        'license_series': license_series,
        'license_verification': True,
        'middle_name': 'Иванович',
        'modified_date': {'$date': datetime.datetime.utcnow().timestamp()},
        'taximeter_version': '9.00 (1234)',
        'taximeter_version_type': '',
        'locale': 'ru',
        'phones': [phone],
        'rule_id': 'work_rule_1',
        'park_id': park_id,
        'work_status': 'working',
        'providers': ['yandex', 'park'],
    }


def main():
    park_id = 'f6d9f7e55a9144239f706f15525ff2a9'
    cars = []
    drivers = []
    for num in range(250):
        phone = '+79001111%03d' % num
        car_doc = create_car(park_id)
        driver_doc = create_driver(phone, car_doc, park_id)
        cars.append(car_doc)
        drivers.append(driver_doc)
    db_dbdrivers_json = 'volumes/bootstrap_db/db_data/db_dbdrivers.json'
    with open(db_dbdrivers_json, 'w', encoding='utf-8') as fle:
        json.dump(drivers, fle, ensure_ascii=False, sort_keys=True, indent=2)
    db_dbcars_json = 'volumes/bootstrap_db/db_data/db_dbcars.json'
    with open(db_dbcars_json, 'w', encoding='utf-8') as fle:
        json.dump(cars, fle, ensure_ascii=False, sort_keys=True, indent=2)
    create_personal_driver_licenses.create_by_dbdriver(db_dbdrivers_json)
    create_personal_phones.create_by_dbdriver(db_dbdrivers_json)


if __name__ == '__main__':
    main()
