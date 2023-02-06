from stall.model.role import Role


def test_guest(tap):

    with tap.plan(5, 'Тестируем роль гостя'):
        guest = Role('guest')
        tap.ok(guest, 'инстанцирован')

        tap.ok(guest.has_permit('login'), 'может логиниться')
        tap.ok(not guest.has_permit('1unknown'), 'не может делать фигню')

        tap.eq(guest.permit('login'), True, 'значение пермита')
        tap.ok(guest.virtual, 'Виртуальная роль')

