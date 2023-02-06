import datetime
import time

import pytest

from taxi_tests import utils


@pytest.mark.driver_experiments('ahaha')
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
def test_get_all(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.72 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'news': [
            {
                'id': '00000000000000000000000000000000',
                'text': 'Текст новости 11',
            },
            {
                'id': '00000000000000000000000000000001',
                'text': 'Текст новости 12',
            },
        ],
    }

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.73 (57)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'news': [
            {
                'id': '00000000000000000000000000000003',
                'text': 'Текст новости 13',
            },
            {
                'id': '00000000000000000000000000000000',
                'text': 'Текст новости 11',
            },
            {
                'id': '00000000000000000000000000000001',
                'text': 'Текст новости 12',
            },
        ],
    }


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
def test_get_all_without_experiment(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.72 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'news': [
            {
                'id': '00000000000000000000000000000001',
                'text': 'Текст новости 12',
            },
        ],
    }

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.73 (57)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'news': [
            {
                'id': '00000000000000000000000000000003',
                'text': 'Текст новости 13',
            },
            {
                'id': '00000000000000000000000000000001',
                'text': 'Текст новости 12',
            },
        ],
    }


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
def test_get_with_less_by_limit(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 2, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.73 (52)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['news']) == 2


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
def test_get_with_less_by_version_build(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 2, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.71 (54)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['news']) == 1


@pytest.mark.driver_experiments('ahaha')
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
@pytest.mark.now('2016-12-19T23:59:00Z')
def test_get_show_only_watched(
        taxi_driver_protocol, db, now, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 2, 'show_only_not_watched': True},
        headers={'User-Agent': 'Taximeter 8.73 (57)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['news']) == 2

    @utils.timeout(1, False)
    def wait_mongo(need_value):
        while True:
            if (
                    db.driver_read_taximeter_news.count(
                        {'driver_id': '1488_driver'},
                    )
                    == need_value
            ):
                return True
            time.sleep(0.01)

    if not wait_mongo(2):
        assert not 'timeout'
        return

    taxi_driver_protocol.invalidate_caches(now=now)

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 2, 'show_only_not_watched': True},
        headers={'User-Agent': 'Taximeter 8.73 (57)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['news']) == 1

    if not wait_mongo(3):
        assert not 'timeout'
        return


@pytest.mark.driver_experiments('ahaha')
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
    },
)
@pytest.mark.now('2016-12-19T23:59:00Z')
@pytest.mark.filldb(driver_read_taximeter_news='update_check')
def test_get_show_only_watched_update_check(
        taxi_driver_protocol, db, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 3, 'show_only_not_watched': True},
        headers={'User-Agent': 'Taximeter 8.73 (57)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['news']) == 2
    assert resp['news'][0]['id'] == '00000000000000000000000000000003'
    assert resp['news'][1]['id'] == '00000000000000000000000000000000'

    @utils.timeout(1, False)
    def wait_mongo():
        while True:
            if (
                    db.driver_read_taximeter_news.count(
                        {'driver_id': '1488_driver'},
                    )
                    == 3
            ):
                return True
            time.sleep(0.01)

    if not wait_mongo():
        assert not 'timeout'
        return

    read_obj = db.driver_read_taximeter_news.find_one(
        {
            'driver_id': '1488_driver',
            'taximeter_new_id': '00000000000000000000000000000003',
        },
    )
    assert read_obj['read_time'] == datetime.datetime(2016, 12, 19, 23, 59)

    read_obj = db.driver_read_taximeter_news.find_one(
        {
            'driver_id': '1488_driver',
            'taximeter_new_id': '00000000000000000000000000000000',
        },
    )
    assert read_obj['read_time'] == datetime.datetime(2016, 12, 19, 23, 59)

    read_obj = db.driver_read_taximeter_news.find_one(
        {
            'driver_id': '1488_driver',
            'taximeter_new_id': '00000000000000000000000000000001',
        },
    )
    assert read_obj['read_time'] == datetime.datetime(2016, 12, 19, 8, 26)


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.tanker_key_selfemployed': {
            'ru': 'Новость для самозанятых!',
        },
    },
)
def test_get_new_selfemployed(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1369', 'qwerty1', 'driver')
    driver_authorizer_service.set_session('1488', 'qwerty2', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1369&session=qwerty1',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    news_selfemployed = {
        'id': '00000000000000000000000000000004',
        'text': 'Новость для самозанятых!',
    }
    assert news_selfemployed in resp['news']

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty2',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert news_selfemployed not in resp['news']


@pytest.mark.filldb(dbparks='selfemployed')
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={'cities': ['Одинцово']},
    TAXIMETER_FNS_SELF_EMPLOYMENT_CITY_MAPPING_SETTINGS={
        'Москва': ['Кубинка'],
    },
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_selfemployed': {
            'ru': 'Новость для самозанятых!',
        },
        'taximeter_news_text.tanker_key_could_be_selfemployed': {
            'ru': 'Новость для будущих самозанятых!',
        },
    },
)
def test_get_new_could_be_selfemployed(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1111', 'qwerty1', 'driver')
    driver_authorizer_service.set_session('1112', 'qwerty2', 'driver')
    driver_authorizer_service.set_session('1113', 'qwerty3', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1112&session=qwerty2',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    news_selfemployed = {
        'id': '00000000000000000000000000000005',
        'text': 'Новость для будущих самозанятых!',
    }
    assert news_selfemployed in resp['news']

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1113&session=qwerty3',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert news_selfemployed in resp['news']

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1111&session=qwerty1',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert news_selfemployed not in resp['news']


@pytest.mark.experiments3(
    name='test_exp_3',
    consumers=['taximeter/whatsnew'],
    match={
        'consumers': ['taximeter/whatsnew'],
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'title': 'main_clause',
            'value': {},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'driver_id',
                                'arg_type': 'string',
                                'value': 'driver',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'park_dbid',
                                'arg_type': 'string',
                                'value': '1488',
                            },
                        },
                    ],
                },
            },
        },
    ],
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_13': {'ru': 'Текст новости 13'},
        'taximeter_news_text.text_tanker_key_12': {'ru': 'Текст новости 12'},
        'taximeter_news_text.text_tanker_key_11': {'ru': 'Текст новости 11'},
        'taximeter_news_text.tanker_key_exp3': {
            'ru': 'Текст новости под экспериментом 3.0',
        },
    },
)
def test_get_with_exp3(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 8.74 (43)'},
    )
    assert response.status_code == 200
    resp = response.json()
    news_ids = [i['id'] for i in resp['news']]
    assert '00000000000000000000000000000006' in news_ids


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taximeter_news_text.text_tanker_key_15': {'ru': 'Текст новости 15'},
    },
)
def test_get_uber(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_client_session(
        'uberdriver', '1488', 'qwerty', 'driver',
    )
    driver_authorizer_service.set_client_session(
        'taximeter', '1488', 'qwerty', 'driver',
    )

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter 9.06 (1234)'},
    )

    assert response.status_code == 200
    resp = response.json()
    news_ids = [item['id'] for item in resp['news']]
    assert '00000000000000000000000000000007' not in news_ids

    response = taxi_driver_protocol.post(
        'driver/whatsnew?db=1488&session=qwerty',
        json={'limit': 10, 'show_only_not_watched': False},
        headers={'User-Agent': 'Taximeter-Uber 9.06 (1234)'},
    )
    assert response.status_code == 200
    resp = response.json()
    news_ids = [item['id'] for item in resp['news']]
    assert '00000000000000000000000000000007' in news_ids
