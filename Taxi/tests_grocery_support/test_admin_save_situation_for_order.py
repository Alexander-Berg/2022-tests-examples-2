import copy

import pytest

from . import common
from . import models


@pytest.mark.now(models.NOW)
async def test_save_to_db(taxi_grocery_support, pgsql, now):
    situation_maas_id = 15

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation = common.create_situation_v2(pgsql, situation_maas_id)

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}

    # Check that suffixes are correctly cut
    products_info = copy.deepcopy(situation.product_infos)

    request_json = {
        'order_id': situation.order_id,
        'situation': {
            'situation_id': situation.maas_id,
            'comment': situation.comment,
            'source': situation.source,
            'has_photo': situation.has_photo,
            'product_infos': products_info,
            'situation_code': situation.situation_code,
        },
    }

    response = await taxi_grocery_support.post(
        '/v2/api/compensation/save-situations-for-order',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    situation.compare_with_db()
