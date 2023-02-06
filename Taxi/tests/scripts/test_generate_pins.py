# pylint: disable=too-many-locals
from datetime import timedelta
from random import sample

import pytz
from libstall.util import tzone, now, time2time
from scripts.cron.generate_pins import generate_pins


async def test_generate_pins_ok(tap, dataset, cfg):
    cfg.set('generate_pins.roles', ['admin'])
    cfg.set('generate_pins.timespan', '00:00-06:00')

    good_tzs = list(set(pytz.all_timezones) - {'NZ-CHAT', 'Pacific/Chatham'})
    users = []
    cur_times = []
    tzs = [tz for tz in good_tzs if 0 < now(tzone(tz)).hour < 6]
    tzs = sample(tzs, 5)

    with tap.plan(15, 'все таймзоны хорошие'):
        for tz in tzs:
            # ставим время на секунду раньше, иначе округление все испортит
            cur_times.append(now(tzone(tz)) - timedelta(seconds=1))
            store = await dataset.store(tz=tz)
            user = await dataset.user(store_id=store.store_id)
            if cfg('generate_pins.roles'):
                user.role = cfg('generate_pins.roles')[0]
            user.pin = '0000'
            await user.save()
            users.append(user)

        await generate_pins()

        for i, user in enumerate(users):
            await user.reload()
            new_pin = user.pin
            pin_updated = time2time(user.vars['pin_updated'])
            tap.ok(new_pin, f'{i+1}-й пин загружен')
            tap.ne_ok(new_pin, '0000', f'{new_pin} не равно 0000')
            tap.ok(pin_updated > cur_times[i], 'pin_updated обновился')


async def test_generate_pins_diff_zones(tap, dataset, cfg):
    cfg.set('generate_pins.roles', ['admin'])
    cfg.set('generate_pins.timespan', '00:00-06:00')

    users = []
    tzs = list(set(pytz.all_timezones) - {'NZ-CHAT', 'Pacific/Chatham'})
    tzs_bad = sample([tz for tz in tzs if 12 < now(tzone(tz)).hour < 18], 2)
    tzs_good = sample([tz for tz in tzs if 0 < now(tzone(tz)).hour < 6], 2)

    with tap.plan(8, 'половина таймзон плохие'):
        for tz in tzs_bad + tzs_good:
            store = await dataset.store(tz=tz)
            user = await dataset.user(store_id=store.store_id)
            user.pin = '0000'
            if cfg('generate_pins.roles'):
                user.role = cfg('generate_pins.roles')[0]
            await user.save()
            users.append(user)

        await generate_pins()

        for i, user in enumerate(users):
            await user.reload()
            new_pin = user.pin
            tap.ok(new_pin, f'{i+1}-й пин загружен')
            if i >= 2:
                tap.ne_ok(new_pin, '0000', f'{new_pin} не равно 0000')
            else:
                tap.eq(new_pin, '0000', f'{new_pin} равно 0000')


async def test_generate_pins_diff_update(tap, dataset, cfg):
    cfg.set('generate_pins.roles', ['admin'])
    cfg.set('generate_pins.timespan', '00:00-06:00')

    users = []
    good_tzs = list(set(pytz.all_timezones) - {'NZ-CHAT', 'Pacific/Chatham'})
    tzs = [tz for tz in good_tzs if 0 < now(tzone(tz)).hour < 6]
    tzs = sample(tzs, 4)

    with tap.plan(10, 'все таймзоны хорошие, различные поля обновлений'):
        for i, tz in enumerate(tzs):
            store = await dataset.store(tz=tz)
            tzs[i] = tzone(tz)

        users_params = [
            {
                'status': 'disabled',
            },
            {
                'status': 'active',
                'vars': {
                    'pin_updated': now(tzs[1]) - timedelta(hours=12)
                },
            },
            {
                'status': 'active',
                'vars': {
                    'pin_updated': now(tzs[2]) - timedelta(days=1, hours=12)
                },
            },
            {
                'status': 'active',
                'vars': {},
            },
            {
                'status': 'active',
                'role': 'city_head',
                'vars': {},
            },
        ]
        results = [False, False, True, True, False]
        if cfg('generate_pins.roles'):
            for up in users_params:
                if 'role' not in up.keys():
                    up['role'] = cfg('generate_pins.roles')[0]

        for attrs in users_params:
            user = await dataset.user(store_id=store.store_id)
            user.pin = '0000'
            for k, v in attrs.items():
                setattr(user, k, v)
            await user.save()
            users.append(user)

        await generate_pins()

        for i, user in enumerate(users):
            await user.reload()
            new_pin = user.pin
            tap.ok(new_pin, f'{i+1}-й пин загружен')
            if results[i]:
                tap.ne_ok(new_pin, '0000', f'{new_pin} не равно 0000')
            else:
                tap.eq(new_pin, '0000', f'{new_pin} равно 0000')
