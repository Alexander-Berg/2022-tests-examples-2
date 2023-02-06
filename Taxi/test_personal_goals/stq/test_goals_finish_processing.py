# pylint: disable=redefined-outer-name
import typing

from aiohttp import web
import pytest

from personal_goals import const
from personal_goals.modules.cashback import plus_transactions
from personal_goals.stq import goals_finish_processing


def _make_reward_promocode_info(user_goal_id, series=None):
    return {
        'reward': {
            'bonus': {
                'type': 'promocode',
                'series': series or 'some_series',
                'value': '500',
                'currency': 'RUB',
            },
            'status': const.REWARD_STATUS_NOT_REWARDED,
            'yandex_uid': '666666',
        },
        'user_goal_id': user_goal_id,
    }


def _make_reward_cashback_boost_info(user_goal_id, value):
    return {
        'reward': {
            'bonus': {
                'type': const.BONUS_TYPE_CASHBACK_BOOST,
                'days': 5,
                'percent': value,
                'classes': ['econom'],
            },
            'status': const.REWARD_STATUS_NOT_REWARDED,
            'yandex_uid': '666667',
        },
        'user_goal_id': user_goal_id,
    }


def _make_reward_cashback_fixed_info(user_goal_id):
    return {
        'reward': {
            'bonus': {
                'type': const.BONUS_TYPE_CASHBACK_FIXED,
                'value': '100',
                'currency': 'RUB',
            },
            'status': const.REWARD_STATUS_NOT_REWARDED,
            'yandex_uid': '666668',
        },
        'user_goal_id': user_goal_id,
    }


async def test_goals_finish_processing(
        stq3_context, mock_personal_goals, mock_coupons,
):
    @mock_personal_goals('/internal/reward/info')
    def _mock_reward_info(request):
        assert request.json['user_goal_id'] == goal_id
        return _make_reward_promocode_info(goal_id)

    @mock_personal_goals('/internal/reward/complete')
    def _mock_reward_complete(request):
        assert request.json['user_goal_id'] == goal_id
        return web.Response()

    @mock_coupons('/internal/generate')
    def _mock_generate(request):
        assert request.json['token'] == goal_id
        assert request.json['series_id'] == 'some_series'
        return {
            'promocode': 'TURBO',
            'promocode_params': {
                'value': 1,
                'currency_code': 'RUB',
                'expire_at': '2021-06-30',
            },
        }

    goal_id = '5_comfort_rides'
    await goals_finish_processing.task(stq3_context, goal_id, 'order_id_1')


@pytest.mark.config(
    PERSONAL_GOALS_BONUS_SERIES_MAPPING={'personalgoal225': 'pgpa'},
)
async def test_goal_finish_processing_mapping(
        stq3_context, mock_personal_goals, mock_coupons,
):
    @mock_personal_goals('/internal/reward/info')
    def _mock_reward_info(request):
        return _make_reward_promocode_info(goal_id, series='personalgoal225')

    @mock_personal_goals('/internal/reward/complete')
    def _mock_reward_complete(request):
        return {}

    @mock_coupons('/internal/generate')
    def _mock_generate(request):
        assert request.json['series_id'] == 'pgpa'
        return {
            'promocode': 'TURBO',
            'promocode_params': {
                'value': 1,
                'currency_code': 'RUB',
                'expire_at': '2021-06-30',
            },
        }

    goal_id = '5_comfort_rides'
    await goals_finish_processing.task(stq3_context, goal_id, 'order_id_1')


async def test_goals_finish_processing_cashback_boost(
        stq3_context, mock_personal_goals, mockserver,
):
    @mock_personal_goals('/internal/reward/info')
    def _mock_reward_info(request):
        assert request.json['user_goal_id'] == goal_id
        return _make_reward_cashback_boost_info(goal_id, 4)

    @mock_personal_goals('/internal/reward/complete')
    def _mock_reward_complete(request):
        assert request.json['user_goal_id'] == goal_id
        return web.Response()

    @mockserver.json_handler('/passenger-tags/v1/upload')
    def _mock_tags_upload(request):
        assert request.query['provider_id'] == 'personal-goals'
        assert request.json == {
            'entity_type': 'yandex_uid',
            'tags': [
                {
                    'match': {'id': '666667', 'ttl': 432000},
                    'name': 'cashback_boost_for_econom_percent_4',
                },
            ],
            'merge_policy': 'append',
        }
        return {}

    goal_id = '3_econom_rides'
    await goals_finish_processing.task(stq3_context, goal_id, 'order_id_1')


