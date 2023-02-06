import contextlib
import datetime

import pytest

from fleet_rent.components import driver_notificator
from fleet_rent.entities import driver_communications_sync
from fleet_rent.generated.web import web_context as context_module


@pytest.mark.config(
    FLEET_RENT_DRIVER_NOTIFICATIONS_V2={
        '__default__': {'timeout': '10d'},
        'new_affiliation': {'timeout': '1h'},
    },
)
async def test_new_affiliation(
        web_context: context_module.Context,
        park_stub_factory,
        park_billing_data_stub_factory,
        aff_stub_factory,
        patch,
):
    @patch(
        'fleet_rent.services.driver_notifications.'
        'DriverNotificationsService.new_affiliation',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.pg_access.driver_communications_sync.'
        'DriverCommunicationsSyncAccessor.new_affiliation_get_for_send',
    )
    @contextlib.asynccontextmanager
    async def _get(*args, **kwargs):
        yield driver_communications_sync.AffiliationNotificationLogEntry(
            notified_at_tz=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            affiliation_id='affiliation_id',
        )

    aff = aff_stub_factory()
    park_info = park_stub_factory()
    park_billing_data = park_billing_data_stub_factory()

    @patch('datetime.datetime.now')
    def _now1(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 0, 30, tzinfo=datetime.timezone.utc,
        )

    with pytest.raises(driver_notificator.AbortedByTimeout) as err:
        await web_context.rent_components.driver_notificator.new_affiliation(
            aff, park_info, park_billing_data,
        )
    assert err.value.time_left == datetime.timedelta(minutes=30)

    @patch('datetime.datetime.now')
    def _now2(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc,
        )

    await web_context.rent_components.driver_notificator.new_affiliation(
        aff, park_info, park_billing_data,
    )


@pytest.mark.config(
    FLEET_RENT_DRIVER_NOTIFICATIONS_V2={
        '__default__': {'timeout': '10d'},
        'new_rent': {'timeout': '1h'},
    },
)
async def test_new_rent(
        web_context: context_module.Context,
        park_stub_factory,
        aff_stub_factory,
        rent_stub_factory,
        patch,
):
    @patch(
        'fleet_rent.services.driver_notifications.'
        'DriverNotificationsService.new_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.pg_access.driver_communications_sync.'
        'DriverCommunicationsSyncAccessor.new_rent_get_for_send',
    )
    @contextlib.asynccontextmanager
    async def _get(*args, **kwargs):
        yield driver_communications_sync.RentNotificationLogEntry(
            notified_at_tz=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            rent_id='record_id',
        )

    aff = aff_stub_factory()
    park_info = park_stub_factory()
    rent = rent_stub_factory()

    @patch('datetime.datetime.now')
    def _now1(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 0, 30, tzinfo=datetime.timezone.utc,
        )

    with pytest.raises(driver_notificator.AbortedByTimeout) as err:
        await web_context.rent_components.driver_notificator.new_rent(
            aff, park_info, rent,
        )
    assert err.value.time_left == datetime.timedelta(minutes=30)

    @patch('datetime.datetime.now')
    def _now2(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc,
        )

    await web_context.rent_components.driver_notificator.new_rent(
        aff, park_info, rent,
    )


@pytest.mark.config(
    FLEET_RENT_DRIVER_NOTIFICATIONS_V2={
        '__default__': {'timeout': '10d'},
        'park_rent_termination': {'timeout': '1h'},
    },
)
async def test_terminated_rent(
        web_context: context_module.Context,
        park_stub_factory,
        aff_stub_factory,
        rent_stub_factory,
        patch,
):
    @patch(
        'fleet_rent.services.driver_notifications.'
        'DriverNotificationsService.terminated_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.pg_access.driver_communications_sync.'
        'DriverCommunicationsSyncAccessor.terminated_rent_get_for_send',
    )
    @contextlib.asynccontextmanager
    async def _get(*args, **kwargs):
        yield driver_communications_sync.RentNotificationLogEntry(
            notified_at_tz=datetime.datetime(
                2020, 1, 1, tzinfo=datetime.timezone.utc,
            ),
            rent_id='record_id',
        )

    aff = aff_stub_factory()
    park_info = park_stub_factory()
    rent = rent_stub_factory()

    @patch('datetime.datetime.now')
    def _now1(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 0, 30, tzinfo=datetime.timezone.utc,
        )

    with pytest.raises(driver_notificator.AbortedByTimeout) as err:
        await web_context.rent_components.driver_notificator.terminated_rent(
            aff, park_info, rent,
        )
    assert err.value.time_left == datetime.timedelta(minutes=30)

    @patch('datetime.datetime.now')
    def _now2(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc,
        )

    await web_context.rent_components.driver_notificator.terminated_rent(
        aff, park_info, rent,
    )
