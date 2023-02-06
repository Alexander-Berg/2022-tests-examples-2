import logging
from unittest.mock import patch, Mock

from django import test
from django.test import TestCase
from parameterized import parameterized

from l3common.tests.cases import override_celery_settings
from .. import tasks
from ..models import (
    Configuration,
    LoadBalancer,
    Service,
    VirtualServer,
    VirtualServerState,
    RealServer,
    RealServerState,
)

logger: logging.Logger = logging.getLogger(__name__)


class CleanUpTestCase(test.SimpleTestCase):
    LBS_TO_REDEPLOY = [1, 2, 3]
    VS_IDS_TO_CLEAN_UP = [1000, 2000]

    @parameterized.expand(
        (
            # LBs to redeploy found case
            (LBS_TO_REDEPLOY,),
            # LBs to redeploy not found case
            ([],),
        )
    )
    @patch("l3mgr.tasks.process_lb_update_requests.si")
    @patch("l3mgr.tasks.clean_up_obsoleted_helpers.filter_balancers_not_available_for_deploy", new_callable=Mock)
    @patch("l3mgr.tasks.clean_up_obsoleted_helpers.find_lbs_with_obsoleted_vs_to_redeploy", new_callable=Mock)
    def test_clean_up_obsoleted_configs_on_lb(
        self,
        balancers_to_redeploy,
        mocked_find_lbs_with_obsoleted_vs_to_redeploy,
        mocked_filter_balancers_not_available_for_deploy,
        process_lb_update_requests_si_mock: Mock,
    ):
        mocked_find_lbs_with_obsoleted_vs_to_redeploy.return_value = balancers_to_redeploy
        mocked_filter_balancers_not_available_for_deploy.return_value = balancers_to_redeploy

        self.assertEqual(len(balancers_to_redeploy), len(tasks.clean_up_obsoleted_configs_on_lb()))
        self.assertListEqual(balancers_to_redeploy, [c[0][0] for c in process_lb_update_requests_si_mock.call_args_list])

    @patch("l3mgr.tasks.chain", new_callable=Mock())
    @patch("l3mgr.tasks.process_lb_update_requests.si", new_callable=Mock())
    @patch("l3mgr.tasks._wait_for_obsoleted.si", new_callable=Mock())
    @patch("l3mgr.tasks.release_lb.si", new_callable=Mock())
    @patch("l3mgr.tasks.lock_lb.si", new_callable=Mock())
    @override_celery_settings(task_always_eager=True)
    def test_redeploy_lbs_and_sync_obsoleted_vs_states(
        self,
        mocked_lock_lb,
        mocked_release_task,
        mocked__wait_for_obsoleted,
        mocked_process_lb_update_requests,
        mocked_chain,
    ):
        with patch("l3mgr.models.LoadBalancer.objects.get", new_callable=Mock()) as lb_get, patch(
            "l3mgr.models.LoadBalancerConfigurationUpdateRequest.objects.get_or_create", new_callable=Mock()
        ) as lb_deploy:
            lb_get.return_value.mode = LoadBalancer.ModeChoices.ACTIVE
            lb_deploy.return_value = Mock(), True

            tasks.schedule_lb_update_request(self.LBS_TO_REDEPLOY[0], None)

        mocked_chain.assert_called_once_with(
            mocked_lock_lb(),
            mocked__wait_for_obsoleted().on_error(),
            mocked_process_lb_update_requests().on_error(),
            mocked_release_task(),
        )

    @patch("l3mgr.utils.clean_up_obsoleted_helpers._find_vs_ids_to_clean_up", new_callable=Mock)
    @patch("l3mgr.utils.clean_up_obsoleted_helpers._delete_disabled_states", new_callable=Mock)
    @patch("l3mgr.utils.clean_up_obsoleted_helpers._change_rs_states_to_disabled", new_callable=Mock)
    @patch("l3mgr.utils.clean_up_obsoleted_helpers._change_vs_states_to_disabled", new_callable=Mock)
    def test__update_vs_and_rs_states(
        self,
        mocked__change_vs_states_to_disabled,
        mocked__change_rs_states_to_disabled,
        mocked__delete_disabled_states,
        mocked__find_vs_ids_to_clean_up,
    ):
        mocked__find_vs_ids_to_clean_up.return_value = self.VS_IDS_TO_CLEAN_UP

        balancer_to_redeploy = self.LBS_TO_REDEPLOY[0]
        self.assertIsNone(tasks._update_vs_and_rs_states(balancer_to_redeploy))
        mocked__find_vs_ids_to_clean_up.assert_called_once_with(balancer_to_redeploy)
        mocked__delete_disabled_states.assert_called_once_with(balancer_to_redeploy, self.VS_IDS_TO_CLEAN_UP)
        mocked__change_rs_states_to_disabled.assert_called_once_with(balancer_to_redeploy, self.VS_IDS_TO_CLEAN_UP)
        mocked__change_vs_states_to_disabled.assert_called_once_with(balancer_to_redeploy, self.VS_IDS_TO_CLEAN_UP)