class MyTestCase(typing.NamedTuple):
    cashback_status: str = 'init'
    has_plus: str = 'true'
    goal_id: str = '100_RUB_cashback'
    has_order_invoice: bool = True
    update_cashback_exception: typing.Optional[Exception] = None
    should_reschedule: bool = False
    should_complete_reward: bool = False


@pytest.mark.config(
    PERSONAL_GOALS_BILLING_INFO_MAP={
        'yandex_birthday': {
            'billing_service': 'card',
            'billing_service_id': '124',
            'cashback_service': 'yataxi',
            'cashback_type': 'transaction',
            'issuer': 'taxi',
            'campaign_name': 'personal_goals_taxi',
            'product_id': 'personal_goals_cashback_bonus',
            'ticket': 'NEWSERVICE-000',
        },
    },
)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(goal_id='not_exist'), id='no_goal'),
        pytest.param(
            MyTestCase(
                update_cashback_exception=plus_transactions.UpdateCashbackRaceCondition(),  # noqa: E501
                should_reschedule=True,
            ),
            id='update_cashback_race_condition',
        ),
        pytest.param(
            MyTestCase(cashback_status='init', should_reschedule=True),
            id='cashback_status_init',
        ),
        pytest.param(
            MyTestCase(
                has_plus='false',
                cashback_status='init',
                should_reschedule=True,
            ),
            id='update_cashback_user_does_not_have_plus',
        ),
        pytest.param(
            MyTestCase(cashback_status='in_progress', should_reschedule=True),
            id='cashback_status_in_progress',
        ),
        pytest.param(
            MyTestCase(
                cashback_status='success',
                should_reschedule=False,
                should_complete_reward=True,
            ),
            id='cashback_status_success',
        ),
        pytest.param(
            MyTestCase(cashback_status='failed', should_reschedule=False),
            id='cashback_status_failed',
        ),
    ],
)
async def test_goals_finish_processing_cashback_fixed(
        stq3_context,
        plus_transactions_fixt,
        mock_reschedule,
        mock_personal_goals,
        mockserver,
        case,
):
    @mockserver.json_handler('/blackbox', prefix=True)
    async def _mock_passport(request):
        assert request.query['attributes'] == '1015'
        assert request.query['uid'] == '666668'
        return {
            'users': [
                {
                    'uid': {'value': '666668'},
                    'login': 'yalogin',
                    'attributes': {
                        '1015': 1 if case.has_plus == 'true' else 0,
                    },
                },
            ],
        }

    @mock_personal_goals('/internal/reward/info')
    def _mock_reward_info(request):
        assert request.json['user_goal_id'] == case.goal_id
        return _make_reward_cashback_fixed_info(case.goal_id)

    @mock_personal_goals('/internal/reward/complete')
    def _mock_reward_complete(request):
        assert request.json['user_goal_id'] == case.goal_id
        return web.Response()

    @mockserver.json_handler('/cashback/v1/cashback/payload')
    def _mock_cashback_payload(request):
        return {
            'payload': {
                'order_id': 'order_id_1',
                'alias_id': 'alias_id',
                'oebs_mvp_id': 'MSKc',
                'tariff_class': 'econom',
                'currency': 'RUB',
                'country': 'RU',
                'base_amount': '356.0',
            },
        }

    plus_transactions_fixt.ext_ref_id = case.goal_id
    plus_transactions_fixt.yandex_uid = '666668'

    plus_transactions_fixt.update_cashback_exception = (
        case.update_cashback_exception
    )
    plus_transactions_fixt.cashback_status = case.cashback_status

    order_id = 'order_id_1'
    plus_transactions_fixt.order_id = order_id
    plus_transactions_fixt.has_plus = case.has_plus

    queue_mock = mock_reschedule(
        stq3_context.stq.goals_finish_processing.queue_name,
    )

    await goals_finish_processing.task(stq3_context, case.goal_id, order_id)

    assert queue_mock.has_calls == case.should_reschedule
    assert _mock_reward_complete.has_calls == case.should_complete_reward
