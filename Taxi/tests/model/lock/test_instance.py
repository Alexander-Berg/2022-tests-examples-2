from stall.model.lock import Lock


def test_instance(tap, uuid):
    with tap.plan(1):
        lock = Lock({
            'name': uuid(),
        })
        tap.ok(lock, 'Лок')


async def test_save(tap, uuid):
    with tap.plan(2):
        lock = Lock({
            'name': uuid(),
        })
        tap.ok(lock, 'Лок')

        no_save = False
        try:
            await lock.save()
        except RuntimeError:
            no_save = True

        tap.eq(no_save, True, 'Сохранять напрямую нельзя')
