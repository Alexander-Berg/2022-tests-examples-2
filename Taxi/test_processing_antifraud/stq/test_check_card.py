import json

import pytest

from taxi.util import performance

from processing_antifraud import const
from processing_antifraud.internal import checkcard
from processing_antifraud.internal import models
from processing_antifraud.models import antifraud_proc
from processing_antifraud.models import events
from processing_antifraud.stq import handle_events
from test_processing_antifraud.stq import common


@pytest.mark.parametrize(
    'regions_checked, check_card_finished',
    [(['225'], True), ([], False), (['123'], False)],
)
@common.mark_check_card_settings_experiment()
async def test_need_check_card(
        stq3_context,
        mockserver,
        territories_mock,
        mock_cardstorage_service,
        regions_checked,
        check_card_finished,
):
    @mockserver.json_handler('/user_api-api/user_phones/get_antifraud_doc')
    def _mock_get_antifraud_doc(request, log_extra=None):
        return {'antifraud': {'group': 1}}

    mock_cardstorage_service.cards = [
        mock_cardstorage_service.mock_card(regions_checked=regions_checked),
    ]

    app = stq3_context
    tse = performance.TimeStorage('processing_antifraud')
    app.ts = tse  # type: ignore

    event = events.Events(
        {
            'event_name': const.EVENT_NAME_ORDER_CREATED,
            'processing_index': 1,
            'antifraud_index': 0,
        },
    )

    afd_doc = await antifraud_proc.AntifraudProc.find_one_by_id(
        app.mongo, 'order_id',
    )
    context = models.Context(afd_doc)

    await checkcard.start_check_card(app, event, context)

    afd_doc = await antifraud_proc.AntifraudProc.find_one_by_id(
        app.mongo, 'order_id',
    )

    if check_card_finished:
        assert afd_doc.check_card_is_finished is True
    else:
        assert afd_doc.check_card_is_finished is None


@pytest.mark.config(BILLING_ANTIFRAUD_ENABLED=True)
@pytest.mark.parametrize(
    'overdraft',
    [
        pytest.param(True, marks=common.mark_check_card_settings_experiment()),
        pytest.param(
            False,
            marks=common.mark_check_card_settings_experiment(zone='spb'),
        ),
        pytest.param(
            False,
            marks=common.mark_check_card_settings_experiment(enabled=False),
        ),
    ],
)
async def test_skip_checkcard(
        stq3_context, web_app_client, mockserver, simple_secdist, overdraft,
):
    @mockserver.json_handler('/user_api-api/user_phones/get_antifraud_doc')
    async def _mock_get_antifraud_doc(*args, **kwargs):
        return {'antifraud': {'version': 1, 'group': 1}}

    order_id = '675b9c43fb7a13138a5d61a653d8fecf'
    app = stq3_context

    data = {
        'order_id': order_id,
        'payment_method_id': 'card-x988b7513b1b4235fb392377a',
        'nearest_zone': 'moscow',
        'user_uid': '123456',
        'payment_type': 'card',
        'source': None,
        'last_known_ip': '::ffff:94.25.170.207',
        'processing_index': 0,
        'user_phone_id': '58247911c0d947f1eef0b1bb',
        'destination_types': [],
        'client_application': 'yango_android',
        'client_version': '3.3.3',
        'source_type': 'other',
        'overdraft': overdraft,
    }

    response = await web_app_client.post(
        '/event/processing/order_created', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(app, order_id)

    doc = await antifraud_proc.AntifraudProc.find_one_by_id(
        app.mongo, order_id,
    )
    result = doc.to_dict(use_default=False)
    assert result['check_card_is_finished'] is True
