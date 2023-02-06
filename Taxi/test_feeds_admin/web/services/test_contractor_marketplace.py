import copy
import json

import pytest

from feeds_admin import models
from feeds_admin.services import contractor_marketplace
from test_feeds_admin import common
from test_feeds_admin import const


SERVICE = 'contractor-marketplace'
PAYLOAD_WITH_PRICE = 'payload_with_price.json'
PAYLOAD_WITHOUT_PRICE = 'payload_without_price.json'

MANUAL_RECIPIENTS = [
    {'type': 'contractor', 'recipients_ids': ['dbid_uuid']},
    {'type': 'experiment', 'recipients_ids': ['experiment']},
]
SCHEDULE = {
    'start_at': '2000-01-01T00:00:00+0300',
    'finish_at': '3000-01-01T00:00:00+0300',
}


@pytest.mark.parametrize(
    'payload_file, self_ok',
    [(PAYLOAD_WITH_PRICE, False), (PAYLOAD_WITHOUT_PRICE, True)],
)
@pytest.mark.parametrize('manual_recipients', MANUAL_RECIPIENTS)
async def test_lifecycle(
        web_app_client, patch, load, payload_file, self_ok, manual_recipients,
):
    payload = json.loads(load(payload_file))
    recipients = manual_recipients
    schedule = copy.deepcopy(SCHEDULE)

    # Create
    check_response = await web_app_client.post(
        '/v1/contractor-marketplace/check-feed',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )
    assert check_response.status == 200
    check_body = (await check_response.json())['data']
    assert check_body['self_ok'] == self_ok
    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json=check_body,
    )
    assert response.status == 200
    feed_id = (await response.json())['id']

    # Update
    payload['title'] = 'updated title'
    recipients['recipients_ids'] = ['dbid1_uuid1', 'dbid2_uuid2']
    schedule['start_at'] = '2111-01-01T00:00:00+0300'

    check_response = await web_app_client.post(
        '/v1/contractor-marketplace/check-feed',
        json={
            'id': feed_id,
            'service': SERVICE,
            'name': 'ContractorMarketPlaceUpdated',
            'payload': payload,
            'schedule': schedule,
        },
    )
    assert check_response.status == 200
    check_body = (await check_response.json())['data']
    assert check_body['self_ok'] == self_ok

    response = await web_app_client.post(
        '/v1/contractor-marketplace/update', json=check_body,
    )
    assert response.status == 200

    # Get
    response = await web_app_client.get(
        '/v1/contractor-marketplace/get',
        params={'service': SERVICE, 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': feed_id,
        'service': SERVICE,
        'name': 'ContractorMarketPlaceUpdated',
        'status': 'created',
        'payload': payload,
        'author': 'adomogashev',
        'schedule': schedule,
        'ticket': '',
    }

    # Purge
    check_response = await web_app_client.post(
        '/v1/contractor-marketplace/check-feed',
        json={'id': feed_id, 'service': SERVICE},
    )
    assert check_response.status == 200
    check_body = (await check_response.json())['data']
    assert check_body['self_ok'] == self_ok

    response = await web_app_client.post(
        '/v1/contractor-marketplace/purge', json=check_body,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/contractor-marketplace/get',
        params={'service': SERVICE, 'id': feed_id},
    )
    assert response.status == 200
    assert (await response.json())['status'] == 'finished'


@pytest.mark.pgsql('feeds_admin', files=['default.sql'])
async def test_list(web_app_client, load):
    response = await web_app_client.post(
        '/v1/contractor-marketplace/list',
        json={
            'service': SERVICE,
            'status': 'created',
            'category': 'auto_parts',
            'partner_name': 'пАРт',
            'author': 'adomogashev',
            'slider': True,
            'place_id': {'lower_bound': 50, 'upper_bound': 51.2},
            'payload': 'to_pa',
            'name': 'MarketPlace',
            'recipients_tag': 'tag2',
            'order_by': 'updated',
        },
    )

    assert response.status == 200
    body = await response.json()
    assert body['items'][0].pop('created')
    assert body['items'][0].pop('updated')
    assert body == {
        'total': 1,
        'offset': 0,
        'limit': 25,
        'items': [
            {
                'id': const.UUID_1,
                'service': SERVICE,
                'status': 'created',
                'author': 'adomogashev',
                'slider': True,
                'place_id': 50.2,
                'name': 'ContractorMarketplace',
                'categories': ['auto_parts'],
                'partner_name': 'Партнёр',
                'start_at': '2000-01-01T00:00:00+0300',
                'finish_at': '3000-01-01T00:00:00+0300',
            },
        ],
    }


async def test_service(web_app_client, load):
    publication = common.create_fake_publication('contractor-marketplace')
    publication.feed.payload = json.loads(load(PAYLOAD_WITH_PRICE))

    recipients_group = publication.recipients_groups[0]
    recipients_group.group_settings['type'] = 'contractor'

    service = contractor_marketplace.ContractorMarketplaceService(
        'contractor-marketplace',
    )

    channels = await service.make_channels(
        publication,
        recipients_group,
        recipients=[
            models.recipients.Recipient(recipient_id='dbid_uuid1'),
            models.recipients.Recipient(recipient_id='dbid_uuid2'),
        ],
    )
    assert channels == ['contractor:dbid_uuid1', 'contractor:dbid_uuid2']

    payload = await service.make_payload(publication)
    assert payload == {
        **publication.feed.payload,
        'feeds_admin_id': const.UUID_1,
    }

    tags = await service.make_tags(publication)
    assert tags == ['auto_parts']

    geo = ['51.5,52.125,"ufa,pushkin,100"', '32.25,32.25,']
    geo_positions = (
        contractor_marketplace._parse_geo_positions(  # pylint: disable=W0212
            geo=geo,
        )
    )
    assert geo_positions == [
        models.geo.Position(
            point=models.geo.Point(longitude=51.5, latitude=52.125),
            meta={'info': 'ufa,pushkin,100'},
        ),
        models.geo.Position(
            point=models.geo.Point(longitude=32.25, latitude=32.25),
        ),
    ]


@pytest.mark.config(CONTRACTOR_MERCH_SUPPORTED_BARCODES={})
async def test_invalide_barcode_type(web_app_client, patch, load):
    payload = json.loads(load(PAYLOAD_WITH_PRICE))
    recipients = copy.deepcopy(MANUAL_RECIPIENTS[0])
    schedule = copy.deepcopy(SCHEDULE)

    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )
    assert response.status == 400


