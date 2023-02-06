import copy

import pytest

from promotions.generated.cron import run_cron


DEFAULT_EXPERIMENT = {
    'name': 'promotions_test_publish',
    'last_modified_at': 123,
    'clauses': [],
}


@pytest.mark.pgsql('promotions', files=['pg_promotions_expired.sql'])
async def test_ok(web_app_client, pgsql, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        resp = copy.deepcopy(DEFAULT_EXPERIMENT)
        resp['clauses'].extend(
            [
                {
                    'title': '+79999999999',
                    'value': {'enabled': True, 'promotions': ['id3']},
                    'predicate': {
                        'type': 'in_set',
                        'init': {
                            'set': ['+79999999999'],
                            'arg_name': 'phone_id',
                            'transform': 'replace_phone_to_phone_id',
                            'phone_type': 'yandex',
                            'set_elem_type': 'string',
                        },
                    },
                },
            ],
        )
        return resp

    await run_cron.main(
        ['promotions.crontasks.unpublish_expired_promotions', '-t', '0'],
    )

    for promotion_id in ['id3_expired', 'eda_expired']:
        response = await web_app_client.get(
            f'admin/promotions/', params={'promotion_id': promotion_id},
        )
        promotion = await response.json()
        assert promotion['status'] == 'stopped'

    response = await web_app_client.get(
        '/admin/showcases/', params={'showcase_id': 'expired_showcase_id'},
    )
    promotion = await response.json()
    assert promotion['status'] == 'stopped'

    response = await web_app_client.get(
        '/admin/promo_on_map/',
        params={'promotion_id': 'expired_promo_on_map_id'},
    )
    promotion = await response.json()
    assert promotion['status'] == 'stopped'
