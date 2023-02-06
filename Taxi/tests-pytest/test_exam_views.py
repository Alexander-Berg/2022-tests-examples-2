# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pytest

from django.test import RequestFactory

from taxi import config
from taxi.core import db
from taxiexams import views


TEST_EXAM_CITIES = {
    'Екатеринбург': {
        'valid_scores': (1, 2, 3, 4, 5),
        'misc_scores_required': True,
    },
    'Москва': {
        'valid_scores': (1, 2, 3, 4, 5),
        'misc_scores_required': True,
    },
    'Нижний Новгород': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Новосибирск': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Омск': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Ростов-на-Дону': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Санкт-Петербург': {
        'valid_scores': (2, 3, 4, 5),
        'misc_scores_required': True,
    },
    'Челябинск': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Ереван': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Уфа': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Самара': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Краснодар': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Волгоград': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Воронеж': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Казань': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Пермь': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Красноярск': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Тбилиси': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Астана': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Алматы': {
        'valid_scores': (1, 2, 3, 4, 5),
    },
    'Киев': {
        'valid_scores': (1, 2, 3, 4, 5),
    }
}


TEST_EXAM_CITIES_WITHOUT_VALID_SCORES = {
    city: {
        'valid_scores': [],
        'misc_scores_required': conf.get('misc_scores_required', False)
    } for city, conf in TEST_EXAM_CITIES.items()
}


TEST_EXAM_CITIES_MOSCOW = {
    'Москва': {
        'valid_scores': (1, 2, 3, 4, 5),
        'misc_scores_required': True,
    }
}


TEST_EXAM_CITIES_EKATERINBURG = {
    'Екатеринбург': {
        'valid_scores': (1, 2, 3, 4, 5),
        'misc_scores_required': True,
    }
}


@pytest.mark.filldb(_specified=True)
@pytest.mark.parametrize('city,city_config,expected_code', [
    ('Москва', TEST_EXAM_CITIES_MOSCOW, 200),
    ('Москва', TEST_EXAM_CITIES_EKATERINBURG, 400),
])
@pytest.inline_callbacks
def test_upload_correct_xml(open_file, city, city_config, expected_code):
    yield config.EXAM_CITIES.save(city_config)
    with open_file('correct_exams.xlsx') as fp:
        request = RequestFactory().post('', {
            'city': city, 'exams.xlsx': fp
        })
    view = views.BulkExamsView.as_view()
    response = yield view(request)
    assert response.status_code == expected_code

    if expected_code == 200:
        assert 'id' in json.loads(response.content)

        bulk_exams = yield db.exams_bulk.find({}).run()
        assert len(bulk_exams) == 1
        assert len(bulk_exams[0]['exams']) == 1

        assert bulk_exams[0].keys() == [
            'status', 'city', 'uid', 'created', 'exams', '_id', 'user',
        ]

        assert set(bulk_exams[0]['exams'][0].keys()) == {
            'profile-phone', 'profile-surname', 'center',
            'characteristic-experience', 'characteristic-language', 'result',
            'profile-birthdate', 'profile-lastname', 'profile-licence-serial',
            'is_finished', 'characteristic-psiho', 'start_date',
            'characteristic-service-standart', 'profile-name',
        }


@pytest.mark.parametrize('incorrect_file_name,city_config', [
    ('incorrect_exams.xlsx', TEST_EXAM_CITIES),
    ('incorrect_exams_too_many_columns.xlsx', TEST_EXAM_CITIES),
    ('incorrect_exams_invalid_score.xlsx', TEST_EXAM_CITIES),
    ('incorrect_exams_non_integer_score.xlsx', TEST_EXAM_CITIES),
    ('correct_exams.xlsx', TEST_EXAM_CITIES_WITHOUT_VALID_SCORES)
])
@pytest.inline_callbacks
def test_upload_incorrect_xml(open_file, incorrect_file_name, city_config):
    yield config.EXAM_CITIES.save(city_config)
    with open_file(incorrect_file_name) as fp:
        request = RequestFactory().post('', {
            'city': 'Москва', 'exams.xlsx': fp
        })
    view = views.BulkExamsView.as_view()
    response = yield view(request)
    assert response.status_code == 400


