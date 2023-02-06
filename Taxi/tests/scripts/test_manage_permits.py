import os
import ruamel.yaml

from scripts.dev.manage_permits import view_permit, add_permit, remove_permit

yaml = ruamel.yaml.YAML()  # pylint: disable=invalid-name
yaml.indent(offset=2)

PERMITS = {
    'roles': {
        'guest': {
            'permits': {
                'login': True,
                'sub': [
                    'executer',
                    'authen_guest'
                ],
            }
        },
        'admin': {
            'permits': {
                'login': True,
            }
        },
        'store_admin': {
            'permits': {
                'login': False,
            }
        }
    }
}


async def test_view_permit(tap):
    with tap.plan(6, 'Просмотр пермитов'):
        test_permits_file = 'tests/scripts/test_view_permit.yaml'
        with open(test_permits_file, 'w') as f:
            yaml.dump(PERMITS, f)

        tap.eq_ok(
            await view_permit('login', 'guest', test_permits_file),
            True,
            'Получение одного пермита одной роли'
        )

        with tap.raises(ValueError, 'Нет пермита'):
            await view_permit('login1', 'guest', test_permits_file)

        with tap.raises(ValueError, 'Нет роли'):
            await view_permit('login', 'guest1', test_permits_file)

        tap.eq_ok(
            await view_permit('sub', 'guest', test_permits_file),
            ['authen_guest', 'executer'],
            'Получение пермита со значением-списком (отсортированно)'
        )

        tap.eq_ok(
            await view_permit('login', None, test_permits_file),
            ['admin', 'guest'],
            'Получение списка ролей с пермитом (отсортированно)'
        )

        with tap.raises(ValueError, 'Нет ролей с пермитом'):
            await view_permit('login1', None, test_permits_file)

        os.remove(test_permits_file)


async def test_add_permit(tap):
    with tap.plan(3, 'Добавление пермита'):
        test_permits_file = 'tests/scripts/test_add_permit.yaml'
        with open(test_permits_file, 'w') as f:
            yaml.dump(PERMITS, f)

        await add_permit('logout', 'guest', file=test_permits_file, quiet=True)
        with open(test_permits_file) as f:
            data = yaml.load(f)
            tap.eq_ok(
                data['roles']['guest']['permits']['logout'],
                True,
                'Добавление нового пермита'
            )

        await add_permit('login', 'store_admin', file=test_permits_file,
                         force_add=True, quiet=True)
        with open(test_permits_file) as f:
            data = yaml.load(f)
            tap.eq_ok(
                data['roles']['store_admin']['permits']['login'],
                True,
                'Изменение существующего пермита'
            )

        with tap.raises(ValueError, 'Нет роли'):
            await add_permit('login', 'guest1', test_permits_file)

        os.remove(test_permits_file)


async def test_remove_permit(tap):
    with tap.plan(4, 'Удаление пермита'):
        test_permits_file = 'tests/scripts/test_remove_permit.yaml'
        with open(test_permits_file, 'w') as f:
            yaml.dump(PERMITS, f)

        await remove_permit('login', 'guest', file=test_permits_file,
                            quiet=True)
        with open(test_permits_file) as f:
            data = yaml.load(f)
            tap.eq_ok(len(data['roles']['guest']['permits']), 1,
                      'Остался один пермит роли guest')
            tap.ok(data['roles']['guest']['permits'].keys().__contains__('sub'),
                   'И он \'sub\'')

        with tap.raises(ValueError, 'Нет роли'):
            await remove_permit('login', 'guest1', test_permits_file,
                                quiet=True)

        with tap.raises(ValueError, 'Нет пермита роли'):
            await remove_permit('login1', 'guest', test_permits_file,
                                quiet=True)

        os.remove(test_permits_file)
