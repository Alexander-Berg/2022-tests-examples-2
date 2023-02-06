import pytest
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from l3mgr.models import (
    RealServerState,
    VirtualServerState,
)
from l3mgr.tasks.clean_up_obsoleted_helpers import (
    filter_balancers_not_available_for_deploy,
    find_lbs_with_obsoleted_vs_to_redeploy,
    update_vs_and_rs_states,
)


BALANCERS_WITH_OBSOLETED_VS = {537, 538}
BALANCER_TO_FILTER = {537}
OBSOLETED_VS = {48125, 47896}


@pytest.fixture
def preconfigure_database():
    """
    Setup DB fields for testing
    """
    # Clear all obsoleted VSs to avoid mixing with target obsoleted VSs
    VirtualServerState.objects.filter(state="OBSOLETED", balancer_id__in=BALANCERS_WITH_OBSOLETED_VS,).update(
        state="DISABLED", timestamp=timezone.now() - timedelta(minutes=60), description="test",
    )

    # Set OBSOLETED state for target VSs and balancers
    VirtualServerState.objects.filter(vs_id__in=OBSOLETED_VS, balancer_id__in=BALANCERS_WITH_OBSOLETED_VS,).update(
        state="OBSOLETED", timestamp=timezone.now() - timedelta(minutes=60), description="test",
    )


def add_committed_state(lbs):
    """
    Set committed state to VS on balancer to test filter_balancers_not_available_for_deploy
    """
    VirtualServerState.objects.filter(state="OBSOLETED", balancer_id__in=lbs).update(
        state="COMMITTED", timestamp=timezone.now() - timedelta(minutes=60), description="test",
    )


def count_of_rs_to_disable(obsoleted_vss, lb_id):
    """
    Finds amount of RSs for OBSOLETED VSs to compare this with
    amount of RSs disabled by update_vs_and_rs_states
    """
    return RealServerState.objects.filter(vs_id__in=obsoleted_vss, balancer_id__in=lb_id).count()


def check_vs_disabled(vss, lb_id):
    """
    Compares number of given VSs for lb_id with number of disabled VSs for lb_id in DB
    returns True if all VSs are disabled
    """
    return len(vss) == VirtualServerState.objects.filter(state="DISABLED", vs_id__in=vss, balancer_id=lb_id).count()


@pytest.mark.django_db
def test_find_lbs_with_obsoleted_vs_to_redeploy(preconfigure_database):
    assert find_lbs_with_obsoleted_vs_to_redeploy() & BALANCERS_WITH_OBSOLETED_VS == BALANCERS_WITH_OBSOLETED_VS


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lbs,lbs_to_filter,lbs_filtered_result",
    [
        (BALANCERS_WITH_OBSOLETED_VS, None, BALANCERS_WITH_OBSOLETED_VS),
        (BALANCERS_WITH_OBSOLETED_VS, BALANCER_TO_FILTER, BALANCERS_WITH_OBSOLETED_VS - BALANCER_TO_FILTER),
        (BALANCERS_WITH_OBSOLETED_VS, BALANCERS_WITH_OBSOLETED_VS, set()),
    ],
)
def test_filter_balancers_not_available_for_deploy(lbs, lbs_to_filter, lbs_filtered_result, preconfigure_database):
    if lbs_to_filter:
        add_committed_state(lbs_to_filter)

    assert filter_balancers_not_available_for_deploy(lbs) == lbs_filtered_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lb_id, expected_vs_to_disable, expected_vs_disabled, expected_rs_disabled, check_vs_disabled",
    [
        (
            BALANCER_TO_FILTER,
            "Obsolete VS to be disabled: {}".format(OBSOLETED_VS),
            "Disabled obsoleted VSs: {}".format(OBSOLETED_VS),
            lambda: "Disabled {} RSs belonging to obsoleted VSs: {}".format(
                count_of_rs_to_disable(OBSOLETED_VS, BALANCER_TO_FILTER), OBSOLETED_VS
            ),
            lambda: check_vs_disabled(OBSOLETED_VS, *BALANCER_TO_FILTER),
        )
    ],
)
@patch("l3mgr.utils.clean_up_obsoleted_helpers.logger.info")
@patch("l3mgr.utils.clean_up_obsoleted_helpers.logger.debug")
def test_update_vs_and_rs_states(
    mocked_logger_debug,
    mocked_logger_info,
    lb_id,
    expected_vs_to_disable,
    expected_vs_disabled,
    expected_rs_disabled,
    check_vs_disabled,
    preconfigure_database,
):
    expected_rs_disabled = expected_rs_disabled()
    update_vs_and_rs_states(*lb_id)

    mocked_logger_debug.assert_called_with(expected_vs_to_disable)
    mocked_logger_info.mock_calls[0].assert_called_with(expected_vs_disabled)
    mocked_logger_info.mock_calls[1].assert_called_with(expected_rs_disabled)
    assert check_vs_disabled()
