import logging

import yt.wrapper as ytw

from connection import yt as yt_connection
from dmp_suite import decorators

logger = logging.getLogger(__name__)


def get_yt_client(cluster: str):
    return ytw.YtClient(
        proxy=yt_connection.get_yt_cluster_proxy(cluster),
        token=yt_connection.get_yt_cluster_token(),
        config={
            "pickling": {
                "module_filter": yt_connection.module_filter,
            },
            "read_parallel": {
                "max_thread_count": 32,
                "data_size_per_thread": 32 * 1024 * 1024
            }
        }
    )


@decorators.try_except(2)
def unmount_table(*, yt_client: ytw.YtClient, table_path: str):
    yt_client.unmount_table(table_path, sync=True)


@decorators.try_except(2)
def mount_table(*, yt_client: ytw.YtClient, table_path: str):
    yt_client.mount_table(table_path, sync=True)


def change_enable_dynamic_store_read(
        *,
        yt_client: ytw.YtClient,
        root_path: str,
        enable: bool,
):
    tables = yt_client.search(
        root=root_path,
        node_type=['table'],
        attributes=['dynamic', 'enable_dynamic_store_read', 'tablet_state'],
    )
    for table in tables:
        attrs = table.attributes
        if not attrs.get('dynamic', False):
            continue

        current_enable_dynamic_store_read = attrs['enable_dynamic_store_read']

        if current_enable_dynamic_store_read == enable:
            logger.info(
                (
                    'Value of enable_dynamic_store_read attribute of %s '
                    'is already %s'
                ),
                table,
                enable,
            )
            continue

        is_mounted = attrs.get('tablet_state') == 'mounted'

        try:
            if is_mounted:
                logger.info('Unmounting %s', table)
                unmount_table(yt_client=yt_client, table_path=table)

            logger.info(
                'Setting enable_dynamic_store_read of table %s to %s',
                table,
                enable,
            )
            yt_client.set_attribute(table, 'enable_dynamic_store_read', enable)

            if is_mounted:
                logger.info('Mounting %s', table)
                mount_table(yt_client=yt_client, table_path=table)

            logger.info(
                'Table\'s %s enable_dynamic_store_read has been changed to %s',
                table,
                enable
            )
        except Exception:
            logger.error(
                'Failed to change enable_dynamic_store_read of table %s',
                table,
            )
            raise


if __name__ == '__main__':
    for cluster in ['hahn', 'arnold']:
        logger.info('Processing cluster %s', cluster)
        ytc = get_yt_client(cluster)
        change_enable_dynamic_store_read(
            yt_client=ytc,
            root_path='//home/market/production/mstat/dwh/ods/abo/item_return',
            enable=True,
        )
        change_enable_dynamic_store_read(
            yt_client=ytc,
            root_path='//home/market/production/mstat/dwh/ods/abo/item_return_reason',
            enable=True,
        )
