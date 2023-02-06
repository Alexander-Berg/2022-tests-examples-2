import dataclasses
from typing import Dict
from typing import List
from typing import Optional

import pytest


TEST_LOGIN = 'random_man'

GET_SUMMONED_USERS = """
    select
        draft_id,
        yandex_login
    from
        approvals_schema.summons s
    where
        yandex_login = any($1::text[])
    order by draft_id, yandex_login;
"""


@dataclasses.dataclass(frozen=True)
class SummonTestCase:
    summon_users: List[str]
    found_logins: List[str]
    draft_tickets: List[str]
    draft_id: int = 1
    status_code: int = 200
    send_email: bool = True
    tplatform_namespace: Optional[str] = 'taxi'
    error_code: Optional[str] = None
    not_found_logins: Optional[List[str]] = None
    db_summoned_users: Optional[List[Dict]] = None

    @property
    def return_logins(self):
        summoned_users = []
        if self.draft_id == 1:
            summoned_users.extend(
                [
                    {
                        'login': 'test_login1',
                        'summoned': '2017-11-01T04:10:00+0300',
                    },
                    {
                        'login': 'test_login2',
                        'summoned': '2017-11-01T04:10:00+0300',
                    },
                ],
            )
        if self.found_logins:
            for login in self.found_logins:
                summoned_users.append(
                    {'login': login, 'summoned': '2019-05-14T03:05:00+0300'},
                )
        return summoned_users


@pytest.mark.parametrize(
    'case',
    [
        SummonTestCase(
            summon_users=['test_login', 'test_login_2'],
            found_logins=['test_login', 'test_login_2'],
            draft_tickets=['https://st.test.yandex-team.ru/TAXIRATE-35'],
            not_found_logins=[],
        ),
        SummonTestCase(
            summon_users=['test_login', 'not_expected', 'not_expected_2'],
            found_logins=['test_login'],
            draft_tickets=['https://st.test.yandex-team.ru/TAXIRATE-35'],
            not_found_logins=['not_expected', 'not_expected_2'],
        ),
        SummonTestCase(
            summon_users=['not_expected', 'not_expected_2'],
            found_logins=[],
            draft_tickets=['https://st.test.yandex-team.ru/TAXIRATE-35'],
            not_found_logins=['not_expected', 'not_expected_2'],
            send_email=False,
        ),
        SummonTestCase(
            status_code=400,
            error_code='invalid-input',
            summon_users=[],
            found_logins=[],
            draft_tickets=['https://st.test.yandex-team.ru/TAXIRATE-35'],
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_summon_approvers(taxi_approvals_client, case, stq_put_mock):
    stq_put = stq_put_mock(
        draft_id=case.draft_id,
        expected_found_logins=case.found_logins,
        expected_tickets=case.draft_tickets,
        tplatform_namespace=case.tplatform_namespace,
    )

    response = await taxi_approvals_client.post(
        f'/drafts/{case.draft_id}/summon_approvers/',
        json={'summon_users': case.summon_users},
        headers={'X-Yandex-Login': TEST_LOGIN},
    )
    content = await response.json()
    assert response.status == case.status_code
    if case.status_code == 200:
        expected = _create_expected_for_summon_approvers(case)
        assert content == expected
        put_calls = 1 if case.send_email else 0
        assert len(stq_put.calls) == put_calls
    else:
        assert content['code'] == case.error_code


@pytest.mark.parametrize(
    'case',
    [
        SummonTestCase(
            draft_id=3,
            summon_users=['test_login', 'test_login_2'],
            found_logins=['test_login', 'test_login_2'],
            draft_tickets=[],
            not_found_logins=[],
            db_summoned_users=[
                {'draft_id': 3, 'yandex_login': 'test_login'},
                {'draft_id': 3, 'yandex_login': 'test_login_2'},
                {'draft_id': 4, 'yandex_login': 'test_login'},
                {'draft_id': 4, 'yandex_login': 'test_login_2'},
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_multidraft_summon_approvers(
        taxi_approvals_client, case, stq_put_mock,
):
    stq_put = stq_put_mock(
        draft_id=case.draft_id,
        expected_found_logins=case.found_logins,
        expected_tickets=case.draft_tickets,
        api_path='$multidraft',
        service_name='$multidraft',
    )
    response = await taxi_approvals_client.post(
        f'/multidrafts/summon_approvers/',
        json={
            'summon_users': case.summon_users,
            'multidraft_id': case.draft_id,
        },
        headers={'X-Yandex-Login': TEST_LOGIN},
    )
    content = await response.json()
    assert response.status == case.status_code
    if case.status_code == 200:
        expected = _create_expected_for_summon_approvers(case)
        assert content == expected
        put_calls = 1 if case.send_email else 0
        assert len(stq_put.calls) == put_calls

        pool = taxi_approvals_client.app['pool']
        async with pool.acquire() as conn:
            result = await conn.fetch(GET_SUMMONED_USERS, case.found_logins)
            result = [dict(res) for res in result]
            assert result == case.db_summoned_users


def _create_expected_for_summon_approvers(case):
    summoned_users = case.return_logins
    expected = {'summoned_users': summoned_users}
    if case.not_found_logins:
        not_found_text = ', '.join(case.not_found_logins)
        expected['comments'] = [
            {
                'login': TEST_LOGIN,
                'comment': (
                    f'Следующих пользователей не удалось найти '
                    f'или у них нет прав на подтверждение черновика: '
                    f'{not_found_text}. Они не будут призваны'
                ),
            },
        ]
    return expected