# definitions
# barcode_params -> bp
# is_send_enabled -> ise
# send_number_along_with_barcode -> sna
# chat_instructions_tanker_key_with_promocode_number -> wp
# chat_instructions_tanker_key_without_promocode_number -> wop
@pytest.mark.parametrize(
    'payload_file',
    [
        'invalid_keys/payload_bp_ise_sna_wop.json',
        'invalid_keys/payload_bp_ise_not_sna_wp.json',
        'invalid_keys/payload_bp_ise_no_sna_wp.json',
        'invalid_keys/payload_bp_not_ise_not_sna_wp.json',
        'invalid_keys/payload_bp_not_ise_sna_wop.json',
        'invalid_keys/payload_no_bp_wop.json',
    ],
)
async def test_invalid_custom_keys(web_app_client, patch, load, payload_file):
    payload = json.loads(load(payload_file))
    recipients = copy.deepcopy(MANUAL_RECIPIENTS[0])
    schedule = copy.deepcopy(SCHEDULE)

    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )

    assert response.status == 400


@pytest.mark.parametrize(
    'payload_file',
    [
        'valid_keys/payload_bp_pp_not_sna_wop.json',
        'valid_keys/payload_bp_ise_sna_wp.json',
        'valid_keys/payload_bp_ise_sna_no_wp.json',
        'valid_keys/payload_bp_ise_not_sna_wop.json',
        'valid_keys/payload_no_bp_wp.json',
    ],
)
async def test_valid_custom_keys(web_app_client, patch, load, payload_file):
    payload = json.loads(load(payload_file))
    recipients = copy.deepcopy(MANUAL_RECIPIENTS[0])
    schedule = copy.deepcopy(SCHEDULE)

    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )

    assert response.status == 200


@pytest.mark.parametrize(
    'payload_file, status',
    [
        pytest.param('few_promocodes/payload_few_promocodes.json', 200),
        pytest.param(
            'few_promocodes/payload_few_promocodes_with_barcode.json', 400,
        ),
    ],
)
async def test_offer_with_few_promocodes(
        web_app_client, patch, load, payload_file, status,
):
    payload = json.loads(load(payload_file))
    recipients = copy.deepcopy(MANUAL_RECIPIENTS[0])
    schedule = copy.deepcopy(SCHEDULE)

    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )

    assert response.status == status


