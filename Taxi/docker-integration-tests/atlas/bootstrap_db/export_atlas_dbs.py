import json

from pymongo import MongoClient


def _get_mongo_connection_string(credentials):
    """
    Preparing list of connections strings for pymong.MongoClient.
    There are multiple connections strings for single client in
    case of direct connections to mongo without proxy. In case of
    connections to local mongos there is only one element in return
    list.

    :param credentials: dict() with connections params from secdist
    :return: list(str)
    """

    connection_string_template = 'mongodb://'
    '{user}:{password}@{host}:{port}/{database}'
    connection_list = list()
    hosts = credentials['host'].split(',')
    connection_instance_params = credentials.copy()
    for host in hosts:
        connection_instance_params['host'] = host
        try:
            connection_string = connection_string_template.format(
                **connection_instance_params)
        except KeyError:
            pass
        connection_list.append(connection_string)
    return connection_list


_credentials = {
    'host': '',
    'port': '',
    'user': '',
    'password': '',
    'database': 'atlas',
}

_connections = _get_mongo_connection_string(_credentials)
_client = MongoClient(_connections)

_cities_list = [i for i in _client.atlas.cities.find()]

for item in _cities_list:
    item.pop('updated', '')

_configs_list = [i for i in _client.atlas.configs_frontend.find()]

with open('db_configs_frontend.json', 'w') as f:
    for item in json.dumps(_configs_list):
        f.write(item)

_classes_list = [i for i in _client.atlas.classes.find()]

for item in _classes_list:
    item.pop('_id', '')

with open('db_classes.json', 'w') as f:
    for item in json.dumps(_classes_list):
        f.write(item)
