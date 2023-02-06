import asyncio
import collections
import datetime
import json

import pytest
import pytz

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_performer_mentorship_plugins import *  # noqa: F403 F401


@pytest.fixture(name='add_depots', autouse=True)
def grocery_depots_add_depot(grocery_depots):
    grocery_depots.add_depot(
        depot_id='FFFF123', legacy_depot_id='123', timezone='Europe/Moscow',
    )


@pytest.fixture
def now_in_msk():
    def _now_in_msk(now=datetime.datetime.now()):
        tz_msk = pytz.timezone('Europe/Moscow')
        now_msk = now.astimezone(tz_msk)
        return now_msk

    return _now_in_msk


def hours_from(distance=0, now=datetime.datetime.now()):
    if distance:
        now = now + datetime.timedelta(hours=distance)
    tz_msk = pytz.timezone('Europe/Moscow')
    now_msk = now.astimezone(tz_msk)
    return now_msk.strftime('%Y-%m-%dT%H:%M')


@pytest.fixture
def collect_common_message_keys(stq):
    async def _collect_common_message_keys(
            items_count, now=datetime.datetime.now(),
    ):
        now = now.replace(tzinfo=None)

        def timediff_if(datetime_str):
            time_point = datetime.datetime.strptime(
                datetime_str[: len('%YYY-%m-%dT%H:%M:%S')],
                '%Y-%m-%dT%H:%M:%S',
            )
            hours = round(
                abs((time_point - now).total_seconds()) / (60.0 * 60.0),
            )
            return (
                int(hours)
                if hours < 24
                else datetime_str[: len('%YYY-%m-%dT%H:%M')]
            )

        messages_by_performer = collections.defaultdict(dict)
        scm = stq.grocery_performer_communications_common_message
        for _i in range(items_count):
            call = await scm.wait_call()
            messages_by_performer[call['kwargs']['performer_id']][
                call['kwargs']['text']['key']
            ] = (
                {
                    arg['name']: (
                        arg['value']['value']
                        if 'date' not in arg['value']['type']
                        else timediff_if(arg['value']['value'])
                    )
                    for arg in call['kwargs']['text']['args']
                }
                if 'args' in call['kwargs']['text']
                else {}
            )
        return dict(messages_by_performer)

    return _collect_common_message_keys


@pytest.fixture(name='published_events')
async def _published_events(testpoint):
    """Wait and return events published to logbroker."""

    @testpoint('logbroker_publish')
    def publish_event(request):
        pass

    class Events:
        async def _wait_next(self):
            request = (await publish_event.wait_call())['request']
            return request['name'], json.loads(request['data'])

        async def _wait(self, alias=None):
            while True:
                event_alias, event = await self._wait_next()
                if alias is None or event_alias == alias:
                    return event_alias, event

        async def wait(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

        async def count(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

        async def collect_by_newbie(self, count):
            # pylint: disable=C4001
            res = {}
            for _i in range(count):
                event = (
                    await self.wait('grocery-performer-mentorship-slot-update')
                )[1]
                res[
                    (
                        f"{event['newbie']['performer_id']} "
                        f"{event['newbie']['shift_id']} "
                        f"{event['action']}"
                    )
                ] = event['mentor']
            return res

    return Events()