@pytest.mark.filldb(_specified=True)
@pytest.mark.parametrize('city,city_config,expected_code', [
    ('Москва', TEST_EXAM_CITIES_MOSCOW, 200),
    ('Москва', TEST_EXAM_CITIES_EKATERINBURG, 400),
])
@pytest.inline_callbacks
def test_post_correct_exam(patch, city, city_config, expected_code):
    yield config.EXAM_CITIES.save(city_config)

    @patch('taxi.external.mds.exists')
    def exists(image_id):
        return True

    request = RequestFactory().post('', {
        'city': city,
        'profile-phone': '9260583257',
        'profile-surname': 'Гигамов',
        'center': 'super-center',
        'characteristic-experience': 1,
        'characteristic-language': 1,
        'result': 1,
        'profile-birthdate': '12.07.1979',
        'profile-lastname': 'Гигамович',
        'profile-licence-serial': 'LADYGAGA',
        'is_finished': True,
        'characteristic-psiho': 1,
        'start_date': '12.08.2016 19:59:17',
        'characteristic-service-standart': 1,
        'profile-name': 'giga',
        'profile-photo': 'f',
        'profile-licence-scan': 'l',
        'user': 'baba',
        'uid': '1',
    })

    request.authorized_by_token = True
    view = views.ExamsView.as_view()
    response = yield view(request)

    assert response.status_code == expected_code

    if expected_code == 200:
        exams = yield db.exams.find({}).run()
        assert len(exams) == 1
        assert set(exams[0].keys()) == {
            'profile-phone', 'profile-surname',
            'characteristic-experience', 'characteristic-language', 'result',
            'profile-birthdate', 'profile-lastname', 'profile-licence-serial',
            'characteristic-psiho', 'characteristic-service-standart',
            'profile-name', '_id', 'city', 'uid', 'center', 'profile-photo',
            'profile-licence-scan', 'user', '_hash', 'created',
        }


@pytest.mark.config(EXAM_CITIES=TEST_EXAM_CITIES)
@pytest.inline_callbacks
def test_post_incorrect_exam(patch):
    @patch('taxi.external.mds.exists')
    def exists(image_id):
        return True

    request = RequestFactory().post('', {
        'city': 'Москва',
        'profile-phone': '9260583257',
        'profile-surname': 'Гигамов',
        'characteristic-experience': 1,
        'characteristic-language': 1,
        'result': 1,
        'profile-birthdate': '12.07.1979',
        'profile-lastname': 'Гигамович',
        'profile-licence-serial': 'LADYGAGA',
        'is_finished': True,
        'characteristic-psiho': 1,
        'start_date': '12.08.2016 19:59:17',
        'characteristic-service-standart': 1,
        'profile-name': 'giga',
        'profile-photo': 'f',
        'profile-licence-scan': 'l',
        'user': 'baba',
        'uid': '1',
    })

    request.authorized_by_token = True
    view = views.ExamsView.as_view()
    response = yield view(request)
    assert response.status_code == 400


@pytest.mark.filldb(_specified=True)
@pytest.mark.config(EXAM_CITIES=TEST_EXAM_CITIES)
@pytest.inline_callbacks
def test_post_new_cities_optional_scores(patch):
    @patch('taxi.external.mds.exists')
    def exists(image_id):
        return True

    request = RequestFactory().post('', {
        'city': 'Омск',
        'profile-phone': '9260583257',
        'profile-surname': 'Гигамов',
        'center': 'super-center',
        'result': 1,
        'profile-birthdate': '12.07.1979',
        'profile-lastname': 'Гигамович',
        'profile-licence-serial': 'LADYGAGA',
        'is_finished': True,
        'start_date': '12.08.2016 19:59:17',
        'profile-name': 'giga',
        'profile-photo': 'f',
        'profile-licence-scan': 'l',
        'user': 'baba',
        'uid': '1',
    })

    request.authorized_by_token = True
    view = views.ExamsView.as_view()
    response = yield view(request)
    assert response.status_code == 200

    exams = yield db.exams.find({}).run()
    assert len(exams) == 1
    assert set(exams[0].keys()) == {
        'profile-phone', 'profile-surname',
        'result', 'profile-birthdate', 'profile-lastname',
        'profile-licence-serial', 'profile-name', '_id', 'city', 'uid',
        'center', 'profile-photo', 'profile-licence-scan', 'user', '_hash',
        'created',
    }


@pytest.mark.parametrize('city_config', [
    TEST_EXAM_CITIES,
    TEST_EXAM_CITIES_WITHOUT_VALID_SCORES,
    TEST_EXAM_CITIES_MOSCOW,
    TEST_EXAM_CITIES_EKATERINBURG,
    {}  # View should return an empty list
])
@pytest.inline_callbacks
def test_exam_cities_view(city_config):
    yield config.EXAM_CITIES.save(city_config)

    request = RequestFactory().get('/')

    view = views.ExamCitiesView.as_view()
    response = yield view(request)

    assert response.status_code == 200

    city_items = json.loads(response.content)

    assert type(city_items) == list

    city_names = set()

    for city_item in city_items:
        assert 'id' in city_item
        assert 'name' in city_item

        city_id = city_item['id']
        city_name = city_item['name']

        assert city_id == city_name
        assert city_id in city_config
        assert city_name in city_config

        city_names.add(city_name)

    assert city_names == set(city_config.keys())
