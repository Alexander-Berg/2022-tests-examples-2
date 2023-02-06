import pytest

from scripts.dev.remove_roles_of_dismissed import remove_roles_of_dismissed


@pytest.mark.parametrize('apply', [False, True])
async def test_remove_roles(tap, dataset, apply):
    with tap:
        user1 = await dataset.user(provider='yandex-team',
                                   role='store_admin',
                                   status='disabled')
        user2 = await dataset.user(provider='yandex-team',
                                   role='store_admin',
                                   status='disabled')
        user3 = await dataset.user(provider='yandex-team',
                                   role='store_admin',
                                   status='active')

        # pylint: disable=unused-argument
        async def get_users(uids):
            return {
                user1.provider_user_id: {
                    'uid': user1.provider_user_id,
                    'official': {
                        'is_dismissed': False,
                    }
                },
                user2.provider_user_id: {
                    'uid': user2.provider_user_id,
                    'official': {
                        'is_dismissed': True,
                    }
                },
                user3.provider_user_id: {
                    'uid': user3.provider_user_id,
                    'official': {
                        'is_dismissed': False,
                    }
                },
            }

        await remove_roles_of_dismissed(get_users, apply=apply)

        await user1.reload()
        await user2.reload()
        await user3.reload()

        tap.eq(user1.role, 'store_admin',
               'user is not dismissed, role did not change')

        if apply:
            tap.eq(user2.role, 'authen_guest',
                   'user was dismissed, role removed')
        else:
            tap.eq(user2.role, 'store_admin',
                   'apply is False, role did not change')
        tap.eq(user3.role, 'store_admin',
               'user is not disabled, role did not change')
        tap.eq(user3.status, 'active',
               'active user is still active')


@pytest.mark.parametrize('force', [False, True])
async def test_remove_roles_force(tap, dataset, force):
    with tap:
        user1 = await dataset.user(provider='yandex-team',
                                   role='store_admin',
                                   status='disabled')
        user2 = await dataset.user(provider='yandex-team',
                                   role='store_admin',
                                   status='disabled')

        # pylint: disable=unused-argument
        async def get_users(uids):
            return {
                user1.provider_user_id: {
                    'uid': user1.provider_user_id,
                    'official': {
                        'is_dismissed': True,
                    }
                },
            }

        await remove_roles_of_dismissed(get_users, apply=True, force=force)

        await user1.reload()
        await user2.reload()

        tap.eq(user1.role, 'authen_guest',
               'user was dismissed, role removed')

        if force:
            tap.eq(user2.role, 'authen_guest',
                   "user's not on staff, force is True, role removed")
        else:
            tap.eq(user2.role, 'store_admin',
                   "user's not on staff, force is false, role didn't changed")
