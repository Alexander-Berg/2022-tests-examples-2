# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import dateutil.parser
import pytest
from django import test as django_test
from django.core.files import uploadedfile

from taxi.core import db
from taxiadmin.api.views import classification_rules

CITY = 'Омск'
NEW_CITY = 'New city'
CLASSIFIERS_URL = '/api/classifiers/'
GET_CLASSIFIER_URL = '/api/getclassifier/'
UPLOAD_CLASSIFIERS_RULES_URL = '/api/upload_classifiers_rules/'
SET_CLASSIFIER_URL = '/api/setclassifier/'
MODEL_SUGGEST_URL = '/api/modelssuggest/'


@pytest.mark.parametrize('method, data, code', [
    ('post', {}, 200),
    ('post', {'bad': 'request'}, 400),
    ('get', {}, 405)
])
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_classifiers(method, data, code):
    client = django_test.Client()
    if method == 'post':
        response = client.post(
            CLASSIFIERS_URL,
            json.dumps(data),
            content_type='application/json'
        )
    elif method == 'get':
        response = client.get(CLASSIFIERS_URL)
    assert response.status_code == code

    response = client.post(
        CLASSIFIERS_URL, {}, content_type='application/json')
    response_content = json.loads(response.content)
    docs = yield db.classification_rules.find().run()
    assert len(docs) == len(response_content['result'])


@pytest.mark.parametrize('method, data, code', [
    ('post', {'name': CITY}, 200),
    ('post', {'bad': 'request'}, 400),
    ('get', {'name': 'bad_method'}, 405)
])
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_classifier(method, data, code):
    client = django_test.Client()
    if method == 'post':
        response = client.post(
            GET_CLASSIFIER_URL,
            json.dumps(data),
            content_type='application/json'
        )
    elif method == 'get':
        response = client.get(GET_CLASSIFIER_URL)
    assert response.status_code == code

    response = client.post(
        GET_CLASSIFIER_URL,
        json.dumps({'name': CITY}),
        content_type='application/json'
    )
    response_content = json.loads(response.content)
    doc = yield db.classification_rules.find_one({'_id': CITY})
    classification_rules.sort_rules(doc['rules'])
    assert doc['rules'] == response_content['rules']


@pytest.mark.parametrize('file_content, duplicate_to_uber, expected_rules', [
    (
        ('name;cls;model;price;age;allowing\n'
         'dem_test;econom;Lada*;None;15;1'),
        False,
        [
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            }
        ]
    ),
    (
        ('name;cls;model;price;age;allowing\n'
         'dem_test;econom;Lada*;None;15;2'),
        False,
        [
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            },
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': False,
            }
        ]
    ),
    (
        ('name;cls;model;price;age;allowing\n'
         'dem_test;econom;Lada*;None;15;1'),
        True,
        [
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            },
            {
                'classifier': 'dem_test',
                'class': 'uberx',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            }
        ]
    ),
    (
        ('name;cls;model;price;age;allowing\n'
         'dem_test;econom;Lada*;None;15;2'),
        True,
        [
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            },
            {
                'classifier': 'dem_test',
                'class': 'econom',
                'model': 'Lada*',
                'age': 15,
                'allowing': False,
            },
            {
                'classifier': 'dem_test',
                'class': 'uberx',
                'model': 'Lada*',
                'age': 15,
                'allowing': True,
            },
            {
                'classifier': 'dem_test',
                'class': 'uberx',
                'model': 'Lada*',
                'age': 15,
                'allowing': False,
            }
        ]
    ),
])
@pytest.mark.config(TARIFF_CLASSES_MAPPING={
    'uberx': {'classes': ['econom']},
    'uberselect': {'classes': ['business']}
})
def test_rules_parser(file_content, duplicate_to_uber, expected_rules):
    rules_file = uploadedfile.SimpleUploadedFile(
        "rules.csv",
        file_content,
    )
    rules_parser = classification_rules.RulesParserFromFile(
        rules_file,
        duplicate_to_uber,
    )
    rules = rules_parser.parse_csv_file()
    assert rules == expected_rules


