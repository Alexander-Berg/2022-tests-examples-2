import pathlib


from app_configuration import AppConfiguration
from datasets.testpalm_dataset import TestpalmDataset
from storages.postgres_storage import PostgresStorage
from testpalm_api_client.client import TestPalmClient


def main():
    config = AppConfiguration()

    table_name = config.testpalm_project_id.replace('-', '_')

    postgres_storage = PostgresStorage(
        dbname=config.postgres_dbname,
        user=config.postgres_user,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
        migrations_path=pathlib.Path('schema/postgres_schema/testpalm'),
        testpalm_project_id=table_name,
    )

    testpalm_client = TestPalmClient(oauth_token=config.testpalm_token)
    definitions = testpalm_client.get_definitions(config.testpalm_project_id)

    testcases = testpalm_client.get_testcases(config.testpalm_project_id)

    tests_builds_dataset = TestpalmDataset(
        [postgres_storage], definitions=definitions,
    )
    tests_builds_dataset.aggregate(testcases)
    tests_builds_dataset.store(table=table_name)


if __name__ == '__main__':
    main()
