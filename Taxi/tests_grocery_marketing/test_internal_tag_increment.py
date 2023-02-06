import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models


LIMIT_LAST_ORDER_IDS = 3


@pytest.mark.config(
    GROCERY_MARKETING_LIMIT_LAST_ORDER_IDS=LIMIT_LAST_ORDER_IDS,
)
async def test_basic(taxi_grocery_marketing, pgsql):
    yandex_uids = ['yandex_uid_1', 'yandex_uid_2']
    tags = ['tag_1', 'tag_2']
    headers = common.DEFAULT_USER_HEADERS

    def _get_expected_last_order_ids(yandex_uid, tag, last_iteration_id):
        return [
            f'{yandex_uid}-{tag}-{id}'
            for id in range(last_iteration_id, -1, -1)
        ]

    for iteration_id in range(LIMIT_LAST_ORDER_IDS):
        for tag in tags:
            for yandex_uid in yandex_uids:
                order_id = f'{yandex_uid}-{tag}-{iteration_id}'

                tag_stat = models.TagStatistic(
                    pgsql=pgsql,
                    yandex_uid=yandex_uid,
                    tag=tag,
                    insert_in_pg=False,
                )
                if iteration_id > 0:
                    tag_stat.update()
                    assert tag_stat.usage_count == iteration_id
                    assert (
                        tag_stat.last_order_ids
                        == _get_expected_last_order_ids(
                            yandex_uid, tag, iteration_id - 1,
                        )
                    )

                usage_count = await common.inc_stat_value(
                    taxi_grocery_marketing, headers, yandex_uid, tag, order_id,
                )
                assert usage_count == iteration_id + 1

                last_order_ids = _get_expected_last_order_ids(
                    yandex_uid, tag, iteration_id,
                )

                tag_stat.update()
                assert tag_stat.usage_count == iteration_id + 1
                assert tag_stat.last_order_ids == last_order_ids

                # Idempotency check
                usage_count = await common.inc_stat_value(
                    taxi_grocery_marketing, headers, yandex_uid, tag, order_id,
                )

                tag_stat.update()
                assert tag_stat.usage_count == iteration_id + 1
                assert tag_stat.last_order_ids == last_order_ids

                assert usage_count == iteration_id + 1

    for tag in tags:
        for yandex_uid in yandex_uids:
            last_order_ids = _get_expected_last_order_ids(
                yandex_uid, tag, LIMIT_LAST_ORDER_IDS - 1,
            )

            tag_stat = models.TagStatistic.fetch(
                pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
            )

            assert tag_stat.last_order_ids == last_order_ids
            assert tag_stat.usage_count == LIMIT_LAST_ORDER_IDS

            order_id = f'{yandex_uid}-{tag}-{LIMIT_LAST_ORDER_IDS}'

            usage_count = await common.inc_stat_value(
                taxi_grocery_marketing, headers, yandex_uid, tag, order_id,
            )
            assert usage_count == LIMIT_LAST_ORDER_IDS + 1

            tag_stat.update()
            assert tag_stat.usage_count == LIMIT_LAST_ORDER_IDS + 1
            assert len(tag_stat.last_order_ids) == LIMIT_LAST_ORDER_IDS
            assert tag_stat.last_order_ids == [order_id] + last_order_ids[:-1]
