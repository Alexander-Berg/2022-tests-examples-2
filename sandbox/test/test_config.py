from cryptography.fernet import Fernet

import library.python.resource as lpr
import pytest

from startrek_client import Startrek
from startrek_client.settings import VERSION_SERVICE

from sandbox.projects.eda.computing_sp_statistic.config import teams


KEY = b'_4Bi5waQ6QaTzN-ntF3BkMOIs4wdwwVTGHfA6_i5zcA='


oauth_token = None
chyt_token = None


def get_oauth_token():
    global oauth_token
    if oauth_token is None:
        cipher_suite = Fernet(KEY)
        secret = lpr.find('/secret1.bin')
        oauth_encoded = cipher_suite.decrypt(secret)
        oauth_token = oauth_encoded.decode()
    return oauth_token


def get_chyt_token():
    global chyt_token
    if chyt_token is None:
        cipher_suite = Fernet(KEY)
        secret = lpr.find('/secret2.bin')
        chyt_encoded = cipher_suite.decrypt(secret)
        chyt_token = chyt_encoded.decode()
    return chyt_token


client = Startrek(
    useragent='robot-pmo-automation',
    token=get_oauth_token(),
    api_version=VERSION_SERVICE,
)


@pytest.mark.parametrize('team, config', list(teams.items()))
def test_validation_query(team, config):
    # test only on last year
    query = config['query'] + ' Resolved: 2021-01-01..2022-01-01'
    tickets = client.issues.find(query)
    assert len(tickets) > 0, '''Не найден ни один тикет в данной очереди или у робота нет доступа'''
