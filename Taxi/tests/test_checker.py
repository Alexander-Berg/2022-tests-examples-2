import pytest
from yt import wrapper as ytw

from context.settings import settings, init_settings
from core.connection import create_postgresql_connection
from tests.helpers import with_tmp_gp_table, prepare_yt_table


@pytest.mark.slow
def test_assert_column_list():
    settings._settings = None
    extra_test_settings = {
        'SQS': {
            'ACCESS_KEY': 'mock',
            'SESSION_TOKEN': 'mock',
            'ENDPOINT': 'mock',
        },
    }
    init_settings(extra_test_settings)

    from core.task_builder import Context, YtToGpTaskBuilder, YtToGpTask

    yt_client = ytw.YtClient(
        proxy=settings('YT.PROXY'),
        token=settings('tests.YT_TOKEN'),
        config={'backend': 'rpc'},
    )

    yt_table = prepare_yt_table(yt_client, 1000, False)

    gp_user = settings('tests.GP_TEST_SUIT_USER', default=None) or settings('tests.GP_CLIENT_USER')
    gp_password = settings('tests.GP_TEST_SUIT_PASSWORD', default=None) or settings('tests.GP_CLIENT_PASSWORD')

    with create_postgresql_connection(
        host=settings('tests.GP_HOST'),
        port=settings('tests.GP_PORT'),
        database=settings('GP.DATABASE'),
        user=gp_user,
        password=gp_password,
    ) as gp_conn:
        with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
            task = YtToGpTask(
                gp_table=tmp_table,
                yt_table_path=yt_table,
                is_chunk_table=False,
                column_list=['col1', 'col2'],
                yt_token=settings('tests.YT_TOKEN'),
                gp_user=gp_user,
                gp_password=gp_password,
                chunk_size=100,
                gp_table_truncate=True,
            )

            context = Context(
                yt_proxy=settings('YT.PROXY'),
                yt_token=settings('tests.YT_TOKEN'),
                gp_host=settings('tests.GP_HOST'),
                gp_port=settings('tests.GP_PORT'),
                gp_database=settings('GP.DATABASE'),
                gp_transfer_user=gp_user,
                gp_transfer_password=gp_password,
                gp_schema_limits={},
                gp_extra_options={}
            )

            builder = YtToGpTaskBuilder()

            task = builder.build(task, context)

            assert task
