# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from StringIO import StringIO

from django import test as django_test

import bson
import datetime
import freezegun
import json
import pytest

from taxi.core import db
from taxiadmin import audit


def with_ticket(doc):
    newdoc = doc.copy()
    newdoc['ticket'] = 'FAKETICKET-1'
    return newdoc


@pytest.fixture(autouse=True)
def no_audit_checks(monkeypatch):
    def fetch_ticket_from_url(value):
        assert type(value) in (str, unicode)
        return value

    def check_ticket(ticket, *args, **kwargs):
        if not ticket:
            raise audit.TicketError('Even a fake ticket is not present!')

    monkeypatch.setattr(audit, 'fetch_ticket_from_url', fetch_ticket_from_url)
    monkeypatch.setattr(audit, 'check_ticket', check_ticket)


@pytest.mark.asyncenv('blocking')
def test_list_promostories():
    response = django_test.Client().post('/api/promo-stories/list/',
                                         data=json.dumps({}),
                                         content_type='application/json')
    assert response.status_code == 200, response.content
    assert json.loads(response.content)['promostories'] == [
        {'id': '556efa92a955205ad71edef3', 'name': 'story_1', 'active': True},
        {'id': '456', 'name': 'story_2', 'active': True},
        {'id': '789', 'name': 'story_3', 'active': True}
    ]


@pytest.mark.asyncenv('blocking')
def test_list_promostories_limit_offset():
    response = django_test.Client().post('/api/promo-stories/list/',
                                         data=json.dumps(
                                             {
                                                 'offset': 1,
                                                 'limit': 2
                                             }
                                         ),
                                         content_type='application/json'
                                         )
    assert response.status_code == 200, response.content
    assert json.loads(response.content)['promostories'] == [
        {'id': '456', 'name': 'story_2', 'active': True},
        {'id': '789', 'name': 'story_3', 'active': True}
    ]


@pytest.mark.xfail(reason='should not work')
@pytest.mark.asyncenv('blocking')
def test_list_promostories_broken_offset():
    response = django_test.Client().post('/api/promo-stories/list/',
                                         data=json.dumps(
                                             {
                                                 'offset': 'a',
                                                 'limit': 2
                                             }
                                         ),
                                         content_type='application/json'
                                         )
    assert response.status_code == 500, response.content


@pytest.mark.config(
    PROMO_STORIES_SETTINGS={
        'story_1': {
            'countries': ['ru'],
            'auto_activate': {
                'start': '2018-01-01T00:00:00Z'
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
def test_get_promostory():
    promo_id = '556efa92a955205ad71edef3'
    response = django_test.Client().get(
        '/api/promo-stories/items/{}/'.format(promo_id)
    )
    expected = {
        'id': promo_id,
        'name': 'story_1',
        'active': True,
        'button_title_key': 'story_button_1_key',
        'created': u'1970-01-01T03:00:12+0300',
        'targeting': {
            'countries': ['ru'],
            'auto_activate': {
                'start': '2018-01-01T00:00:00Z'
            }
        },
        'languages': [
            {
                'locale': 'ka',
                'teaser_image': 'http://host/story_image_1_ka.png',
                'button_link': 'http://www.apple_1_ka.com',
                'media': [
                    {
                        'type': 'video',
                        'content': 'http://host/1_ka.mp4',
                        'show_button': True
                    },
                    {
                        'type': 'video',
                        'content': 'http://host/10_ka.mp4',
                        'show_button': True
                    }
                ]
            }
        ]
    }

    assert response.status_code == 200, response.content
    assert json.loads(response.content) == expected


@pytest.mark.asyncenv('blocking')
def test_delete_promo_story(patch, no_audit_checks):
    '''
    Should delete:
        1) entry in db
        2) files from MDS

    '''

    key_names = ['/story_image_1_ka.png', '/1_ka.mp4', '/10_ka.mp4']

    class MockBucket:
        def delete_keys(self, key_names_to_remove, quiet=False):
            checks = [key_name in key_names for key_name in key_names_to_remove]
            assert all(checks)
            for key_name in key_names_to_remove:
                key_names.remove(key_name)
            return []

        def get_key(self, key_name):
            return 'key'

    @patch('taxiadmin.api.views.promo_stories._get_bucket')
    def _get_bucket():
        return MockBucket()

    promo_id = '556efa92a955205ad71edef3'

    doc = db.promo_stories.find_one({'_id': promo_id}).result
    assert doc

    response = django_test.Client().post(
        '/api/promo-stories/items/{}/delete/'.format(promo_id),
        data=json.dumps(with_ticket({})),
        content_type='application/json'
    )

    assert response.status_code == 200, response.content

    # 1) check delete entry in db
    doc = db.promo_stories.find_one({'_id': promo_id}).result
    assert doc is None

    # 2) check delete files in MDS
    assert key_names == []


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'ka'])
@pytest.mark.asyncenv('blocking')
def test_create_promo_story(patch, no_audit_checks):
    NOW = datetime.datetime(2018, 4, 21, 10)

    story = {
      'name': 'some_story',
      'active': True,
      'button_title_key': 'promo_story.sdc.button_title',
      'languages': [
        {
          'locale': 'en',
          'teaser_image': 'https://promo-stories.s3.yandex.net/some_story/en/teazer_image.png',
          'button_link': 'http://www.apple_1_ka.com',
          'media': [
            {
              'type': 'video',
              'content': 'https://promo-stories.s3.yandex.net/some_story/en/sdc1.mp4',
              'show_button': True
            },
            {
              'type': 'video',
              'content': 'https://promo-stories.s3.yandex.net/some_story/en/sdc2.mp4',
              'show_button': False
            }
          ]
        }
      ]
    }

    @patch('taxiadmin.api.views.promo_stories._check_tanker_key')
    def _check_tanker_key(key_name, locale):
        return True

    # 1) create story
    with freezegun.freeze_time(NOW, ignore=['']):
        response = django_test.Client().post('/api/promo-stories/items/',
                                             json.dumps(with_ticket(story)),
                                             content_type='application/json')
    assert response.status_code == 200, response.content
    content = json.loads(response.content)

    promo_id = content['id']
    doc = db.promo_stories.find_one({'_id': bson.objectid.ObjectId(promo_id)}).result
    doc.pop('_id')

    assert doc['updated'] == doc['created']
    doc.pop('updated')
    doc.pop('created')

    assert doc == story


@pytest.mark.config(
    PROMO_STORIES_SETTINGS={
        'story_1': {
            'countries': ['en'],
            'auto_activate': {
                'start': '2018-01-01T00:00:00Z'
            }
        }
    }
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_promostory(patch, no_audit_checks):
    @patch('taxiadmin.api.views.promo_stories._check_tanker_key')
    def _check_tanker_key(key_name, locale):
        return True

    promo_id = '556efa92a955205ad71edef3'

    edit_story = yield db.promo_stories.find_one(promo_id)
    assert edit_story
    edit_story.pop('_id')
    edit_story.pop('created')
    if 'updated' in edit_story:
        edit_story.pop('updated')
    edit_story['languages'][0]['locale'] = 'en'
    edit_targeting = {
        'countries': ['ru'],
        'auto_activate': {'end': '2018-08-01T00:01:02+3'},
        'match_with_experiments': True
    }
    edit_story['targeting'] = edit_targeting

    response = yield django_test.Client().post(
        '/api/promo-stories/items/{}/update/'.format(promo_id),
        json.dumps(with_ticket(edit_story)),
        content_type='application/json'
    )

    assert response.status_code == 400


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'ka'])
def test_button_title(no_audit_checks):

    story = {
        'name': 'some_story',
        'languages': [
            {
                'button_title': 'hello',
                'teaser_image': '',
                'button_link': '',
                'locale': 'en',
                'media': []
            }
        ],
    }

    response = django_test.Client().post('/api/promo-stories/items/',
                                         json.dumps(with_ticket(story)),
                                         content_type='application/json')
    assert response.status_code == 200, response.content


@pytest.mark.asyncenv('blocking')
def test_deactivate_story(no_audit_checks):

    good_locale = 'en'

    story = {
        'name': 'some_story',
        'active': True,
        'button_title_key': 'promo_story.sdc.button_title',
        'languages': [
            {
                'locale': good_locale,
                'teaser_image': 'https://promo-stories.s3.yandex.net/some_story/en/teazer_image.png',
                'button_link': 'http://www.apple_1_ka.com',
                'media': [
                    {
                        'type': 'video',
                        'content': 'https://promo-stories.s3.yandex.net/some_story/en/sdc1.mp4',
                        'show_button': True
                    },
                    {
                        'type': 'video',
                        'content': 'https://promo-stories.s3.yandex.net/some_story/en/sdc2.mp4',
                        'show_button': False
                    }
                ]
            }
        ]
    }
    # 1) create normal story

    response = django_test.Client().post('/api/promo-stories/items/',
                                         json.dumps(with_ticket(story)),
                                         content_type='application/json')
    assert response.status_code == 200, response.content
    content = json.loads(response.content)

    promo_id = content['id']
    doc = db.promo_stories.find_one({'_id': bson.objectid.ObjectId(promo_id)}).result
    doc.pop('_id', None)

    assert doc['updated'] == doc['created']
    doc.pop('updated', None)
    doc.pop('created', None)
    assert doc == story
    # 2) activate it
    url = '/api/promo-stories/items/{}/status/'.format(promo_id)
    response = django_test.Client().post(url,
                                        json.dumps(with_ticket({
                                            'active': True})),
                                        content_type='application/json')
    assert response.status_code == 200, response.content
    doc = db.promo_stories.find_one(bson.ObjectId(promo_id)).result
    assert doc['active']
    assert doc['name']
    assert doc['languages']

    # 3) deactivate it
    response = django_test.Client().post(url,
                                        json.dumps(with_ticket({'active': False})),
                                        content_type='application/json')
    assert response.status_code == 200, response.content
    doc = db.promo_stories.find_one(bson.ObjectId(promo_id)).result
    assert not doc['active']


@pytest.mark.asyncenv('blocking')
def test_upload_media(patch, no_audit_checks):

    @patch('boto.s3.bucket.Bucket.get_key')
    def get_key(key_name):
        assert key_name == '/sdc/ka/sdc2.mp4'
        return None

    @patch('boto.s3.bucket.Bucket.delete_key')
    def delete_key(key_name):
        return

    @patch('taxiadmin.api.views.promo_stories._get_bucket')
    def _get_bucket():
        return None

    content = 'somecontent'

    @patch('taxi.external.s3_wrapper.upload_object')
    def upload_object(bucket, key, data, metadata=None):
        assert data == content
        return None

    s = StringIO(content)
    s.name = 'somename'

    s2 = StringIO(content)
    s2.name = 'somename2'

    teaser = StringIO('somecontent')
    teaser.name = 'teaser.png'

    response = django_test.Client().post(
        '/api/promo-stories/items/456/en/media/',
             {
                 'media': [s, s2],
                 'teaser_image': teaser,
             }
    )

    assert response.status_code == 200, response.content
    assert json.loads(response.content)['urls'] == [
        {
            'name': 'somename',
            'url': u'https://promo-stories.s3.yandex.net/story_2/en/c66868b67fa4d2f7e2d51d935bac246015ef0577'
        },
        {
            'name': 'somename2',
            'url': u'https://promo-stories.s3.yandex.net/story_2/en/52ecdde9448ad41d898eb963fb77ba48419413cd'
        },
        {
            'name': 'teaser.png',
            'url': u'https://promo-stories.s3.yandex.net/story_2/en/c2b4fe1ff7910f674c706f3a4658de4f1f01cd43.png'
        },
    ]


MEDIA_LIMIT_BYTES = 2048


@pytest.mark.config(
    PROMO_STORIES_MEDIA_LIMITS={
        'image': {
            'max_size_kb': MEDIA_LIMIT_BYTES / 1024,
            'extra_message': 'send help',
        },
    }
)
# NB: taxi/backend django version guesses content type from filename
@pytest.mark.parametrize('file_name,size,expected_status_code', [
    ('image.png', MEDIA_LIMIT_BYTES, 200),
    ('image.png', MEDIA_LIMIT_BYTES + 1, 400),
    ('image.jpeg', MEDIA_LIMIT_BYTES + 1, 400),
    ('video.mp4', MEDIA_LIMIT_BYTES + 1, 200),
])
@pytest.mark.asyncenv('blocking')
def test_upload_media_limits(
    patch, no_audit_checks, file_name, size, expected_status_code
):

    @patch('boto.s3.bucket.Bucket.get_key')
    def get_key(key_name):
        assert key_name == '/sdc/ka/sdc2.mp4'
        return None

    @patch('boto.s3.bucket.Bucket.delete_key')
    def delete_key(key_name):
        return

    @patch('taxiadmin.api.views.promo_stories._get_bucket')
    def _get_bucket():
        return None

    @patch('taxi.external.s3_wrapper.upload_object')
    def upload_object(*args, **kwargs):
        return None

    media = StringIO('a' * size)
    media.name = file_name
    response = django_test.Client().post(
        '/api/promo-stories/items/456/en/media/',
             {
                 'media': [media],
             }
    )

    assert response.status_code == expected_status_code, response.content


@pytest.mark.xfail(reason='This feature is not implemented yet')
@pytest.mark.asyncenv('blocking')
def test_delete_media(patch):

    @patch('boto.s3.bucket.Bucket.get_key')
    def get_key(key_name):
        assert key_name == '/sdc/ka/sdc2.mp4'
        return None

    @patch('boto.s3.bucket.Bucket.delete_key')
    def delete_key(key_name):
        return

    data = {
        'url': 'https://promo-stories.s3.yandex.net/sdc/ka/sdc2.mp4'
    }
    response = django_test.Client().delete('/api/promo-stories/items/123/media/',
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {}
