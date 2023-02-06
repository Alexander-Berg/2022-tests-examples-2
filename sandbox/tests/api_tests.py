from __future__ import absolute_import

# from django.core.urlresolvers import reverse

from unittest import TestCase
# from rest_framework.test import APITestCase
# from rest_framework import status

from django.test.runner import DiscoverRunner


class DatabaselessTestRunner(DiscoverRunner):
    """A test suite runner that does not set up and tear down a database."""

    def setup_databases(self):
        """Overrides DjangoTestSuiteRunner"""
        pass

    def teardown_databases(self, *args):
        """Overrides DjangoTestSuiteRunner"""
        pass


class MongoTestCase(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    # mongodb_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    mongodb_db_name = 'test_%s' % 'brand_new_events'
    mongodb_port = 27019

    def setUp(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_db_name)

    def tearDown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_db_name)
        disconnect()


# class EventsTests(APITestCase, MongoTestCase):
#     def test_create_event(self):
#         url = reverse('events-collection')
#         data = {
#             'events': [
#                 {
#                     'name': 'test_event',
#                     'params': {
#                         'param1': 'value1',
#                         'param2': 'value2'
#                     }
#                 }
#             ]
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['ids']), 1)
#
#     def test_get_event(self):
#         url = reverse('events-collection')
#         event_dict = {
#             'name': 'test_event',
#             'params': {
#                 'param1': 'value1',
#                 'param2': 'value2'
#             }
#         }
#         data = {
#             'events': [event_dict]
#         }
#         response = self.client.post(url, data, format='json')
#         event_id = response.data['ids'][0]
#
#         url = reverse('events-item', kwargs={'event_id': event_id})
#         response = self.client.get(url)
#         self.assertEqual(response.data['result']['name'], event_dict['name'])
#         self.assertEqual(response.data['result']['params'], event_dict['params'])
#
#     def test_get_events(self):
#         url = reverse('events-collection')
#         events = [
#             {
#                 'name': 'test_event_1',
#                 'params': {
#                     'param1': 'value1_1',
#                     'param2': 'value2_1'
#                 }
#             },
#             {
#                 'name': 'test_event_2',
#                 'params': {
#                     'param1': 'value1_2',
#                     'param2': 'value2_2'
#                 }
#             }
#         ]
#         data = {'events': events}
#         response = self.client.post(url, data, format='json')
#         event_ids = response.data['ids']
#         print event_ids
#
#         response = self.client.get(url)
#         resp_data = response.data['result']
#
#         ids = (x['_id'] for x in resp_data)
#
#         self.assertTrue(all(x in ids for x in event_ids))
#
#     def test_pagination(self):
#         url = reverse('events-collection')
#         events = [{
#                 'name': 'test_event_%s' % i,
#                 'params': {
#                     'param1': 'value1_%s' % i,
#                     'param2': 'value2_%s' % i
#                 }
#             } for i in xrange(1, 101)]
#
#         data = {'events': events}
#         response = self.client.post(url, data, format='json')
#         event_ids = response.data['ids']
#
#         response = self.client.get(url, data={'limit': 20})
#         self.assertEqual(len(response.data['result']), 20)
#
#         response = self.client.get(url, data={'skip': 10})
#         self.assertEqual(response.data['result'][0]['_id'], event_ids[10])
#
#         response = self.client.get(url, data={'skip': 10, 'limit': 20})
#         self.assertEqual(len(response.data['result']), 20)
#         self.assertEqual(response.data['result'][0]['_id'], event_ids[10])
#         self.assertEqual(response.data['result'][-1]['_id'], event_ids[29])
#
#     def test_filter_name(self):
#         url = reverse('events-collection')
#         events = [{
#                 'name': 'test_event_1',
#                 'params': {
#                     'param1': 'value1_%s' % i,
#                     'param2': 'value2_%s' % i
#                 }
#             } for i in xrange(1, 101)]
#
#         events += [{
#                 'name': 'test_event_2',
#                 'params': {
#                     'param1': 'value1_%s' % i,
#                     'param2': 'value2_%s' % i
#                 }
#             } for i in xrange(1, 51)]
#
#         data = {'events': events}
#         self.client.post(url, data, format='json')
#
#         response = self.client.get(url, data={'name': 'test_event_1', 'limit': 150})
#         self.assertEqual(len(response.data['result']), 100)
#         self.assertTrue(all(x['name'] == 'test_event_1' for x in response.data['result']))
#
#     def test_filter_params(self):
#         url = reverse('events-collection')
#         events = [{
#                 'name': 'test_event_%s' % i,
#                 'params': {
#                     'param1': 'value1_%s' % i,
#                     'param2': 'value2_%s' % i
#                 }
#             } for i in xrange(1, 101)]
#
#         events += [{
#                 'name': 'test_event_2',
#                 'params': {
#                     'param1': 'value1_%s' % i,
#                     'param2': 'value2_%s' % i
#                 }
#             } for i in xrange(1, 51)]
#
#         data = {'events': events}
#         self.client.post(url, data, format='json')
#
#         response = self.client.get(url, data={'limit': 200, 'params__param1': 'value1_1'})
#         self.assertEqual(len(response.data['result']), 2)
#         names = [x['name'] for x in response.data['result']]
#         self.assertTrue('test_event_1' in names)
#         self.assertTrue('test_event_2' in names)
#
#
# class ActionConfigsTests(APITestCase, MongoTestCase):
#
#     def _get_test_config(
#             self,
#             task_type='STATINFRA_TASK',
#             action_id='external:stjob-regular/testtesttest',
#             ev_name='clock',
#             scale='5m'
#     ):
#         return {
#             'task_type': task_type,
#             'action_params': {
#                 'action_id': action_id
#             },
#             'event_deps': [
#                 {
#                     'name': ev_name,
#                     'params': {
#                         'scale': scale,
#                         'timestamp': '~'
#                     }
#                 }
#             ]
#         }
#
#     def test_create_action_config(self):
#         url = reverse('configs-collection')
#         config = self._get_test_config()
#         response = self.client.post(url, data=config, format='json')
#         ac_id = response.data['id']
#
#         url = reverse('configs-item', kwargs={'ac_id': ac_id})
#         response = self.client.get(url)
#         self.assertEqual(response.data['result']['_id'], ac_id)
#         self.assertEqual(response.data['result']['task_type'], config['task_type'])
#         self.assertTrue(response.data['result']['event_deps'][0].viewitems() >= config['event_deps'][0].viewitems())
#
#     def test_get_all_configs(self):
#         config1 = self._get_test_config()
#         config2 = self._get_test_config(action_id='testtesttest222', scale='10m')
#
#         url = reverse('configs-collection')
#
#         response = self.client.post(url, data=config1, format='json')
#         ac_id1 = response.data['id']
#
#         response = self.client.post(url, data=config2, format='json')
#         ac_id2 = response.data['id']
#
#         response = self.client.get(url)
#         self.assertEqual(len(response.data['result']), 2)
#         self.assertTrue(all(ac_id in (x['_id'] for x in response.data['result']) for ac_id in (ac_id1, ac_id2)))
#
#     def test_delete_config(self):
#         config = self._get_test_config()
#         url = reverse('configs-collection')
#         response = self.client.post(url, data=config, format='json')
#         ac_id = response.data['id']
#
#         url = reverse('configs-item', kwargs={'ac_id': ac_id})
#         self.client.delete(url)
#
#         url = reverse('configs-collection')
#         response = self.client.get(url)
#         self.assertFalse(ac_id in (x['_id'] for x in response.data['result']))
#
#     def test_modify_config(self):
#         config = self._get_test_config()
#         url = reverse('configs-collection')
#         response = self.client.post(url, data=config, format='json')
#         ac_id = response.data['id']
#
#         config['event_deps'][0]['params']['scale'] = '10m'
#         url = reverse('configs-item', kwargs={'ac_id': ac_id})
#         self.client.put(url, data=config, format='json')
#
#         response = self.client.get(url)
#         self.assertEqual(response.data['result']['_id'], ac_id)
#         self.assertEqual(response.data['result']['task_type'], config['task_type'])
#         self.assertEqual(response.data['result']['event_deps'][0]['params']['scale'], '10m')
#
#     def test_get_filter(self):
#         config1 = self._get_test_config()
#         config2 = self._get_test_config(action_id='testtesttest222', scale='10m')
#
#         url = reverse('configs-collection')
#
#         response = self.client.post(url, data=config1, format='json')
#         ac_id1 = response.data['id']
#
#         response = self.client.post(url, data=config2, format='json')
#         ac_id2 = response.data['id']
#
#         response = self.client.get(url, data={'action_params__action_id': config1['action_params']['action_id']})
#         confs = response.data['result']
#         self.assertEqual(len(confs), 1)
#         self.assertEqual(confs[0]['action_params']['action_id'], config1['action_params']['action_id'])
