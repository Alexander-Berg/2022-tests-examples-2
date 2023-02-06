import copy
import datetime
import enum


class MongoResponse(enum.Enum):
    EXIST = 1
    EXIST_OFFER = (2,)
    EXIST_CONSENT = (3,)
    NOT_EXIST = 4


DEFAULT_PARKS = {
    'id': 'db1',
    'login': 'some_login',
    'name': 'some_name',
    'is_active': True,
    'city_id': 'MSK',
    'locale': 'ru',
    'is_billing_enabled': True,
    'is_franchising_enabled': True,
    'demo_mode': False,
    'country_id': 'rus',
    'driver_partner_source': 'selfemployed_fns',
    'fleet_type': 'taximeter',
    'provider_config': {'clid': '12345', 'type': 'production'},
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}

OFFER_ACCEPTED_TIME = '2018-09-13T15:21:02Z'
OFFER_ACCEPTED_TIME_TEST = '2018-09-13T15:21:02+00:00'

# used by GET handlers for OPTEUM and TAXIMETER:
RESPONSE200_ACCEPTED = {'offer_state': 'accepted'}
RESPONSE200_NOT_ACCEPTED = {
    'offer_state': 'not_accepted',
    'offer_url': 'https://yandex.ru/legal/zapravki_postpaidtaxi_offer/',
}
RESPONSE200_ERROR = {
    'offer_state': 'acceptance_error',
    'offer_url': 'https://yandex.ru/legal/zapravki_postpaidtaxi_offer/',
}
RESPONSE200_IN_PROGRESS = {'offer_state': 'acceptance_in_progress'}
RESPONSE200_NOT_AVAILABLE = {'offer_state': 'not_available'}
RESPONSE200_EXPIRED = {
    'offer_state': 'creation_expired',
    'offer_url': 'https://yandex.ru/legal/zapravki_postpaidtaxi_offer/',
}
RESPONSE404_PARK_NOT_FOUND = {'code': '404', 'message': 'Park not found.'}
RESPONSE500 = {'code': '500', 'message': 'InternalError'}

INSERT_PARTNER_CONTRACTS_ACCEPT = (
    'INSERT INTO gas_stations.partner_contracts_acceptance '
    '(park_id, clid, started, finished)'
    ' VALUES (\'{}\', \'{}\', \'{}\', {})'
)

DEFAULT_CONTRACTS_RESPONSE = {'inquiry_id': 'some_id', 'status': 'OK'}


def get_response200_accepted(login, time):
    result = copy.deepcopy(RESPONSE200_ACCEPTED)
    result['acceptor_login'] = login
    result['informed_consent_accepted_date'] = time
    result['offer_accepted_date'] = time
    return result


def make_park_not_active(park):
    result = copy.deepcopy(park)
    result['is_active'] = False
    return result


def make_park_empty_login(park):
    result = copy.deepcopy(park)
    result['login'] = ''
    return result


def make_park_wrong_fleet_type(park):
    result = copy.deepcopy(park)
    result['fleet_type'] = 'something_wrong'
    return result


def make_park_without_prov_conf(park):
    result = copy.deepcopy(park)
    del result['provider_config']
    return result


def make_park_without_clid(park):
    result = copy.deepcopy(park)
    del result['provider_config']['clid']
    return result


def make_park_wrong_type(park):
    result = copy.deepcopy(park)
    result['provider_config']['type'] = 'aggregation'
    return result


def make_park_wrong_partner_source(park):
    result = copy.deepcopy(park)
    del result['driver_partner_source']
    return result


FORMAT = '%Y-%m-%d %H:%M:%S'
POSTFIX = '.00+00'


def get_in_progress_time():
    started = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
    ).strftime(FORMAT) + POSTFIX
    finished = None
    return {'started': started, 'finished': finished}


def get_expired_time():
    started = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=120)
    ).strftime(FORMAT) + POSTFIX
    finished = None
    return {'started': started, 'finished': finished}


def get_finished_time():
    started = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
    ).strftime(FORMAT) + POSTFIX
    finished = (datetime.datetime.utcnow()).strftime(FORMAT) + POSTFIX
    return {'started': started, 'finished': finished}


def update_mongo_gas_stations(mongodb, key, result_type):
    format_str = '%Y-%m-%dT%H:%M:%SZ'
    time = datetime.datetime.strptime(OFFER_ACCEPTED_TIME, format_str)
    if result_type == MongoResponse.NOT_EXIST:
        mongodb.dbparks.update(
            {'_id': key},
            {
                '$unset': {
                    'gas_stations.offer_accepted_date': 1,
                    'gas_stations.informed_consent_accepted_date': 1,
                },
            },
        )
    elif result_type == MongoResponse.EXIST_OFFER:
        mongodb.dbparks.update(
            {'_id': key},
            {
                '$unset': {'gas_stations.informed_consent_accepted_date': 1},
                '$set': {'gas_stations.offer_accepted_date': time},
            },
        )

    elif result_type == MongoResponse.EXIST_CONSENT:
        mongodb.dbparks.update(
            {'_id': key},
            {
                '$unset': {'gas_stations.informed_consent_accepted_date': 1},
                '$set': {'gas_stations.offer_accepted_date': time},
            },
        )
    else:
        mongodb.dbparks.update(
            {'_id': key},
            {
                '$set': {
                    'gas_stations.offer_accepted_date': time,
                    'gas_stations.informed_consent_accepted_date': time,
                },
            },
        )
