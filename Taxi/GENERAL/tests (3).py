import bson
from django.test import client
from django.utils import unittest

from taxi.core import async
from taxi.core import db


class NewRatingInCabinetTestCase(unittest.TestCase):
    """
    This test case does not cover any ratings logic.
    Only correctness of a view code.
    """
    @async.inline_callbacks
    def setUp(self):
        yield db.drivers.insert({
            'updated_ts': bson.timestamp.Timestamp(0, 0),
            '_id': '1_django1',
            '_state': 'active',
            'uuid': 1,
            'clid': 1,
            'driver_license': 'djangoA1',
            'car': {'model': 'KIA RIO'},
        })
        yield db.unique_drivers.insert({
            'updated_ts': bson.timestamp.Timestamp(0, 0),
            'score':
            {
                'total': 1.0,
                'delays': 1,
                'cancelled': 0,
            },
                'licenses': [{'license': 'djangoA1'}],
            })

    @async.inline_callbacks
    def tearDown(self):
        yield db.drivers.remove({'_id': '1_django1'})
        yield db.unique_drivers.remove(
            {'licenses.license': 'djangoA1'}
        )

    @async.inline_callbacks
    def test_totals_from_profile(self):
        c = client.Client()
        response = c.get('/drivers/')
        self.assertEqual(200, response.status_code)
        self.assertTrue('<td>3.8</td>' in response.content)

    @async.inline_callbacks
    def test_totals_from_unique_profile(self):
        c = client.Client()
        response = c.get('/drivers/')
        self.assertEqual(200, response.status_code)
        self.assertFalse('<td>3.8</td>' in response.content)
        self.assertTrue('<td>5.0</td>' in response.content)
