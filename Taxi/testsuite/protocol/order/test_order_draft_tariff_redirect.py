import pytest

from order_core_exp_parametrize import CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
from protocol.order.order_draft_common import orderdraft


@pytest.mark.filldb(tariff_settings='test_tariff_redirect')
@pytest.mark.parametrize(
    ['comment', 'expected_code', 'excpected_error', 'city'],
    (
        pytest.param(
            'детское кресло',
            200,
            None,
            'helsinki',
            id='child_chair_with_tariff_presented',
        ),
        pytest.param(
            'доставка',
            200,
            None,
            'moscow',
            id='express_with_tariff_presented',
        ),
        pytest.param(
            'детское кресло',
            406,
            'CHILDCHAIR_BANNED_COMMENT',
            'moscow',
            id='child_chair_without_tariff_presented',
        ),
        pytest.param(
            'доставка',
            406,
            'EXPRESS_BANNED_COMMENT',
            'helsinki',
            id='express_without_tariff_presented',
        ),
    ),
)
@pytest.mark.order_experiments('child_chair_ban_comment')
@pytest.mark.experiments3(filename='exp3_banned_comments.json')
@pytest.mark.config(
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=[
        {
            'excluded_classes': ['cargo', 'courier', 'express'],
            'redirect_to': 'express',
            'words': ['доставка'],
        },
        {
            'excluded_classes': ['cargo', 'courier', 'express'],
            'redirect_to': 'child_tariff',
            'words': ['детское кресло'],
        },
    ],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_tariff_redirect(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        comment,
        expected_code,
        excpected_error,
        city,
):
    """
    db_tariff_settings_test_tariff_redirect:
    Moscow zone has express and doesn't have child_tariff
    Helsinki zone has child_tariff and doesn't have express
    """
    order_path = 'tariff_redirect'
    request = load_json(f'{order_path}/request_{city}.json')
    request['comment'] = comment

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )

    if expected_code == 406:
        assert response['error']['code'] == excpected_error
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled
