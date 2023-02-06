# coding: utf-8

import cStringIO as StringIO

from django.test import client
from django.utils import unittest
import elementflow

from taxi.core import async
from taxi.core import db
from cabinet_api import views as api_views


class TestTokenCheckMiddleware(unittest.TestCase):

    @async.inline_callbacks
    def setUp(self):
        yield db.parks.insert({
            'updated_ts': {'$type': 'timestamp'},
            '_id': '999',
            'apikey': 'xednayixat'
        })

    @async.inline_callbacks
    def tearDown(self):
        yield db.parks.remove({'_id': '999'})

    def test_missing_token_header(self):
        c = client.Client()
        response = c.get('/api/999/ping/')
        self.assertEqual(response.status_code, 403)

    def test_non_alnum_header(self):
        c = client.Client()
        response = c.get('/api/999/ping/', HTTP_YATAXI_API_KEY='xednay.ixat')
        self.assertEqual(response.status_code, 400)

    def test_invalid_token(self):
        c = client.Client()
        response = c.get('/api/999/ping/', HTTP_YATAXI_API_KEY='hentaitaxi')
        self.assertEqual(response.status_code, 403)

    def test_happy_path(self):
        c = client.Client()
        response = c.get('/api/999/ping/', HTTP_YATAXI_API_KEY='xednayixat')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            'Success. You are authenticated as a clid=999'
        )


class TestCompensationBodyGeneration(unittest.TestCase):

    def test_compensation_message_body(self):
        park_doc = {
            'name': u'rainbow', '_id': u'65535', 'city': u'Kaluga'
        }
        form_data = {
            'order_id': 'oRdEr :D',
            'route_from': 'Lunacharskogo',
            'route_to': 'Tulskij per.',
            'trip_time': '2 minutes',
            'tariff': '100 rub / min',
            'service_level': 'VIP',
            'requirements': [],
            'compensation_amount': '200 rub',
            'comment': ''
        }
        email = 'stromsund@y-t.ru'

        # Test data contains tuples (comment text, expected substring)
        test_data = (
            (
                u'',
                u'<test><p><span>Название таксопарка: rainbow</span><br/>'
            ),
            (
                u'Simple Single Line (SSL)',
                u'<test><p><span>Simple Single Line (SSL)</span><br/></p><p>'
            ),
            (
                u'Multi<br>Line',
                u'<test><p><span>Multi</span><br/><span>Line</span><br/></p>'
            )
        )

        for comment_text, expected_substr in test_data:
            form_data['comment'] = comment_text
            output = StringIO.StringIO()
            with elementflow.xml(output, 'test') as xml:
                api_views._generate_compensation_message_body(
                    park_doc, email, form_data, xml
                )
            result = output.getvalue().decode('utf-8')
            self.assertTrue(expected_substr in result)
