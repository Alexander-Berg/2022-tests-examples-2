import re
import typing

import pytest

from tests_eats_restapp_marketing import sql

SCOPE_NAME = 'eda'


def make_media_url(media_id: str):
    result = {
        'media_id': media_id,
        'media_type': 'foo',
        'media_url': 'url_%s' % media_id,
        'tags': ['foo_tag1', 'foo_tag2'],
    }
    return result


def get_distinct_media_ids(status: str, pgsql) -> typing.List[str]:
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT DISTINCT image '
        'FROM eats_restapp_marketing.banners '
        'WHERE status = \'%s\' ' % status,
        'ORDER BY id;',
    )

    result = [row[0] for row in cursor.fetchall()]
    return result


def get_banners_by_status(status: str, pgsql) -> typing.List[int]:
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT id '
        'FROM eats_restapp_marketing.banners '
        'WHERE status = \'%s\' ' % status,
        'ORDER BY id;',
    )

    result = [row[0] for row in cursor.fetchall()]
    return result


def init_table(eats_restapp_marketing_db):
    for x in [1, 2, 3]:
        sql.insert_campaign(eats_restapp_marketing_db, sql.Campaign(id=x))

        sql.insert_banner(
            eats_restapp_marketing_db,
            sql.Banner(
                id=x,
                place_id=x,
                inner_campaign_id=x,
                image='media_id%d' % x,
                status=sql.BannerStatus.UPLOADED,
            ),
        )
    for x in [4, 5, 6]:
        sql.insert_campaign(eats_restapp_marketing_db, sql.Campaign(id=x))

        sql.insert_banner(
            eats_restapp_marketing_db,
            sql.Banner(
                id=x,
                place_id=x,
                inner_campaign_id=x,
                image='same_media_id',
                status=sql.BannerStatus.UPLOADED,
            ),
        )
    for x in [7, 8, 9]:
        sql.insert_campaign(eats_restapp_marketing_db, sql.Campaign(id=x))

        sql.insert_banner(
            eats_restapp_marketing_db,
            sql.Banner(
                id=x,
                place_id=x,
                inner_campaign_id=x,
                image='foo%d' % x,
                status=sql.BannerStatus.ACTIVE,
            ),
        )


CONFIG_DISABLED = {
    'enabled': False,
    'task_period_seconds': 123,
    'queue': 'foo_name',
}


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_SET_BANNERS_FOR_MODERATION=CONFIG_DISABLED,
)
async def test_set_banners_for_moderation_disabled(
        testpoint,
        taxi_eats_restapp_marketing,
        pgsql,
        eats_restapp_marketing_db,
):
    """
    Проверка что конфиг выключает периодику
    """
    init_table(eats_restapp_marketing_db)
    expected_ids = get_banners_by_status('uploaded', pgsql)

    @testpoint('set-banners-for-moderation-finished')
    async def handle_finished(arg):
        return

    async with taxi_eats_restapp_marketing.spawn_task(
            'set-banners-for-moderation',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
    assert expected_ids == get_banners_by_status('uploaded', pgsql)


CONFIG_ENABLED = {
    'enabled': True,
    'task_period_seconds': 123,
    'queue': 'foo_name',
}


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_SET_BANNERS_FOR_MODERATION=CONFIG_ENABLED,
)
@pytest.mark.parametrize(
    'failed, banner_status',
    [
        pytest.param(False, 'in_moderation', id='Succesful responses'),
        pytest.param(True, 'pre_moderation', id='Failed responses'),
    ],
)
async def test_set_banners_for_moderation(
        testpoint,
        taxi_eats_restapp_marketing,
        pgsql,
        mockserver,
        failed,
        banner_status,
        eats_restapp_marketing_db,
):
    """
    Проверка установки статусов баннеров при успешном/неуспешном запросе
    """
    init_table(eats_restapp_marketing_db)
    expected_ids = get_banners_by_status('uploaded', pgsql)
    uniq_media_ids = get_distinct_media_ids('uploaded', pgsql)

    @mockserver.json_handler('/feeds-admin/v1/media/get-urls')
    async def _handle_get_urls(request):
        if failed:
            return mockserver.make_response(status=500)

        assert request.json['media_ids'] == uniq_media_ids
        return mockserver.make_response(
            status=200,
            json={'urls': [make_media_url(m_ids) for m_ids in uniq_media_ids]},
        )

    @mockserver.json_handler('/eats-moderation/moderation/v1/task')
    async def _handle_moderation_task(request):
        assert request.json['scope'] == SCOPE_NAME
        assert request.json['queue'] == CONFIG_ENABLED['queue']
        context_pattern = re.compile(
            r'{"media_id":"[\d\w]+",\s?'
            r'"data":\[({"id":"\d+",\s?"place_id":"[\d\w]+"},?)+\]}',
        )  # for example {"media_id":"123e",
        # "data":[{"id":"123", "place_id":"url321"},{"id":123, ...},...]}
        payload_pattern = re.compile(
            r'{"photo_url":"[\d\w]+"}',
        )  # for example {"photo_url":"url123"}
        assert context_pattern.fullmatch(request.json['context'])
        assert payload_pattern.fullmatch(request.json['payload'])
        return mockserver.make_response(status=200, json={})

    @testpoint('set-banners-for-moderation-finished')
    async def handle_finished(arg):
        return

    async with taxi_eats_restapp_marketing.spawn_task(
            'set-banners-for-moderation',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert expected_ids == get_banners_by_status(banner_status, pgsql)
    assert _handle_get_urls.times_called > 0
    assert _handle_moderation_task.times_called == 0 if failed else 1
