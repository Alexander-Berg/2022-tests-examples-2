import flask
import logging
from multiprocessing import Process
import pytest

import yatest.common.network


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MTAPI_MOCK_HOST = 'localhost'
MTAPI_ROOT_PATH = '/v1/cluster'

port_manager = yatest.common.network.PortManager()
port = port_manager.get_port()

app = flask.Flask('mtapi_mock')


@app.route(MTAPI_ROOT_PATH + '/get')
def get():
    fqdn = flask.request.args.getlist('fqdn')
    field = flask.request.args.getlist('field')

    if len(fqdn) == 1:
        return flask.jsonify(
            result=True,
            data=[{
                'dc_name': 'sas',
                'layer': 1,
                'index': 0,
                'shard': 1,
                'replica': 1,
                'root_group': 'mtlog',
            }],
        )
    elif field:
        return flask.jsonify(
            result=True,
            data=[
                {
                    'dc_name': 'sas',
                    'root_group': 'mtlog',
                },
                {
                    'dc_name': 'iva',
                    'root_group': 'mtlog',
                },
            ]
        )


def start_server():
    app.run(MTAPI_MOCK_HOST, port)


@pytest.fixture(scope='session')
def mtapi():
    server = Process(target=start_server)
    logger.debug('Starting Flask server...')
    server.start()

    yield app

    logger.debug('Stopping Flask server...')
    server.terminate()
    server.join()
    logger.debug('Flask server stopped.')


@pytest.fixture(scope='session')
def mtapi_url():
    return 'http://{host}:{port}{root_path}'.format(host=MTAPI_MOCK_HOST, port=port, root_path=MTAPI_ROOT_PATH)
