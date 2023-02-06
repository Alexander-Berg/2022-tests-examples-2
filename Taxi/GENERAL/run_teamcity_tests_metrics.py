import pathlib
import typing


from app_configuration import AppConfiguration
from clients.teamcity_client import TeamcityApiClient
from datasets.tests_builds_dataset import TestsBuildsDataset
from storages.postgres_storage import PostgresStorage


def main():
    config = AppConfiguration()

    table_name = config.teamcity_table_name or config.tests_task_id

    postgres_storage = PostgresStorage(
        dbname=config.postgres_dbname,
        user=config.postgres_user,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
        migrations_path=pathlib.Path('schema/postgres_schema/teamcity_builds'),
        teamcity_table_name=table_name,
    )

    tc_client = TeamcityApiClient(config.teamcity_url, config.teamcity_token)

    tests_builds_dataset = TestsBuildsDataset([postgres_storage])
    build_type = config.tests_task_id
    tc_data: typing.List = tc_client.get_all_builds(build_type)

    tests_builds_dataset.aggregate(tc_data)
    tests_builds_dataset.store(table=table_name)


if __name__ == '__main__':
    main()
