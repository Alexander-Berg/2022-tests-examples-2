import json

import pytest

from . import utils


# Generated via `tvmknife unittest service -s 2020527 -d 2020527`
PROMOCODES_TICKET = (
    '3:serv:CBAQ__________9_IggIr6l7EK-pew:JDDmKdfGuACYhSKVXG'
    'UFESNoA6lQMeMul8NDJEXxBotkpTNSlWLu8EpC_95SgsHqCxhelXTaJs'
    'ZLD_IsUXf-g3Yr-t79TF1CGXl9-5IwkhVFHT1sXxae-uh_OiWvNK7PoG'
    'GlcZWZDeRPkvCR9zfZ1vx3fAE94Tv1QOlL-u7CAFY'
)
# Generated via `tvmknife unittest service -s 111 -d 2020527`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCvqXs:CVDEtdtqrs0R8h1GQPKNFfkRf0O'
    '2e-0G4tKqOIEcMxRA3WSiAzU51HWeC39gVpxXhNCDrgNjVfdsT5EudT-IJpKXP'
    'fB4IYRXXFClXOdtFcRuB1wP5hXDG-0M8A6THzrN1xgMPmD4wyLNExcCrIY5srk'
    'r9m5EPsC6D5LR-UFZspg'
)
DRAFT_HEADERS = {
    'X-YaTaxi-Draft-Author': 'vdovkin',
    'X-YaTaxi-Draft-Tickets': 'TAXI-1,TAXI-2',
}
HEADERS = {'X-Yandex-Login': 'vdovkin', 'X-Ya-Service-Ticket': MOCK_TICKET}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'internal-service', 'dst': 'driver-promocodes'}],
    TVM_SERVICES={
        'driver-promocodes': 2020527,
        'internal-service': 111,
        'stq-agent': 111,
    },
)
@pytest.mark.tvm2_ticket({2020527: PROMOCODES_TICKET, 111: MOCK_TICKET})
@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_recall.sql'],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'url', ['admin/v1/promocodes/recall', 'internal/v1/promocodes/recall'],
)
@pytest.mark.parametrize(
    'request_recall,response_recall,tags_request,is_good',
    [
        (
            'request_promocode_recall_active.json',
            'response_promocode_recall_active.json',
            'request_tags_promocode_recall_active.json',
            True,
        ),
        (
            'request_promocode_recall_active_2.json',
            'response_promocode_recall_active_2.json',
            'request_tags_promocode_recall_active_2.json',
            True,
        ),
        (
            'request_promocode_recall_published.json',
            'response_promocode_recall_published.json',
            None,
            True,
        ),
        ('request_promocode_recall_unknown.json', None, None, False),
    ],
)
async def test_driver_promocodes_recall_promocode(
        taxi_driver_promocodes,
        stq,
        stq_runner,
        mockserver,
        load_json,
        url,
        request_recall,
        response_recall,
        tags_request,
        is_good,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        if not tags_request:
            assert False
        data = json.loads(request.get_data())
        assert data == load_json(tags_request)
        return {}

    response = await taxi_driver_promocodes.post(
        url, json=load_json(request_recall), headers=HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    if response_recall:
        assert utils.remove_not_testable(
            response.json(),
        ) == utils.remove_not_testable(load_json(response_recall))

    assert stq.driver_promocodes_upload_tags.times_called == bool(tags_request)
    if tags_request:
        await utils.call_tags_task(stq, stq_runner)


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_recall.sql'],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_recall,response_recall,response_list_after,tags_request,is_good',
    [
        (
            'request_series_recall.json',
            'response_series_recall.json',
            'response_series_recall_after.json',
            'request_tags_series_recall.json',
            True,
        ),
        ('request_series_recall_unknown.json', None, None, None, False),
    ],
)
async def test_driver_promocodes_recall_series_admin(
        taxi_driver_promocodes,
        stq,
        stq_runner,
        mockserver,
        load_json,
        request_recall,
        response_recall,
        response_list_after,
        tags_request,
        is_good,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        if not tags_request:
            assert False
        data = json.loads(request.get_data())
        assert data == load_json(tags_request)
        return {}

    response = await taxi_driver_promocodes.post(
        'admin/v1/series/recall/check',
        json=load_json(request_recall),
        headers=DRAFT_HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    response = await taxi_driver_promocodes.post(
        'admin/v1/series/recall',
        json=load_json(request_recall),
        headers=DRAFT_HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    if response_recall:
        assert utils.remove_not_testable(
            response.json(),
        ) == utils.remove_not_testable(load_json(response_recall))

    if response_list_after:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list', params={},
        )
        assert (
            utils.remove_not_testable_promocodes(response.json())
            == utils.remove_not_testable_promocodes(
                load_json(response_list_after),
            )
        )

    assert stq.driver_promocodes_upload_tags.times_called == bool(tags_request)
    if tags_request:
        await utils.call_tags_task(stq, stq_runner)
