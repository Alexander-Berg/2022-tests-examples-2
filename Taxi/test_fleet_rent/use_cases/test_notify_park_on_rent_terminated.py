import datetime
import typing

import pytest

from fleet_rent.entities import park
from fleet_rent.entities import park_notification as pn
from fleet_rent.entities import park_user
from fleet_rent.generated.cron import cron_context as context

_SUBJECT_TEMPLATE = (
    '[Периодические списания] - {park_name}, {park_city}: '
    'Списание {rent_number} прекращено водителем, {driver_full_name}'
)
_BODY_TEMPLATE = (
    'Парк: {park_name}, {park_city}. '
    'Списание {rent_number}, {rent_opteum_url} , '
    'прекращено водителем {driver_full_name} в {rent_termination_time}.'
)


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'park_rent_terminated_notification_title': {'ru': 'Отказ от списания'},
        'park_rent_terminated_notification_text': {
            'ru': 'Водитель отказался от списания №{rent_number}',
        },
        'park_rent_terminated_email_subject': {
            'ru': _SUBJECT_TEMPLATE.strip(),
        },
        'park_rent_terminated_email_body': {'ru': _BODY_TEMPLATE.strip()},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'ПереводМосква'}},
)
@pytest.mark.config(
    FLEET_RENT_PARK_NOTIFICATIONS={
        'rent_url_template': '/{rent_id}/{park_id}/{serial_id}',
    },
)
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.now('2020-01-01 12:00:00')
async def test_notify_one(
        cron_context: context.Context,
        patch,
        mock_load_park_info,
        mock_load_driver_info,
        mock_load_park_branding,
        mock_find_park_owner,
):
    @patch('fleet_rent.services.park_mailing.ParkMailingService.notify')
    async def _mail(
            idempotence_token: str,
            text_subject: str,
            text_body: str,
            park_branding: park.Branding,
            park_user_info: park_user.ParkUser,
            locales: typing.List[str],
    ):
        assert text_subject == (
            '[Периодические списания] - ИмяПарка, ПереводМосква: '
            'Списание 1 прекращено водителем, Водителев Водитель Водителевич'
        )
        assert text_body == (
            'Парк: ИмяПарка, ПереводМосква. '
            'Списание 1, https://driver.yandex/rent_id/park_id/1 , '
            'прекращено водителем Водителев Водитель Водителевич '
            'в 02.01.20, 3:00.'
        )

    @patch(
        'fleet_rent.services.park_notifications.'
        'ParkNotificationsService.send_single',
    )
    async def _push(park_id: str, notification: pn.Notification):
        assert park_id == 'park_id'
        assert notification == pn.Notification(
            idempotency_token='rent_rent_id_terminated',
            body=pn.Notification.Body(
                request_id='rent_rent_id_terminated',
                expiry_date=datetime.datetime(
                    2020, 1, 8, 12, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                payload=pn.Notification.Body.Payload(
                    title='Отказ от списания',
                    text='Водитель отказался от списания №1',
                    entity=pn.Notification.Body.Payload.Entity(
                        type='fleet-rent/termination',
                        id='rent_id',
                        url='/rent_id/park_id/1',
                    ),
                ),
            ),
        )

    use_case = cron_context.use_cases.notify_park_on_rent_terminated
    await use_case.notify_one('rent_id')


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_notify_all_stuck(cron_context: context.Context, patch):
    processed = []

    synchronizer_access = cron_context.pg_access.park_communications_sync

    @patch(
        'fleet_rent.use_cases.notify_park_on_rent_terminated.'
        'NotifyOnRentTerminated.notify_one',
    )
    async def _notify_one(rent_id: str):
        await synchronizer_access.rent_terminated.sync_process(
            rent_id=rent_id, process=lambda: process(rent_id),
        )

    async def process(rent_id: str):
        nonlocal processed
        processed.append(rent_id)

    use_case = cron_context.use_cases.notify_park_on_rent_terminated
    await use_case.notify_all_stuck()

    assert processed == ['rent_id']
