import datetime

from testsuite.utils import http

from fleet_rent.entities import park_notification as pn
from fleet_rent.generated.web import web_context as context_module


async def test_park_notifications_service(
        web_context: context_module.Context, mock_fleet_notifications,
):
    @mock_fleet_notifications('/v1/notifications/create')
    async def _retrieve(request: http.Request):
        assert request.json == {
            'request_id': 'rent_rent_id_terminated',
            'payload': {
                'title': 'Отказ от списания',
                'text': 'Водитель отказался от списания №1',
                'entity': {
                    'type': 'fleet-rent/termination',
                    'id': 'rent_id',
                    'url': '/rent_id/park_id',
                },
            },
            'destinations': [{'park_id': 'park_id'}],
            'expiry_date': '2020-01-01T15:00:00+03:00',
        }
        return {}

    await web_context.external_access.park_notifications.send_single(
        park_id='park_id',
        notification=pn.Notification(
            idempotency_token='rent_rent_id_terminated',
            body=pn.Notification.Body(
                request_id='rent_rent_id_terminated',
                expiry_date=datetime.datetime(
                    2020, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                payload=pn.Notification.Body.Payload(
                    title='Отказ от списания',
                    text='Водитель отказался от списания №1',
                    entity=pn.Notification.Body.Payload.Entity(
                        type='fleet-rent/termination',
                        id='rent_id',
                        url='/rent_id/park_id',
                    ),
                ),
            ),
        ),
    )
