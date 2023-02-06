import itertools
import logging
import typing
from collections import defaultdict
from http import HTTPStatus
from unittest.mock import patch

from django import test
from django.db.models import Func, F
from django.db.models import Q
from parameterized import parameterized

from l3common.typing import alias
from ... import models
from ...tests import test_fields
from ...utils import validate_lbs_helpers
from ...utils.validate_config_helpers import ConfigVersionValidator, PreconditionFailureError

logger: logging.Logger = logging.getLogger(__name__)

DUMMY_SVC_ID: int = 94


class FakeRequest:
    if_match_header_value = None

    @property
    def headers(self):
        return {ConfigVersionValidator.IF_MATCH_HEADER: self.if_match_header_value}


def fake_request_with_if_match_header(if_match_header_value):
    request = FakeRequest()
    request.if_match_header_value = if_match_header_value

    return request


class ConfigVersionValidationTest(test.SimpleTestCase):
    @parameterized.expand(
        [
            (fake_request_with_if_match_header("cfg_id=`1`"), None, None, False),
            (fake_request_with_if_match_header("cfg_id=0"), None, None, False),
            (fake_request_with_if_match_header("cfg_id=123,456"), None, None, False),
            (fake_request_with_if_match_header("cfg_id=id"), None, None, False),
            (fake_request_with_if_match_header("cfg_id=-1"), None, None, False),
            (fake_request_with_if_match_header("abc"), None, None, False),
            (fake_request_with_if_match_header("123"), None, None, False),
            (fake_request_with_if_match_header("cfg_id=123"), None, [], True),
            (fake_request_with_if_match_header("cfg_id=123"), 456, [], True),
        ]
    )
    def test_config_version_validation_success_case(self, fake_request, exclude_cfg_id, found_cfg_ids, expect_db_call):
        with patch("l3mgr.utils.validate_config_helpers.Configuration.objects.filter") as mocked_db_call:
            mocked_db_call.return_value.values_list.return_value = found_cfg_ids
            version_validator = ConfigVersionValidator(DUMMY_SVC_ID, fake_request, exclude_cfg_id)

            self.assertEqual(version_validator.validate(), None)

            if expect_db_call:
                mocked_db_call.assert_called_once_with(
                    ~Q(pk=exclude_cfg_id), service_id=DUMMY_SVC_ID, id__gt=version_validator.cfg_id
                )

    @parameterized.expand(
        [
            (fake_request_with_if_match_header("cfg_id=123"), 456, [456, 789]),
            (fake_request_with_if_match_header("cfg_id=123"), None, [456]),
        ]
    )
    def test_config_version_validation_failure_case(self, fake_request, exclude_cfg_id, found_cfg_ids):
        with patch("l3mgr.utils.validate_config_helpers.Configuration.objects.filter") as mocked_db_call:
            mocked_db_call.return_value.values_list.return_value = found_cfg_ids

            with self.assertRaises(PreconditionFailureError) as cm:
                ConfigVersionValidator(DUMMY_SVC_ID, fake_request, exclude_cfg_id).validate()

            self.assertEqual(cm.exception.error_code, HTTPStatus.PRECONDITION_FAILED)