class CleanUpParameterizedTestCase(TestCase):
    def setUp(self):
        svc = Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        lb = LoadBalancer.objects.create(
            fqdn="man1-lb2b.yndx.net",
            state=LoadBalancer.STATE_CHOICES.ACTIVE,
        )
        rss = RealServer.objects.bulk_create(
            [
                RealServer(fqdn="mnt-myt.yandex.net", ip="2a02:6b8:0:1482::115"),
                RealServer(fqdn="mnt-myt.yandex.net", ip="77.88.1.115"),
                RealServer(fqdn="mnt-sas.yandex.net", ip="2a02:6b8:b010:31::233"),
            ]
        )
        vs = VirtualServer.objects.create(
            service=svc,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port=80,
            protocol=VirtualServer.PROTOCOL_CHOICES.TCP,
            rs_ids=[rs.id for rs in rss],
            config={},
        )
        for rs in rss:
            RealServerState.objects.create(balancer=lb, vs=vs, server=rs, fwmark=1)
        VirtualServerState.objects.create(balancer=lb, vs=vs)
        Configuration.objects.create(service=svc, vs_ids=[vs.pk], description="test")

    def setStates(self, c_state, vs_state, rs_state):
        Configuration.objects.all().update(state=c_state)
        VirtualServerState.objects.all().update(state=vs_state)
        RealServerState.objects.all().update(state=rs_state)

    _C_ACTIVE = Configuration.STATE_CHOICES.ACTIVE
    _C_INACTIVE = Configuration.STATE_CHOICES.INACTIVE
    _VS_INACTIVE = VirtualServerState.STATE_CHOICES.INACTIVE
    _VS_DISABLED = VirtualServerState.STATE_CHOICES.DISABLED
    _VS_OBSOLETED = VirtualServerState.STATE_CHOICES.OBSOLETED
    _RS_INACTIVE = RealServerState.STATE_CHOICES.INACTIVE
    _RS_DISABLED = RealServerState.STATE_CHOICES.DISABLED

    @parameterized.expand(
        (
            # when config is not INACTIVE, clean up also won't do anything
            ((_C_ACTIVE,), _VS_INACTIVE, _RS_INACTIVE, _VS_INACTIVE, _RS_INACTIVE),
            ((_C_ACTIVE,), _VS_INACTIVE, _RS_DISABLED, _VS_INACTIVE, _RS_DISABLED),
            ((_C_ACTIVE,), _VS_DISABLED, _RS_INACTIVE, _VS_DISABLED, _RS_INACTIVE),
            ((_C_ACTIVE,), _VS_DISABLED, _RS_DISABLED, _VS_DISABLED, _RS_DISABLED),
            ((_C_ACTIVE,), _VS_OBSOLETED, _RS_INACTIVE, _VS_OBSOLETED, _RS_INACTIVE),
            ((_C_ACTIVE,), _VS_OBSOLETED, _RS_DISABLED, _VS_OBSOLETED, _RS_DISABLED),
            # when vs is not OBSOLETED, clean up won't do anything
            ((_C_INACTIVE,), _VS_INACTIVE, _RS_INACTIVE, _VS_INACTIVE, _RS_INACTIVE),
            ((_C_INACTIVE,), _VS_INACTIVE, _RS_DISABLED, _VS_INACTIVE, _RS_DISABLED),
            ((_C_INACTIVE,), _VS_DISABLED, _RS_INACTIVE, _VS_DISABLED, _RS_INACTIVE),
            ((_C_INACTIVE,), _VS_DISABLED, _RS_DISABLED, _VS_DISABLED, _RS_DISABLED),
            # all prerequisites are met
            ((_C_INACTIVE,), _VS_OBSOLETED, _RS_INACTIVE, _VS_DISABLED, _RS_DISABLED),
            ((_C_INACTIVE,), _VS_OBSOLETED, _RS_DISABLED, _VS_DISABLED, _RS_DISABLED, False),
            ((_C_INACTIVE,), _VS_OBSOLETED, _RS_DISABLED, _VS_DISABLED, None, True),
            # when at least one config is not INACTIVE, clean up also won't do anything
            ((_C_ACTIVE, _C_INACTIVE, _C_INACTIVE), _VS_OBSOLETED, _RS_INACTIVE, _VS_OBSOLETED, _RS_INACTIVE),
            ((_C_ACTIVE, _C_INACTIVE, _C_INACTIVE), _VS_OBSOLETED, _RS_DISABLED, _VS_OBSOLETED, _RS_DISABLED),
            #  all prerequisites are met
            ((_C_INACTIVE, _C_INACTIVE, _C_INACTIVE), _VS_OBSOLETED, _RS_INACTIVE, _VS_DISABLED, _RS_DISABLED),
            ((_C_INACTIVE, _C_INACTIVE, _C_INACTIVE), _VS_OBSOLETED, _RS_DISABLED, _VS_DISABLED, _RS_DISABLED, False),
            ((_C_INACTIVE, _C_INACTIVE, _C_INACTIVE), _VS_OBSOLETED, _RS_DISABLED, _VS_DISABLED, None, True),
        )
    )
    def test_clean_up(self, c_states, vs_state, rs_state, expected_vss, expected_rss, remove_states_history=False):
        self.setStates(c_states[0], vs_state, rs_state)
        svc = Service.objects.get()
        svc.options.remove_states_history = remove_states_history
        self.assertEqual(remove_states_history, svc.options.remove_states_history)
        svc.save(update_fields=["options"])
        vs_ids = [VirtualServer.objects.get().pk]
        for c_state in c_states[1:]:
            Configuration.objects.create(service=svc, vs_ids=vs_ids, description="test", state=c_state)
        lb = LoadBalancer.objects.get()
        tasks._update_vs_and_rs_states(lb)
        vs = VirtualServerState.objects.get()
        self.assertEqual(expected_vss, vs.state)
        rss = RealServerState.objects.all().values_list("state", flat=True)
        if expected_rss is not None:
            self.assertEqual(len(rss), 3)
            self.assertEqual(len(rss.distinct()), 1)
            self.assertEqual(expected_rss, rss.first())
        else:
            self.assertEqual(len(rss), 0)
