import argparse
import pytest
from stall.model.user import User
from scripts.cron.disable_users import disable_users


@pytest.mark.parametrize('is_dismissed', [
    'True',
    'False'
])
async def test_disable_user(tap, dataset, is_dismissed, uuid):
    with tap.plan(3, 'Удаление пользователей'):
        uid = uuid()
        company = await dataset.company()

        user = await dataset.user(
            provider='yandex-team',
            provider_user_id=uid,
            status='active',
            company_id=company.company_id,
        )

        tap.ok(user, 'Пользователь создан')

        staff_data = {
            uid: {
                'uid': uid,
                'login': 'login',
                'official': {
                    'is_dismissed': is_dismissed,
                    }
                },
            }

        wms_users = await User.list(
            by='look',
            conditions=[
                ('company_id', [company.company_id,]),
            ],
            db={'mode': 'slave'},
            limit=100,
        )

        await disable_users(
            wms_users=wms_users,
            staff_users=staff_data,
            args=argparse.Namespace(
                apply=True,
                force=False,
            )
        )

        await user.reload()
        tap.eq_ok(user.status, 'disabled', 'статус изменен')
        tap.eq_ok(user.role, 'authen_guest', 'роль отозвана')


async def test_disable_if_not_found(tap, dataset, uuid):
    with tap.plan(3, 'Удаление пользователей'):
        uid = uuid()
        company = await dataset.company()

        user = await dataset.user(
            provider='yandex-team',
            provider_user_id=uid,
            status='active',
            company_id=company.company_id,
        )

        tap.ok(user, 'Пользователь создан')

        staff_data = {}

        wms_users = await User.list(
            by='look',
            conditions=[
                ('company_id', [company.company_id,]),
            ],
            db={'mode': 'slave'},
            limit=100,
        )

        await disable_users(
            wms_users=wms_users,
            staff_users=staff_data,
            args=argparse.Namespace(
                apply=True,
                force=True,
            )
        )

        await user.reload()
        tap.eq_ok(user.status, 'disabled', 'статус изменен')
        tap.eq_ok(user.role, 'authen_guest', 'роль отозвана')
