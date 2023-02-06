import datetime

import libstall.util

from stall.model.stash import Stash


async def test_coerce_expired(tap):
    with tap.plan(3):
        s = Stash({})
        await s.save()

        tap.eq_ok(s.expired, None, 'No TTL')

        now = libstall.util.now()

        s.expired = 60
        await s.save()

        tap.ok(
            now < s.expired <= (now + datetime.timedelta(seconds=65)),
            'TTl in seconds',
        )

        s.expired = now
        await s.save()

        tap.eq_ok(
            s.expired,
            now,
            'TTL as datetime',
        )


async def test_ilist_expired(tap):
    with tap:
        now = libstall.util.now()

        not_expired = set()
        s = await Stash.stash()
        not_expired.add(s.stash_id)
        s = await Stash.stash(
            expired=(now + datetime.timedelta(seconds=60))
        )
        not_expired.add(s.stash_id)

        tap.ok(
            not not_expired.issubset(
                {i.stash_id async for i in Stash.ilist_expired()}
            ),
            '2 not expired stashes'
        )

        expired = set()
        for i in range(5):
            s = await Stash.stash(
                expired=(now - datetime.timedelta(seconds=i))
            )
            expired.add(s.stash_id)

        tap.ok(
            expired.issubset(
                {i.stash_id async for i in Stash.ilist_expired()}
            ),
            '5 expired stashes'
        )

        staled = set()
        updated = now - datetime.timedelta(seconds=60)
        for i in range(5):
            s = Stash({'updated': updated})
            await s.save()
            staled.add(s.stash_id)

        tap.ok(
            staled.issubset(
                {i.stash_id async for i in Stash.ilist_expired(force_ttl=30)}
            ),
            '5 expired stashes with force_ttl'
        )
