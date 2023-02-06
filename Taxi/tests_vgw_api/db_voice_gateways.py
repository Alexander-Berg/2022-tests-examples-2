import collections
import datetime

import dateutil.parser
from psycopg2 import extras
import pytz


K_ID = 'id'
K_ENABLED_AT = 'enabled_at'
K_DISABLED_AT = 'disabled_at'
K_TOKEN = 'token'

K_INFO = 'info'
K_HOST = 'host'
K_IGNORE_CERTIFICATE = 'ignore_certificate'

K_SETTINGS = 'settings'
K_NAME = 'name'
K_IDLE_EXPIRES_IN = 'idle_expires_in'
K_DISABLED = 'disabled'
K_WEIGHT = 'weight'

GATEWAY1 = {
    K_ID: 'id_1',
    K_TOKEN: 'token_1',
    K_INFO: {K_HOST: 'host_1', K_IGNORE_CERTIFICATE: False},
    K_SETTINGS: {
        K_NAME: 'name_1',
        K_IDLE_EXPIRES_IN: 100,
        K_DISABLED: False,
        K_WEIGHT: 10,
    },
}

GATEWAY2 = {
    K_ID: 'id_2',
    K_TOKEN: 'token_2',
    K_INFO: {K_HOST: 'host_2', K_IGNORE_CERTIFICATE: True},
    K_SETTINGS: {
        K_NAME: 'name_2',
        K_IDLE_EXPIRES_IN: 200,
        K_DISABLED: True,
        K_WEIGHT: 20,
    },
}


def select_gateways(pgsql):
    cursor = pgsql['vgw_api'].cursor()
    extras.register_composite('voice_gateways.info_t', cursor)
    extras.register_composite('voice_gateways.settings_t', cursor)
    cursor.execute(
        'SELECT '
        'id, '
        'enabled_at, '
        'disabled_at, '
        'info::voice_gateways.info_t, '
        'settings::voice_gateways.settings_t, '
        'token, '
        'deleted '
        'FROM voice_gateways.voice_gateways '
        'ORDER BY id ASC',
    )
    result = cursor.fetchall()
    cursor.close()
    gateways = []
    gateway_ = collections.namedtuple(
        'Gateway',
        [
            'id',
            'enabled_at',
            'disabled_at',
            'info',
            'settings',
            'token',
            'deleted',
        ],
    )
    for row in result:
        gateways.append(
            gateway_(row[0], row[1], row[2], row[3], row[4], row[5], row[6]),
        )
    return gateways


def select_disabling_history(pgsql, gateway_id):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT voice_gateway_id, '
        'enabled_at, '
        'disabled_at, '
        'disable_reason, '
        'additional_disable_data, '
        'additional_enable_data, '
        'disabled_by, '
        'enabled_by, '
        'enable_after, '
        'relapse_count '
        'FROM voice_gateways.disabling_history '
        f'WHERE voice_gateway_id=\'{gateway_id}\' '
        'ORDER BY disabled_at DESC;',
    )
    result = cursor.fetchall()
    cursor.close()
    entries = []
    entry_ = collections.namedtuple(
        'Gateway',
        [
            'id',
            'enabled_at',
            'disabled_at',
            'disable_reason',
            'additional_disable_data',
            'additional_enable_data',
            'disabled_by',
            'enabled_by',
            'enable_after',
            'relapse_count',
        ],
    )
    for row in result:
        entries.append(
            entry_(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
            ),
        )
    return entries


def now_utc():
    return datetime.datetime.now(tz=pytz.timezone('UTC'))


def is_now_str(time_str):
    time = dateutil.parser.parse(time_str)
    return is_now(time)


def is_now(time):
    return abs(time - now_utc()) < datetime.timedelta(minutes=10)
