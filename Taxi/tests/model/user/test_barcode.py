async def test_qrcode(tap, dataset):
    tap.plan(4)
    user = await dataset.user()

    tap.ok(user, 'пользователь сгенерирован')
    tap.isa_ok(user.qrcode, str, 'qrкод есть')

    loaded = await user.load(user.qrcode, by='barcode')
    tap.ok(loaded, 'Загружен по qrкоду')
    tap.eq(loaded.user_id, user.user_id, 'идентификатор пользователя')

    tap()
