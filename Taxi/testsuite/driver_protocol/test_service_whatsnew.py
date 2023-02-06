import datetime

import pytest


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_add_new_taximeter_new(taxi_driver_protocol, db):
    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
                'taximeter_version': '8.71',
                'taximeter_build': 11,
                'taximeter_version_types': [
                    'release',
                    'beta',
                    'azerbaijan',
                    'experimental',
                    'sdc',
                ],
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one({})
    assert news_obj['author'] == 'melon-aerial'
    assert news_obj['editor_text'] == 'Новая новость о новой фиче'
    assert news_obj['text_tanker_key'] == 'ficha_cool'
    assert news_obj['taximeter_version'] == '8.71'
    assert news_obj['taximeter_build'] == 11
    assert news_obj['experiment'] == 'cool_exp'
    assert set(news_obj['taximeter_version_types']) == set(
        ['release', 'beta', 'azerbaijan', 'experimental', 'sdc'],
    )
    assert db.misc_taximeter_news.count() == 1

    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool2',
                'taximeter_version': '8.71',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'text_tanker_key': 'ficha_cool2'},
    )
    assert news_obj['editor_text'] == 'Новая новость о новой фиче'
    assert news_obj['text_tanker_key'] == 'ficha_cool2'
    assert news_obj['taximeter_version'] == '8.71'
    assert news_obj['author'] == 'melon-aerial'
    assert db.misc_taximeter_news.count() == 2


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_add_new_taximeter_conflict(taxi_driver_protocol, db):
    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'taximeter_version': '8.71',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    assert db.misc_taximeter_news.count() == 1

    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool2',
                'taximeter_version': '8.71',
            },
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'taximeter_version': '8.71',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 409
    assert db.misc_taximeter_news.count() == 1

    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool2',
                'taximeter_version': '8.71',
            },
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool2',
                'taximeter_version': '8.71',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 409
    assert db.misc_taximeter_news.count() == 1


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_add_new_bad_request(taxi_driver_protocol):
    data = {
        'news': [
            {
                'author': 'haha',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 400


def test_add_new_bad_request_bad_version_type(taxi_driver_protocol):
    data = {
        'news': [
            {
                'author': 'haha',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
                'taximeter_version_types': ['XX'],
                'taximeter_version': '8.71',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 400


def test_add_new_bad_request_bad_version(taxi_driver_protocol):
    data = {
        'news': [
            {
                'author': 'haha',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
                'taximeter_version_types': ['release'],
                'taximeter_version': (
                    '8'
                ),  # version have to be in format "X.YY",
                # where X - is major release number,
                # and YY - is minor release number.
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 400


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.filldb(misc_taximeter_news='edit')
def test_edit_new_taximeter_news(taxi_driver_protocol, db):
    data = {
        'author': 'haha',
        'editor_text': 'Новая новость о новой фиче',
        'text_tanker_key': 'ficha_cool',
        'editor_title': 'Стало круто!',
        'title_tanker_key': 'ficha_cool_title',
        'experiment': 'cool_exp',
        'taximeter_version': '8.71',
        'taximeter_build': 11,
        'taximeter_version_types': [
            'release',
            'beta',
            'azerbaijan',
            'experimental',
            'sdc',
        ],
    }
    response = taxi_driver_protocol.put(
        '/service/whatsnew',
        data,
        params={'id': '00000000000000000000000000000001'},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'_id': '00000000000000000000000000000001'},
    )
    assert news_obj['updated'] == datetime.datetime(2018, 1, 21, 23, 59)
    assert news_obj['editor_text'] == 'Новая новость о новой фиче'
    assert news_obj['text_tanker_key'] == 'ficha_cool'
    assert news_obj['author'] == 'haha'
    assert news_obj['taximeter_version'] == '8.71'
    assert news_obj['taximeter_build'] == 11
    assert news_obj['experiment'] == 'cool_exp'
    assert set(news_obj['taximeter_version_types']) == set(
        ['release', 'beta', 'azerbaijan', 'experimental', 'sdc'],
    )

    data = {
        'author': 'haha',
        'editor_text': 'Новая новость о новой фиче',
        'text_tanker_key': 'ficha_cool2',
        'editor_title': 'Стало круто!',
        'title_tanker_key': 'ficha_cool_title',
        'taximeter_version': '8.71',
        'taximeter_version_types': [
            'release',
            'beta',
            'azerbaijan',
            'experimental',
            'sdc',
        ],
    }
    response = taxi_driver_protocol.put(
        '/service/whatsnew',
        data,
        params={'id': '00000000000000000000000000000000'},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'_id': '00000000000000000000000000000000'},
    )
    assert news_obj['updated'] == datetime.datetime(2018, 1, 21, 23, 59)
    assert news_obj['editor_text'] == 'Новая новость о новой фиче'
    assert news_obj['text_tanker_key'] == 'ficha_cool2'
    assert news_obj['author'] == 'haha'
    assert news_obj['taximeter_version'] == '8.71'
    assert 'taximeter_build' not in news_obj
    assert 'experiment' not in news_obj
    assert set(news_obj['taximeter_version_types']) == set(
        ['release', 'beta', 'azerbaijan', 'experimental', 'sdc'],
    )


@pytest.mark.filldb(misc_taximeter_news='edit')
def test_edit_new_bad_request(taxi_driver_protocol):
    data = {
        'author': 'belka',
        'editor_text': 'Новая новость о новой фиче',
        'text_tanker_key': 'ficha_cool',
        'editor_title': 'Стало круто!',
        'title_tanker_key': 'ficha_cool_title',
    }
    response = taxi_driver_protocol.put(
        '/service/whatsnew',
        data,
        params={'id': '00000000000000000000000000000001'},
    )
    assert response.status_code == 400


@pytest.mark.filldb(misc_taximeter_news='edit')
def test_edit_new_not_found(taxi_driver_protocol):
    data = {
        'author': 'belka',
        'editor_text': 'Новая новость о новой фиче',
        'text_tanker_key': 'ficha_cool',
        'editor_title': 'Стало круто!',
        'title_tanker_key': 'ficha_cool_title',
        'taximeter_version': '8.71',
    }
    response = taxi_driver_protocol.put(
        '/service/whatsnew', data, params={'id': '746178696d5f6e65775f3130'},
    )
    assert response.status_code == 404


@pytest.mark.filldb(misc_taximeter_news='get')
def test_get_news_taximeter_news(taxi_driver_protocol, db):
    response = taxi_driver_protocol.get(
        '/service/whatsnew', params={'taximeter_version': 8.71},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['news']) == 2
    assert resp_json['news'][0] == {
        'author': 'melon-aerial',
        'application': 'taximeter',
        'editor_text': 'Текст новости #11',
        'text_tanker_key': 'text_tanker_key_11',
        'taximeter_version': '8.71',
        'taximeter_build': 55,
        'experiment': 'ahaha',
        'id': '00000000000000000000000000000000',
        'updated': '2016-12-19T08:26:00.000000Z',
        'created': '2016-12-19T08:26:00.000000Z',
        'taximeter_version_types': [],
        'is_hidden': False,
        'target_filter': [],
    }
    assert resp_json['news'][1] == {
        'author': 'melon-aerial',
        'application': 'taximeter',
        'editor_text': 'Текст новости #12',
        'text_tanker_key': 'text_tanker_key_12',
        'taximeter_version': '8.71',
        'id': '00000000000000000000000000000001',
        'updated': '2016-12-19T08:25:50.000000Z',
        'created': '2016-12-19T08:26:10.000000Z',
        'taximeter_version_types': [],
        'is_hidden': False,
        'target_filter': [],
    }


@pytest.mark.filldb(misc_taximeter_news='get')
def test_get_news_taximeter_news_return_all(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew',
        params={'show_hidden': True, 'taximeter_version': 8.71},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['news']) == 3
    assert resp_json['news'][2] == {
        'author': 'melon-aerial',
        'application': 'taximeter',
        'editor_text': 'Текст новости #13',
        'text_tanker_key': 'text_tanker_key_13',
        'taximeter_version': '8.71',
        'id': '00000000000000000000000000000002',
        'updated': '2016-12-19T08:25:40.000000Z',
        'created': '2016-12-19T08:26:20.000000Z',
        'is_hidden': True,
        'taximeter_version_types': ['release'],
        'target_filter': [],
    }


@pytest.mark.filldb(misc_taximeter_news='get')
def test_get_news_taximeter_news_target_filter(taxi_driver_protocol, db):
    response = taxi_driver_protocol.get(
        '/service/whatsnew', params={'taximeter_version': 8.72},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['news']) == 1
    assert resp_json['news'][0] == {
        'author': 'melon-aerial',
        'application': 'taximeter',
        'editor_text': 'Текст новости #13',
        'text_tanker_key': 'text_tanker_key_13',
        'taximeter_version': '8.72',
        'id': '00000000000000000000000000000003',
        'updated': '2016-12-19T08:25:50.000000Z',
        'created': '2016-12-19T08:26:30.000000Z',
        'taximeter_version_types': [],
        'is_hidden': False,
        'target_filter': ['selfemployed', 'could_be_selfemployed'],
    }


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.filldb(misc_taximeter_news='edit')
def test_edit_new_target_filter(taxi_driver_protocol, db):
    data = {
        'author': 'haha',
        'application': 'taximeter',
        'editor_text': 'Новая новость о новой фиче',
        'text_tanker_key': 'ficha_cool',
        'editor_title': 'Стало круто!',
        'title_tanker_key': 'ficha_cool_title',
        'experiment': 'cool_exp',
        'taximeter_version': '8.71',
        'taximeter_build': 11,
        'taximeter_version_types': [],
        'target_filter': ['selfemployed'],
    }
    response = taxi_driver_protocol.put(
        '/service/whatsnew',
        data,
        params={'id': '00000000000000000000000000000001'},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'_id': '00000000000000000000000000000001'},
    )
    assert news_obj['target_filter'] == ['selfemployed']


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_add_new_taximeter_new_target_filter(taxi_driver_protocol, db):
    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
                'taximeter_version': '8.71',
                'target_filter': ['could_be_selfemployed'],
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one({})
    assert news_obj['target_filter'] == ['could_be_selfemployed']


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_typed_experiment(taxi_driver_protocol, db):
    data = {
        'news': [
            {
                'author': 'melon-aerial',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'experiment': 'cool_exp',
                'typed_experiment': 'exp3',
                'taximeter_version': '8.71',
                'taximeter_build': 11,
                'taximeter_version_types': [
                    'release',
                    'beta',
                    'azerbaijan',
                    'experimental',
                    'sdc',
                ],
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one({})
    assert news_obj['typed_experiment'] == 'exp3'

    data['news'][0].update({'typed_experiment': 'edited_exp3'})
    response = taxi_driver_protocol.put(
        '/service/whatsnew',
        json=data['news'][0],
        params={'id': news_obj['_id']},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one({})
    assert news_obj['typed_experiment'] == 'edited_exp3'

    response = taxi_driver_protocol.get(
        '/service/whatsnew', params={'taximeter_version': 8.71},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['news'][0]['typed_experiment'] == 'edited_exp3'


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_uber_new(taxi_driver_protocol, db):
    data = {
        'news': [
            {
                'author': 'artfulvampire',
                'editor_text': 'Новая новость о новой фиче',
                'text_tanker_key': 'ficha_cool',
                'taximeter_version': '9.05',
                'application': 'uberdriver',
            },
        ],
    }
    response = taxi_driver_protocol.post('/service/whatsnew', data)
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one({})
    assert news_obj['application'] == 'uberdriver'
