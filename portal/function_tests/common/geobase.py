# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
from functools32 import lru_cache
from requests import Session

session = Session()
API_ENDPOINT = 'http://geobase.qloud.yandex.ru/v1/{}'


class Regions(object):
    # Countries
    RUSSIA = 225
    UKRAINE = 187
    BELARUS = 149
    KAZAKHSTAN = 159

    TURKEY = 983
    GEORGIA = 169
    UZBEKISTAN = 171
    USA = 84

    # Russia

    MOSCOW = 213
    SAINT_PETERSBURG = 2
    YEKATERINBURG = 54
    VORONEZH = 193
    NIZHNY_NOVGOROD = 47
    ROSTOV_NA_DONU = 39
    KRASNODAR = 35
    CHELYABINSK = 56
    SAMARA = 51
    NOVOSIBIRSK = 65
    VOLGOGRAD = 38
    UFA = 172
    PERM = 50
    SARATOV = 194
    PETROPAVLOVSK = 78
    KALUGA = 6
    LIPETSK = 9
    ZHELEZNODOROZHNY = 21622

    # Belarus
    MINSK = 157
    VITEBSK = 154
    BOBRUISK = 20729

    # Ukraine
    KYIV = 143
    LVIV = 144

    # Kazakhstan
    ASTANA = 163
    ALMATY = 162
    KARAGANDA = 164

    # Turkey
    ISTANBUL = 11508
    ANKARA = 11503

    # Uzbekistan
    TASHKENT = 10335
    SAMARKAND = 10334

    # Other
    LONDON = 10393
    NEW_YORK = 202
    BERLIN = 177
    WASHINGTON = 87


class ipByRegion(object):
    MOSCOW = '89.175.217.44'
    ASTANA = '2.75.212.68'
    MINSK = '93.84.10.197'
    WASHINGTON = '3.14.212.29'
    ISTANBUL = '185.65.206.246'


_cache = lru_cache(maxsize=100)


def _geobase_request(method, params, retries=10):
    # print method, params
    responce = ''
    while retries:
        retries -= 1
        responce = session.get(API_ENDPOINT.format(method), params=params)
        if responce.status_code == 200:
            return responce.json()
    else:
        raise Exception('Got bad status_code from geobase: {}\nanswer: {}'
                        .format(responce.status_code, responce.content))


def asset(ip):
    return _geobase_request('asset', dict(ip=ip))


@_cache
def calculate_points_distance(alat, alon, blat, blon):
    return _geobase_request('calculate_points_distance', dict(alon=alon, alat=alat, blon=blon, blat=blat))


@_cache
def chief_region_id(id):
    return _geobase_request('chief_region_id', dict(id=id))


def children(id, crimea_status='ru'):
    return _geobase_request('children', dict(id=id, crimea_status=crimea_status))


@_cache
def find_country(id, crimea_status='ru'):
    return _geobase_request('find_country', dict(id=id, crimea_status=crimea_status))


def is_in(id, pid, crimea_status='ru'):
    return _geobase_request('in', dict(pid=pid, id=id, crimea_status=crimea_status))


@_cache
def linguistics_for_region(id, lang):
    return _geobase_request('linguistics_for_region', dict(id=id, lang=lang))


@_cache
def parent_id(id, crimea_status='ru'):
    return _geobase_request('parent_id', dict(id=id, crimea_status=crimea_status))


@_cache
def parents(id, crimea_status='ru'):
    return _geobase_request('parents', dict(id=id, crimea_status=crimea_status))


@_cache
def region_by_id(id, crimea_status='ru'):
    return _geobase_request('region_by_id', dict(id=id, crimea_status=crimea_status))


def region_by_ip(ip, crimea_status='ru'):
    return _geobase_request('region_by_ip', dict(ip=ip, crimea_status=crimea_status))


def region_id(ip):
    return _geobase_request('region_id', dict(ip=ip))


def region_id_by_location(lat, lon):
    return _geobase_request('region_id_by_location', dict(lat=lat, lon=lon))


def regions_by_type(type):
    return _geobase_request('regions_by_type', dict(type=type))


def subtree(id, crimea_status):
    return _geobase_request('subtree', dict(id=id, crimea_status=crimea_status))


def supported_linguistics():
    return _geobase_request('supported_linguistics', dict())


@_cache
def timezone(id):
    return _geobase_request('timezone', dict(id=id))


@_cache
def tzinfo(id):
    return _geobase_request('tzinfo', dict(id=id))


def get_kubr_domain(id):
    region_parents = set(parents(id))

    if Regions.UKRAINE in region_parents:
        return 'ua'

    if Regions.BELARUS in region_parents:
        return 'by'

    if Regions.KAZAKHSTAN in region_parents:
        return 'kz'

    if Regions.UZBEKISTAN in region_parents:
        return 'uz'

    return 'ru'


def get_domain_by_region(region_id):
    region_parents = set(parents(region_id))

    if Regions.UKRAINE in region_parents:
        return 'ua'

    if Regions.BELARUS in region_parents:
        return 'by'

    if Regions.KAZAKHSTAN in region_parents:
        return 'kz'

    if Regions.TURKEY in region_parents:
        return 'com.tr'

    if Regions.GEORGIA in region_parents:
        return 'com.ge'

    if Regions.UZBEKISTAN in region_parents:
        return 'uz'

    if Regions.USA in region_parents:
        return 'com'

    return 'ru'


def get_time(id):
    return datetime.now(pytz.timezone(timezone(id)))
