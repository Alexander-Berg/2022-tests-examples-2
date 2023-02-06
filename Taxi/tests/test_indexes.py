import unittest
import sys
from mock import patch

sys.path.append('src')
from mongodb_health.indexes import check # noqa


class IndexesTestCase(unittest.TestCase):

    @patch('mongodb_health.indexes.get_db_indexes')
    @patch('mongodb_health.indexes.make_connection')
    @patch('mongodb_health.indexes.make_authorization')
    @patch('mongodb_health.indexes.get_rs_status')
    def test_excludes(self, mock_get_rs_status, mock_make_authorization, mock_make_connection, mock_get_db_indexes):
        status = {'members': [{'_id': 2,
                               'configVersion': 275214,
                               'health': 1.0,
                               'name': 'ugr7-cat-mongo01.ydf.yandex.net:27017',
                               'pingMs': 1,
                               'state': 2,
                               'stateStr': 'SECONDARY',
                               'syncingTo': 'sas-cat-mongo01.ydf.yandex.net:27017',
                               'uptime': 1808358},
                              {'_id': 3,
                               'configVersion': 275214,
                               'health': 1.0,
                               'name': 'mytd2-cat-mongo01.ydf.yandex.net:27017',
                               'self': True,
                               'state': 2,
                               'stateStr': 'SECONDARY',
                               'syncingTo': 'sas-cat-mongo01.ydf.yandex.net:27017',
                               'uptime': 11684998},
                              {'_id': 4,
                               'configVersion': 275214,
                               'health': 1.0,
                               'name': 'sas-cat-mongo01.ydf.yandex.net:27017',
                               'pingMs': 8,
                               'state': 1,
                               'stateStr': 'PRIMARY',
                               'uptime': 1808362},
                              {'_id': 5,
                               'configVersion': 275214,
                               'health': 1.0,
                               'name': 'sas-cat-mongo-backup01.ydf.yandex.net:27017',
                               'pingMs': 8,
                               'state': 2,
                               'stateStr': 'SECONDARY',
                               'syncingTo': 'sas-cat-mongo01.ydf.yandex.net:27017',
                               'uptime': 56349}],
                  'myState': 2,
                  'ok': 1.0,
                  'set': 'ydf-stable-caterpillar-mongo',
                  'syncingTo': 'sas-cat-mongo01.ydf.yandex.net:27017'}

        indexes = {u'mytd2-cat-mongo01.ydf.yandex.net': {u'caterpillar': 12,
                                                         u'caterpillar_bazinga': 9,
                                                         u'worker_bazinga': 3},
                   u'sas-cat-mongo-backup01.ydf.yandex.net': {u'caterpillar': 0,
                                                              u'caterpillar_bazinga': 0,
                                                              u'worker_bazinga': 0},
                   u'sas-cat-mongo01.ydf.yandex.net': {u'caterpillar': 12,
                                                       u'caterpillar_bazinga': 9,
                                                       u'worker_bazinga': 3},
                   u'ugr7-cat-mongo01.ydf.yandex.net': {u'caterpillar': 12,
                                                        u'caterpillar_bazinga': 9,
                                                        u'worker_bazinga': 3}}

        mock_make_connection.side_effect = lambda **kwargs: kwargs
        mock_make_authorization.side_effect = lambda conn, *args: conn
        mock_get_db_indexes.side_effect = lambda kwargs: indexes[kwargs['host']]
        mock_get_rs_status.return_value = ('ok', status, '0;Ok;Ok')
        self.assertEqual(check('__all__', 'sas-cat-mongo-backup01.ydf.yandex.net:27017'),
                         '0;OK;Indexes count match.')
