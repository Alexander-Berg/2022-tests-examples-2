import datetime
import pytest
import pymongo
import requests
import os


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'stq_agent_queue(name): a stq-queue to be used in test',
    )


def pytest_addoption(parser):
    # options set by mongo and redis recipes
    parser.addoption('--mongo')
    parser.addoption('--redis-host')
    parser.addoption('--redis-sentinel-port')
    parser.addoption('--redis-master-port')


@pytest.fixture(autouse=True)
def stq_agent_queue(request):
    marks = [i for i in request.node.iter_markers('stq_agent_queue')]
    stq_config_docs = [
        {
            '_id': mark.args[0],
            'shards': [
                {
                    'collection': mark.args[0] + '_0',
                    'connection': 'stq',
                    'database': 'db',
                    'hosts': [],
                },
            ],
            'updated': datetime.datetime.utcnow(),
            'worker_configs': {
                'instances': 1,
                'max_execution_time': 10,
                'max_tasks': 100,
                'polling_interval': 0.1,
            },
        }
        for mark in marks
    ]
    if stq_config_docs:
        connection_string = request.config.getoption('--mongo')
        assert connection_string
        client = pymongo.MongoClient(connection_string)
        db = client.dbstq_config
        collection = db.stq_config
        collection.insert_many(stq_config_docs)
        server_port = os.getenv('STQ_AGENT_LISTEN_PORT', 1180)
        response = requests.post(
            f'http://localhost:{server_port}/tests/control',
            json={
                'invalidate_caches': {
                    'update_type': 'incremental',
                    'names': ['stqs-config'],
                },
            },
        )
        assert response.status_code == 200