@pytest.mark.parametrize(
    (
        'current_rules_data, new_rules_data, delete_current_rules, '
        'conflict_resolve_policy, dry_run, expected_rules, expected_rules_log'
    ),
    [
        (
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
            ],
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': False},
            ],
            True, 'ours', False,
            [
                {'class': 'business', 'model': 'Toyota*',
                 'age': 5, 'allowing': False},
            ],
            {
                'added': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': False},
                ],
                'conflicted': [],
                'deleted': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Lada*', 'age': 5, 'allowing': False},
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': True},
                ],
            }
        ),
        (
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
            ],
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': False},
            ],
            True, 'ours', True,
            [
                {'class': 'business', 'model': 'Toyota*',
                 'age': 5, 'allowing': False},
            ],
            {
                'added': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': False},
                ],
                'conflicted': [],
                'deleted': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Lada*', 'age': 5, 'allowing': False},
                ],
            }
        ),
        (
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
            ],
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': False},
            ],
            False, 'ours', False,
            [
                {'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
                {'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': False},
            ],
            {
                'added': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': False},
                ],
                'conflicted': [],
                'deleted': [],
            }
        ),
        (
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
            ],
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 4, 'allowing': True},
            ],
            False, 'ours', False,
            [
                {'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'class': 'business',
                 'model': 'Toyota*', 'age': 4, 'allowing': True},
            ],
            {
                'added': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 4, 'allowing': True},
                ],
                'conflicted': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': True},
                ],
                'deleted': [],
            }
        ),
        (
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
            ],
            [
                {'classifier': 'dem_test', 'class': 'business',
                 'model': 'Toyota*', 'age': 4, 'allowing': True},
            ],
            False, 'theirs', False,
            [
                {'class': 'business',
                 'model': 'Lada*', 'age': 5, 'allowing': False},
                {'class': 'business',
                 'model': 'Toyota*', 'age': 5, 'allowing': True},
            ],
            {
                'added': [],
                'conflicted': [
                    {'classifier': 'dem_test', 'class': 'business',
                     'model': 'Toyota*', 'age': 5, 'allowing': True},
                ],
                'deleted': [],
            }
        ),
    ]
)
@pytest.mark.filldb(
    _specified=True, auto_dictionary='', auto_dictionary_special=''
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_rules_builder(current_rules_data, new_rules_data, delete_current_rules,
                       conflict_resolve_policy, dry_run,
                       expected_rules, expected_rules_log):
    current_rules_builder = classification_rules.RulesBuilder(
        current_rules_data,
        True,
        'ours',
        False
    )
    current_rules = current_rules_builder.set_rules()
    current_rules_log = current_rules_builder.get_rules_log()
    assert len(current_rules) == len(current_rules)
    assert len(current_rules_log['added']) == len(current_rules)

    current_db_doc = yield db.classification_rules.find_one()
    current_db_doc_rules = current_db_doc['rules']

    assert len(current_db_doc_rules) == len(current_rules)

    rules_builder = classification_rules.RulesBuilder(
        new_rules_data,
        delete_current_rules,
        conflict_resolve_policy,
        dry_run,
    )
    rules = rules_builder.set_rules()
    rules_log = rules_builder.get_rules_log()
    assert rules == expected_rules
    assert rules_log == expected_rules_log

    new_db_doc = yield db.classification_rules.find_one()
    new_db_doc_rules = new_db_doc['rules']

    if dry_run:
        assert len(new_db_doc_rules) == len(current_rules)
    else:
        assert len(new_db_doc_rules) == len(rules)


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.parametrize('method, file_content, expected_db_doc, code', [
    (
        'post',
        ('name;cls;model;price;age;allowing\n'
         '{NEW_CITY};econom;Ford Focus Wagon;None;15;0\n'
         '{NEW_CITY};business;Hummer*;None;12;1\n'),
        {
            '_id': NEW_CITY,
            'rules': [
                {
                    'age': 15,
                    'class': 'econom',
                    'allowing': False,
                    'model': 'Ford Focus Wagon',
                },
                {
                    'age': 12,
                    'class': 'business',
                    'allowing': True,
                    'model': 'Hummer*',
                }
            ],
            'extended_rules': [
                {
                    'age': 15,
                    'class': 'econom',
                    'allowing': False,
                    'model': 'Ford Focus Wagon',
                },
                {
                    'age': 12,
                    'class': 'business',
                    'allowing': True,
                    'model': 'Hummer Some model',
                },
                {
                    'age': 12,
                    'class': 'business',
                    'allowing': True,
                    'model': 'Hummer H1',
                },
                {
                    'age': 12,
                    'class': 'business',
                    'allowing': True,
                    'model': 'Hummer H2',
                },
                {
                    'age': 12,
                    'class': 'business',
                    'allowing': True,
                    'model': 'Hummer H3',
                },
            ],
            'rules_updated': dateutil.parser.parse('2017-07-20T10:00:00.0'),
            'extended_rules_updated': dateutil.parser.parse(
                '2017-07-20T10:00:00.0'
            ),
        },
        200
    ),
    (
        'post',
        ('name;cls;model;price;age;allowing\n'
         '{NEW_CITY};econom;Ford Focus Wagon;100000;15;0\n'
         '{NEW_CITY};business;Hummer*;None;12;1\n'),
        None,
        400
    ),
    (
        'post',
        ('name;cls;model;price;age;allowing\n'
         '{NEW_CITY};econom;None;None;15;0\n'
         '{NEW_CITY};business;Hummer*;None;12;1\n'),
        None,
        400
    ),
    ('post', 'bad headers\nbad file', None, 400),
    ('get', 'bad method', None, 405)
])
@pytest.mark.filldb(
    _specified=True, auto_dictionary='', auto_dictionary_special=''
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_upload_classifiers_rules(method, file_content, expected_db_doc, code):
    client = django_test.Client()
    if method == 'post':
        rules_file = uploadedfile.SimpleUploadedFile(
            "rules.csv",
            file_content.format(NEW_CITY=NEW_CITY),
        )
        data = {
            'rules_file': rules_file,
            'duplicate_to_uber': False,
            'dry_run': False,
            'delete_current_rules': True,
            'conflict_resolve_policy': 'theirs',
        }
        response = client.post(
            UPLOAD_CLASSIFIERS_RULES_URL,
            data
        )
    elif method == 'get':
        response = client.get(SET_CLASSIFIER_URL)
    assert response.status_code == code
    if code != 200:
        return

    db_doc = yield db.classification_rules.find_one()

    assert set(db_doc.keys()) == set(expected_db_doc.keys())
    for key in ('rules', 'extended_rules'):
        db_rules = db_doc.pop(key)
        expected_rules = expected_db_doc.pop(key)
        for rule in db_rules:
            assert rule in expected_rules

    assert db_doc == expected_db_doc


@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.parametrize('method, data, expected_db_doc, code', [
    (
        'post',
        {
            'name': NEW_CITY,
            'rules': [
                 {
                    'age': 15,
                    'class': 'econom',
                    'allowing': False,
                    'model': 'Ford Focus Wagon',
                 },
                 {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer*'
                 }
            ],
        },
        {
            '_id': NEW_CITY,
            'rules': [
                {
                    'age': 15,
                    'class': 'econom',
                    'allowing': False,
                    'model': 'Ford Focus Wagon',
                },
                {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer*',
                }
            ],
            'extended_rules': [
                {
                    'age': 15,
                    'class': 'econom',
                    'allowing': False,
                    'model': 'Ford Focus Wagon',
                },
                {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer Some model',
                },
                {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer H1',
                },
                {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer H2',
                },
                {
                    'age': 12,
                    'class': 'comfort',
                    'allowing': True,
                    'model': 'Hummer H3',
                },
            ],
            'rules_updated': dateutil.parser.parse('2017-07-20T10:00:00.0'),
            'extended_rules_updated': dateutil.parser.parse(
                '2017-07-20T10:00:00.0'
            ),
        },
        200
    ),
    (
        'post',
        {
            'name': NEW_CITY,
            'rules': [
                {
                    'price': 100000,
                    'age': 10,
                    'class': 'econom',
                    'allowing': False
                },
                {
                    'age': 16,
                    'class': 'econom',
                    'allowing': True,
                    'model': 'Bentley Arnage'
                },
            ],
        },
        {
            '_id': NEW_CITY,
            'rules': [
                {
                    'price': 100000,
                    'age': 10,
                    'class': 'econom',
                    'allowing': False
                },
                {
                    'age': 16,
                    'class': 'econom',
                    'allowing': True,
                    'model': 'Bentley Arnage'
                },
            ],
            'extended_rules': [
                {
                    'price': 100000,
                    'age': 10,
                    'class': 'econom',
                    'allowing': False
                },
                {
                    'age': 16,
                    'class': 'econom',
                    'allowing': True,
                    'model': 'Bentley Arnage'
                },
            ],
            'rules_updated': dateutil.parser.parse('2017-07-20T10:00:00.0'),
            'extended_rules_updated': dateutil.parser.parse(
                '2017-07-20T10:00:00.0'
            ),
        },
        200
    ),
    ('post', {'bad': 'request'}, None, 400),
    ('get', {'name': 'bad_method', 'rules': []}, None, 405)
])
@pytest.mark.filldb(
    _specified=True, auto_dictionary='', auto_dictionary_special=''
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_classifier(method, data, expected_db_doc, code):
    client = django_test.Client()
    if method == 'post':
        response = client.post(
            SET_CLASSIFIER_URL,
            json.dumps(data),
            content_type='application/json'
        )
    elif method == 'get':
        response = client.get(SET_CLASSIFIER_URL)
    assert response.status_code == code
    if code != 200:
        return

    db_doc = yield db.classification_rules.find_one()

    assert set(db_doc.keys()) == set(expected_db_doc.keys())
    for key in ('rules', 'extended_rules'):
        db_rules = db_doc.pop(key)
        expected_rules = expected_db_doc.pop(key)
        for rule in db_rules:
            assert rule in expected_rules

    assert db_doc == expected_db_doc


@pytest.mark.parametrize('method, data, code, expected_response', [
    ('post', {'q': 'Ben arn'}, 200, ['Bentley Arnage']),
    ('post', {'bad': 'request'}, 400, None),
    ('get', {'name': 'bad_method'}, 405, None),
    ('post', {'q': 'No such car'}, 200, []),
    ('post', {'q': 'H'}, 200, ['Hummer', 'Hyundai']),
    ('post', {'q': 'v p'}, 200, ['Volkswagen Passat Variant']),
    ('post', {'q': 'b e'}, 200, ['Bentley Eight',
                                 'Buick Electra',
                                 'Buick Enclave',
                                 'Buick Encore',
                                 'Buick Envision',
                                 'Buick Estate Wagon',
                                 'Buick Excelle'])
])
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
def test_model_suggest(method, data, code, expected_response):
    client = django_test.Client()
    if method == 'post':
        response = client.post(
            MODEL_SUGGEST_URL,
            json.dumps(data),
            content_type='application/json'
        )

    elif method == 'get':
        response = client.get(MODEL_SUGGEST_URL)
    assert response.status_code == code

    if code == 200:
        response_content = json.loads(response.content)
        assert response_content['result'] == expected_response