class LbValidationTestCase(test.TestCase):
    def setUp(self) -> None:
        self.service: models.Service = models.Service.objects.create(fqdn="test.localhost", abc="dostavkatraffika")

        self.regions: typing.Dict[
            models.LocationRegion.REGION_CHOICES, typing.List[models.LocationNetwork.LOCATION_CHOICES]
        ] = {r.code: sorted(r.location) for r in models.LocationRegion.objects.all()}

        locations: typing.List[models.LocationNetwork.LOCATION_CHOICES] = sorted(
            itertools.chain.from_iterable(self.regions.values())
        )

        self.rss: typing.Dict[models.LocationNetwork.LOCATION_CHOICES, models.RealServer] = {
            r.location[0]: r
            for r in models.RealServer.objects.bulk_create(
                [
                    models.RealServer(
                        fqdn=f"{location.lower()}-{idx}.yandex.net",
                        ip=f"2a02:6b8:0:1482::{idx}",
                        config={},
                        location=[location],
                    )
                    for idx, location in enumerate(locations)
                ]
            )
        }

        self.vss = []

        with alias(models.LocationNetwork.LOCATION_CHOICES) as L:
            sas_lb = models.LoadBalancer(
                fqdn=f"{L.SAS}.yndx.net", location=[L.SAS], state=models.LoadBalancer.STATE_CHOICES.ACTIVE
            )
            iva_lb = models.LoadBalancer(
                fqdn=f"{L.IVA}.yndx.net", location=[L.IVA], state=models.LoadBalancer.STATE_CHOICES.ACTIVE
            )

            self.lbs: typing.Dict[L, models.LoadBalancer] = {L.SAS: sas_lb, L.IVA: iva_lb}
            vs_regional: models.VirtualServer = self.make_vs(L.IVA)
            vs_locational: models.VirtualServer = self.make_vs(L.SAS, DC_FILTER=True)

        models.LoadBalancer.objects.bulk_create(self.lbs.values())
        models.LoadBalancerAccess.objects.bulk_create(
            [models.LoadBalancerAccess(balancer=lb, abc=self.service.abc) for lb in [sas_lb, iva_lb]]
        )

        self.config: models.Configuration = models.Configuration.objects.create(
            service=self.service, vs_ids=[vs_regional.id, vs_locational.id]
        )

    @property
    def cfg_id(self):
        return self.config.id

    @property
    def lb_ids(self):
        return [lb.id for lb in self.lbs.values()]

    def make_vs(self, *args: models.LocationNetwork.LOCATION_CHOICES, **kwargs) -> models.VirtualServer:
        self.assertGreater(len(args), 0)
        idx: int = len(self.vss)
        vs: models.VirtualServer = models.VirtualServer.objects.create(
            service=self.service,
            ip=f"2a02:6b8:b040:3100:ccc::{idx}",
            port=idx,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            config=test_fields.make_config(ANNOUNCE=True, **kwargs),
            rs_ids=[self.rss[location].id for location in args],
        )
        self.vss.append(vs)
        return vs

    def test_vs_without_lbs_validation_because_of_absent_access(self) -> None:
        deleted, _ = models.LoadBalancerAccess.objects.filter(
            balancer=self.lbs[models.LocationNetwork.LOCATION_CHOICES.SAS]
        ).delete()
        self.assertEqual(1, deleted)

        self._test_vs_without_lbs_validation()

    def test_vs_without_lbs_validation_because_of_agent_on_lb(self) -> None:
        models.AllowUsedByMachineFeature.objects.create(balancer=self.lbs[models.LocationNetwork.LOCATION_CHOICES.SAS])

        self._test_vs_without_lbs_validation()

    def _test_vs_without_lbs_validation(self) -> None:
        presentations = self.config.prepare_presentations()
        self.assertEqual(1, len(presentations))

        used_vss_ids: typing.Set[int] = set(itertools.chain.from_iterable(p.data.keys() for p in presentations))
        self.assertEqual(1, len(used_vss_ids))
        unused_vss_ids: typing.Set[int] = set(self.config.vs_ids) - used_vss_ids
        self.assertEqual(1, len(unused_vss_ids))

        with self.assertRaises(
            validate_lbs_helpers.UnallocatedVsError,
            msg=f"Not all vs were allocated for CFG#{self.cfg_id}: {sorted(unused_vss_ids)}",
        ):
            validate_lbs_helpers.validate_lbs(self.config, presentations, logger)

    def test_lbs_validation_because_of_agent_on_lb_with_dsm(self) -> None:
        self.service.options.dsm = True
        self.service.options.dsm_mode = models.Service.Options.DsmMode.SOLELY
        self.service.save()
        models.AllowUsedByMachineFeature.objects.create(balancer=self.lbs[models.LocationNetwork.LOCATION_CHOICES.SAS])

        presentations = self.config.prepare_presentations()
        self.assertEqual(2, len(presentations))

        with self.assertRaises(
            validate_lbs_helpers.InvalidLbError,
            msg=f"Only balancers with agents should be used for CFG#{self.cfg_id}: {[self.lbs[models.LocationNetwork.LOCATION_CHOICES.IVA].fqdn]}",
        ):
            validate_lbs_helpers.validate_lbs(self.config, presentations, logger)

    @patch("l3mgr.utils.validate_lbs_helpers.create_tasklog_for_config_id_with_message")
    @patch("l3mgr.utils.validate_lbs_helpers.MAX_NUMBER_OF_LOGGING_RECORDS", 4)
    def test_log_rs_matching_lbs_location(self, mocked_create_tasklog_for_config_id_with_message) -> None:
        """
        Test validate LBs when locations of RSs don't match locations of LBs
        """

        # Set RS location tha same as LB location
        rs_ids: typing.Set[int] = set(self.config.get_rss_ids())
        lb_locations: typing.List[models.LocationNetwork.LOCATION_CHOICES] = self.lbs[
            models.LocationNetwork.LOCATION_CHOICES.SAS
        ].location
        self.assertListEqual([models.LocationNetwork.LOCATION_CHOICES.SAS], lb_locations)
        updated: int = models.RealServer.objects.filter(id__in=rs_ids).update(location=lb_locations)
        self.assertEqual(2, updated)

        validate_lbs_helpers.validate_lbs_callback(self.cfg_id, self.lb_ids, logger)
        mocked_create_tasklog_for_config_id_with_message.assert_not_called()

    @patch("l3mgr.utils.validate_lbs_helpers.create_tasklog_for_config_id_with_message")
    @patch("l3mgr.utils.validate_lbs_helpers.MAX_NUMBER_OF_LOGGING_RECORDS", 4)
    def test_log_rs_not_matching_lbs_location(self, mocked_create_tasklog_for_config_id_with_message) -> None:
        """
        Test validate LBs when locations of RSs don't match locations of LBs
        """

        # Set RS location not overlapping with any existing locations
        vs_ids: typing.List[int] = self.config.vs_ids
        rs_ids: typing.Set[int] = set(
            models.VirtualServer.objects.filter(pk__in=vs_ids)
            .annotate(rs_id=Func(F("rs_ids"), function="UNNEST"))
            .values_list("rs_id", flat=True)
        )
        updated: int = models.RealServer.objects.filter(id__in=rs_ids).update(
            location=[models.LocationNetwork.LOCATION_CHOICES.VLA]
        )
        self.assertEqual(len(rs_ids), updated)

        # RS location doesn't match LB location
        with self.assertRaises(validate_lbs_helpers.RsNotMatchingLbsLocationError):
            validate_lbs_helpers.validate_lbs_callback(self.cfg_id, self.lb_ids, logger)

        amount_of_rs_matching_lb_location: int = len(
            validate_lbs_helpers.real_servers_with_location_not_matching_any_lb_location(self.lb_ids, rs_ids)
        )

        self.assertEqual(amount_of_rs_matching_lb_location, mocked_create_tasklog_for_config_id_with_message.call_count)

    def test_inactive_lbs_case(self) -> None:
        """
        Test validate LBs when balancers are inactive
        """
        for lb_id in self.lb_ids:
            updated = models.LoadBalancer.objects.filter(id=lb_id).update(
                state=models.LoadBalancer.STATE_CHOICES.INACTIVE, fqdn="lb_fqdn" + str(lb_id)
            )
            self.assertEqual(1, updated)

        # todo: this test looks wierd. what should we expect here?
        validate_lbs_helpers.validate_lbs_callback(self.cfg_id, self.lb_ids, logger)

    def test_no_vs_ids(self) -> None:
        """
        Test validate LBs when there is no vs_ids for config
        """
        models.Configuration.objects.filter(pk=self.cfg_id).update(vs_ids=[])
        validate_lbs_helpers.validate_lbs_callback(self.cfg_id, self.lb_ids, logger)

    def test_no_rs_ids(self) -> None:
        """
        Test validate LBs when there is no rs_ids for vs_ids used in config
        """
        self.config.vss.update(rs_ids=[])
        validate_lbs_helpers.validate_lbs_callback(self.cfg_id, self.lb_ids, logger)

    def test_validate_no_missing_lbs_in_config(self) -> None:
        """
        Test missing lbs in config and vss have no announce set
        """
        with self.assertRaises(
            validate_lbs_helpers.MissingLBsInConfigError, msg=f"There are no LBs for CFG#{self.cfg_id}"
        ):
            validate_lbs_helpers.validate_lbs_callback(self.cfg_id, [], logger)

    @patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list))
    def test_validate_any_vs_has_announce_setting(self, mock) -> None:
        """
        Test missing lbs in config and vss have no announce set
        """

        for vs_id in self.config.vs_ids:
            vs: models.VirtualServer = models.VirtualServer.objects.get(pk=vs_id)
            vs.config["ANNOUNCE"] = False
            vs.save()

        with self.assertRaises(
            validate_lbs_helpers.ValidationResult.NoVSsWithAnnounceError,
            msg=(
                f"There are no VSs among {self.config.vs_ids} with 'ANNOUNCE=True' setting for CFG #{self.cfg_id}."
                f" VS IP would never be announced"
            ),
        ):
            validate_lbs_helpers.validate_configuration(self.config)