@pytest.mark.parametrize(
    'payload_file, expected_code',
    [
        ('ok_with_payment_link.json', 200),
        ('not_ok_without_payment_link.json', 400),
    ],
)
async def test_actions(web_app_client, load_json, payload_file, expected_code):
    payload = load_json(payload_file)
    recipients = copy.deepcopy(MANUAL_RECIPIENTS[0])
    schedule = copy.deepcopy(SCHEDULE)

    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'adomogashev'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )

    assert response.status == expected_code
    if expected_code != 200:
        assert await response.json() == {
            'code': '400',
            'message': 'actions should be provided',
        }


@pytest.mark.pgsql('feeds_admin', files=['feeds.sql'])
async def test_get_geo(web_app_client):
    feed_id = const.UUID_1
    get_response = await web_app_client.get(
        '/v1/contractor-marketplace/get',
        params={'service': SERVICE, 'id': feed_id},
    )
    get_result = await get_response.json()
    assert get_result['geo'] == [
        '1.123,2.123,3',
        '123.321,50.321,',
        '50.1,50.2,",commas,text,"',
    ]


async def test_create_geo(web_app_client, load_json):
    geo = ['12.5,12.125,a', '321123.25,aba', '1.0,2.125,"a,b,a,c,a,b,a"']
    response = await web_app_client.post(
        '/v1/contractor-marketplace/create',
        headers={'X-Yandex-Login': 'who'},
        json={
            'service': SERVICE,
            'name': 'ContractorMarketPlace2',
            'payload': load_json('payload.json'),
            'geo': geo,
            'recipients': {'type': 'tag', 'recipients_ids': ['tag3', 'tag4']},
            'schedule': {
                'start_at': '2000-01-01T00:00:00+03:00',
                'finish_at': '3000-01-01T00:00:00+03:00',
            },
        },
    )

    feed_id = (await response.json())['id']
    get_response = await web_app_client.get(
        '/v1/contractor-marketplace/get',
        params={'service': SERVICE, 'id': feed_id},
    )
    get_result = await get_response.json()
    assert get_result['geo'] == geo


@pytest.mark.pgsql('feeds_admin', files=['feeds.sql'])
async def test_update_geo(web_app_client, load_json):
    geo = ['12.5,12.125,a', '321123.25,aba', '1.0,2.125,"a,b,a,c,a,b,a"']
    await web_app_client.post(
        '/v1/contractor-marketplace/update',
        json={
            'id': const.UUID_1,
            'service': SERVICE,
            'name': 'ContractorMarketPlace2',
            'payload': load_json('payload.json'),
            'geo': geo,
            'recipients': {'type': 'tag', 'recipients_ids': ['tag3', 'tag4']},
            'schedule': {
                'start_at': '2000-01-01T00:00:00+03:00',
                'finish_at': '3000-01-01T00:00:00+03:00',
            },
        },
    )

    get_response = await web_app_client.get(
        '/v1/contractor-marketplace/get',
        params={'service': SERVICE, 'id': const.UUID_1},
    )
    get_result = await get_response.json()
    assert get_result['geo'] == geo


@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        SERVICE: {
            'max_channels_for_immediate_publish': 3,
            'feed_id_source': 'feeds-admin',
        },
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds.sql'])
async def test_publish_geo(web_app_client, stq_runner, mockserver, load_json):
    @mockserver.json_handler('feeds/v1/batch/create')
    async def _create(_):
        return {
            'items': [{'service': SERVICE, 'feed_ids': {}, 'filtered': []}],
        }

    @mockserver.json_handler('feeds/v1/update')
    async def _update(_):
        return {}

    @mockserver.json_handler('feeds/v1/upload_geo')
    async def upload_geo(request):
        assert request.json['points'] == [
            {
                'point': {
                    'longitude': pytest.approx(1.8123),
                    'latitude': pytest.approx(2.123),
                },
                'meta': {'info': '3'},
            },
            {
                'point': {
                    'longitude': pytest.approx(123.25),
                    'latitude': pytest.approx(50.125),
                },
            },
            {
                'point': {
                    'longitude': pytest.approx(50.111),
                    'latitude': pytest.approx(50.222),
                },
                'meta': {'info': ',commas,text,'},
            },
        ]
        return {}

    await stq_runner.feeds_admin_send.call(
        args=(const.UUID_1,), kwargs={'run_id': 50},
    )
    assert upload_geo.times_called == 1
