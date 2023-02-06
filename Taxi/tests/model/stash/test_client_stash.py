import datetime

import libstall.util

from stall.model.stash import ClientStash


async def test_samples_not_exists(tap, uuid):
    with tap:
        tap.ok(
            await ClientStash.samples(uuid()) == {}, 'у клиента нет семплов',
        )


async def test_samples_exists(tap, uuid, now):
    with tap:
        client_id = uuid()

        s = ClientStash(
            {'name': f'{client_id}:samples', 'value': {uuid(): now()}}
        )
        await s.save()

        tap.ok(s.stash_id, 'создали стеш')
        tap.ok(await ClientStash.samples(client_id), 'получили семплы')


async def test_samples_new(tap, uuid):
    with tap:
        now = libstall.util.now()
        client_id = uuid()
        product_ids = [uuid(), uuid()]

        samples = await ClientStash.samples(client_id, product_ids)

        tap.eq(set(samples.keys()), set(product_ids), 'корректные продукты')
        tap.eq(
            list(samples.values())[0].date(),
            now.date(),
            'последняя дата использования сэмпла',
        )


async def test_samples_update_used(tap, uuid):
    with tap:
        past = libstall.util.now() - datetime.timedelta(days=2)
        client_id = uuid()
        product_ids = [uuid(), uuid()]

        s = ClientStash(
            {
                'name': f'{client_id}:samples',
                'value': {
                    product_ids[0]: past,
                    product_ids[1]: past,
                }
            }
        )
        await s.save()

        tap.ok(s.stash_id, 'создали стеш')

        samples = await ClientStash.samples(client_id)

        tap.eq(
            [samples[product_ids[0]].date(), samples[product_ids[1]].date()],
            [past.date(), past.date()],
            'семплы на месте',
        )

        samples = await ClientStash.samples(client_id, [product_ids[0]])

        tap.ok(
            samples[product_ids[0]].date() > past.date(),
            'время использования обновилось',
        )
        print(samples[product_ids[0]].date(),  past.date())
        tap.ok(
            samples[product_ids[1]].date() == past.date(),
            'время использования не обновилось',
        )


async def test_samples_update_expired(tap, uuid):
    with tap:
        past = libstall.util.now() - datetime.timedelta(days=2)
        client_id = uuid()
        product_ids = [uuid(), uuid()]

        s = ClientStash(
            {
                'name': f'{client_id}:samples',
                'value': {
                    product_ids[0]: past,
                    product_ids[1]: past,
                },
                'expired': past,
            }
        )
        await s.save()

        tap.ok(s.stash_id, 'создали стеш')
        tap.eq(s.expired, past, 'корректный экспайред')

        tap.ok(
            await ClientStash.samples(client_id, product_ids),
            'семплы обновили',
        )

        await s.reload()

        tap.ok(s.expired > past, 'время протухания обновилось')
