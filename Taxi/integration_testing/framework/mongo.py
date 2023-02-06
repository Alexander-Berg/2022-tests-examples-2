import datetime
import pymongo
from pymongo import errors as mongo_errors
import pytest

from taxi.integration_testing.framework import environment
from taxi.integration_testing.framework import files

MONGO_STARTUP_TIMEOUT_SECONDS = 180
MONGO_SHARDS_SETUP_TIMEOUT_SECONDS = 180


@pytest.fixture(scope='session')
def mongo_container(testenv: environment.EnvironmentManager,
                    platform: str) -> environment.TestContainer:
    with files.TarBuilder() as tar_builder:
        tar_builder.add_dir('taxi/logs', mode=0o777)
        tar_builder.add_dir('data/db', mode=0o777)
        tar_builder.add_resource('resfs/file/taxi/integration_testing/framework/mongo/fs', strip_prefix=True,
                                 mode=0o777)
        archive = tar_builder.get_bytes()

    cntnr = testenv.add_container(
        name='mongo',
        image=f'registry.yandex.net/taxi/taxi-integration-{platform}-base',
        command='/taxi/run/mongo-init.sh',
        hostname='None',
        environment={
            'REQUESTS_CA_BUNDLE': '/usr/local/share/ca-certificates/rootCA.crt',
            'SSL_CERT_FILE': '/usr/local/share/ca-certificates/rootCA.crt',
            'LANG': 'ru_RU.UTF-8',
            'MONGO_RAMDISK': 'None'
        },
        archive=archive,
        privileged=False,
        tmpfs={
            '/mnt/ram': 'size=4G'
        },
        ports=[27017],
        aliases=[
            'mongo.taxi.yandex'
        ]
    )

    return cntnr


@pytest.fixture(scope='session')
def mongo(mongo_container: environment.TestContainer) -> pymongo.MongoClient:
    mongo_endpoint = mongo_container.get_endpoint(27017)

    mongo_client = pymongo.MongoClient(
        host=f'mongodb://{mongo_endpoint}/?retryWrites=false',
        socketTimeoutMS=60000,
        connectTimeoutMS=10000,
        waitQueueTimeoutMS=10000,
    )

    # wait until mongo connection is established
    mongo_start_timeout: datetime.timedelta = datetime.timedelta(seconds=MONGO_STARTUP_TIMEOUT_SECONDS)
    started = datetime.datetime.now()
    while True:
        try:
            result = mongo_client.admin.command('ping')

            if result['ok'] == 1.0:
                break
            else:
                raise environment.EnvironmentSetupError('mongo ping returned not \'ok\' result')
        except mongo_errors.ConnectionFailure:
            pass

        if datetime.datetime.now() > started + mongo_start_timeout:
            raise environment.EnvironmentSetupError(f'mongo did not respond during {mongo_start_timeout}')

    # wait until mongo shards are created
    mongo_shards_timeout: datetime.timedelta = datetime.timedelta(seconds=MONGO_SHARDS_SETUP_TIMEOUT_SECONDS)
    started = datetime.datetime.now()
    while True:
        if mongo_client.get_database('config')['shards'].count({}) > 0:
            break

        if datetime.datetime.now() > started + mongo_shards_timeout:
            raise environment.EnvironmentSetupError(f'mongo shards were not created during {mongo_shards_timeout}')

    yield mongo_client
    mongo_client.close()
