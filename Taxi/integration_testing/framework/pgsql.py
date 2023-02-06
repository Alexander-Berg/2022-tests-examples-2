import datetime
import psycopg2
import pytest

from taxi.integration_testing.framework import environment


@pytest.fixture(scope='session')
def postgres_container(testenv: environment.EnvironmentManager) -> environment.TestContainer:
    return testenv.add_container(
        name='postgres',
        image='registry.yandex.net/taxi/externalimages/postgres',
        healthcheck={
            'test': '/taxi/tools/healthcheck.sh env PGPASSWORD=password pg_isready -U user -h pgaas.mail.yandex.net -p 5432 -d dborders -q',
            'timeout': '30s',
            'interval': '5s',
            'retries': '20'
        },
        environment={
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'password'
        },
        tmpfs={
            '/var/lib/postgresql/data': 'size=4G'
        },
        ports=[5432],
        aliases=[
            'pgaas.mail.yandex.net'
        ]
    )


class TestPostgres:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def get_connection(self, name: str) -> psycopg2._psycopg.connection:
        return psycopg2.connect(f'{self.connection_string}/{name}')

    def create_db(self, name: str):
        print(f'Creating postgres database {name}')
        with self.get_connection('postgres') as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE "{name}"')

    def drop_db(self, name: str):
        print(f'Dropping postgres database {name}')
        with self.get_connection('postgres') as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(f'DROP DATABASE "{name}"')

    def exec_sql_script(self, db_name: str, path: str):
        with open(path) as file:
            sql = file.read()

        self.exec_sql(db_name, sql)

    def exec_sql(self, db_name: str, sql: str):
        with self.get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()

        conn.close()

    def wait_until_healthy(self):
        # wait until postgres connection is established
        postgres_start_timeout: datetime.timedelta = datetime.timedelta(seconds=180)
        started = datetime.datetime.now()

        while True:
            try:
                with self.get_connection('postgres') as connection:
                    with connection.cursor() as cursor:
                        cursor.execute('select 1')

                break
            except Exception:
                pass

            if datetime.datetime.now() > started + postgres_start_timeout:
                raise environment.EnvironmentSetupError(f'postgres did not respond during {postgres_start_timeout}')


@pytest.fixture(scope='session')
def postgres(postgres_container: environment.TestContainer) -> TestPostgres:
    postgres_endpoint = postgres_container.get_endpoint(5432)
    result = TestPostgres(f'postgresql://user:password@{postgres_endpoint}')
    result.wait_until_healthy()
    return result
