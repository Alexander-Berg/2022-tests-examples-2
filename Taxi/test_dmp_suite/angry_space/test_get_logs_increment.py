from connection import angry_space
from dmp_suite.file_utils import from_same_directory
from dmp_suite.angry_space.angry_space_api import ApiWrapper
from dmp_suite.angry_space import angry_space_api
import mock
import json

def new_get_logs_list(self, created_at_from, created_at_to):
    params = {}
    while True:
        with open(from_same_directory(__file__, "data/temp.json")) as f:
            sample = json.load(f)

        data = {'items':sample, 'prev_cursor':'', 'next_cursor':''}
        items = data.get('items')
        if items:
            yield from items

            cursor = data.get('next_cursor')
            params['cursor'] = cursor
            if not cursor:
                break
        else:
            break

def new_get_angry_space_api_wrapper(name='taxi-dwh-angry-space-api'):
    settings = {'api_url':'', 'space_id':'', 'access_token':''}

    return angry_space_api.build(
        api_url=settings['api_url'],
        auth_token=settings['access_token'],
        space_id=settings['space_id'],
    )


def test_get_logs_increment():
    created_at_from = 1627171200 #2021-07-25
    created_at_to = 1627257599 #2021-07-26
    with mock.patch.object(angry_space, 'get_angry_space_api_wrapper', new=new_get_angry_space_api_wrapper):
        api = angry_space.get_angry_space_api_wrapper()
    with mock.patch.object(ApiWrapper, '_get_logs_list', new=new_get_logs_list):
        increment, last_load_timestamp = api.get_logs_increment(created_at_from, created_at_to)

    assert last_load_timestamp == 1627257527 and sum(1 for e in increment) == 4
