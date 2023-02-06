# -*- coding: utf-8 -*-
import logging
import os
import yaml
import sandbox.projects.common.build.parameters as build_parameters

from sandbox import sdk2
from sandbox.sandboxsdk import errors, environments

DCS_HAVING_POWER_TREE = ["IVA", "MANTSALA", "MYT", "SAS", "VLADIMIR"]
DCS_HAVING_AIR_TREE = ["MANTSALA", "SAS", "VLADIMIR"]
DCS_HAVING_AIR_POWER_TREE = ["IVA", "MANTSALA", "MYT", "SAS", "VLADIMIR"]
PATH_PREFIX_POWER = "power"
PATH_PREFIX_AIR = "air"
PATH_PREFIX_AIR_POWER = "air-power"
LIMITS_FILENAME = ".limits.yml"
LIMITS_POWER_MUST_HAVE_KEYS = ["power_limit_kwt"]
LIMITS_AIR_MUST_HAVE_KEYS = ["air_limit_m3h"]
LIMITS_AIR_POWER_MUST_HAVE_KEYS = ["air_power_limit_kwt"]
RACKS_FILENAME = ".racks.yml"


class HaasEngTopologyTestStructDir(sdk2.Task):
    """ Run me to validate power & air topology directories of haas/eng_topology project. """

    _arcadia_path = "arcadia_src"
    _patch_path = "patch_src"

    _param_arcadia_patch_placeholder = "{arcadia_patch}"

    class Parameters(sdk2.Parameters):
        checkout_arcadia_from_url = build_parameters.ArcadiaUrl()
        arcadia_patch = sdk2.parameters.String(
            build_parameters.ArcadiaPatch.description,
            default=build_parameters.ArcadiaPatch.default,
            multiline=True
        )

    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment("PyYAML")
        ]

    @property
    def arcadia_path(self):
        return self.path(self._arcadia_path)

    @property
    def patch_path(self):
        return self.path()

    def pre_execute(self):
        checkout_arcadia_from_url = self.Parameters.checkout_arcadia_from_url
        try:
            checkout_arcadia_from_url = sdk2.svn.Arcadia.freeze_url_revision(checkout_arcadia_from_url)
        except errors.SandboxSvnError as error:
            raise errors.SandboxTaskUnknownError(
                "Arcadia URL {0} does not exist. Error: {1}".format(checkout_arcadia_from_url, error)
            )

        parsed_url = sdk2.svn.Arcadia.parse_url(checkout_arcadia_from_url)
        self.Context.ap_arcadia_revision = parsed_url.revision
        self.Context.ap_arcadia_trunk = parsed_url.trunk
        self.Context.ap_arcadia_branch = parsed_url.branch
        self.Context.ap_arcadia_tag = parsed_url.tag
        self.Context.checkout_arcadia_from_url = checkout_arcadia_from_url

    def on_execute(self):
        logging.info("Hello, Sandbox!")
        self.pre_execute()
        logging.info("self.Context.checkout_arcadia_from_url = {}".format(self.Context.checkout_arcadia_from_url))
        logging.info("self.path = {}".format(self.path()))
        logging.info("self.arcadia_path = {}".format(self.arcadia_path))
        sdk2.svn.Arcadia.checkout(url=self.Context.checkout_arcadia_from_url, path=self.arcadia_path,
                                  revision=self.Context.ap_arcadia_revision)
        logging.info("self.Parameters.arcadia_patch = {}".format(self.Parameters.arcadia_patch))
        if self.Parameters.arcadia_patch and self.Parameters.arcadia_patch != self._param_arcadia_patch_placeholder:
            sdk2.svn.Arcadia.apply_patch(self.arcadia_path, self.Parameters.arcadia_patch, self.patch_path)

        actual_path = self._test_root_path(expected_relative_path="struct")
        self._test_power_struct(actual_path)
        self._test_air_struct(actual_path)
        self._test_air_power_struct(actual_path)

    def get_arcadia_src_dir(self, copy_trunk=False):
        return sdk2.svn.Arcadia.get_arcadia_src_dir(
            self.Context.checkout_arcadia_from_url,
            copy_trunk=copy_trunk,
        )

    def _test_power_struct(self, expected_path):
        logging.info("_test_power_struct() expected_path={}".format(expected_path))
        self._test_datacenters_in_power_tree(expected_path)
        expected_dir = expected_path.joinpath(PATH_PREFIX_POWER)
        logging.info("_test_power_struct() expected_dir={}".format(expected_dir))
        self._test_limits_files(expected_dir, LIMITS_POWER_MUST_HAVE_KEYS)
        self._test_racks_files(expected_dir)

    def _test_air_struct(self, expected_path):
        logging.info("_test_air_struct() expected_path={}".format(expected_path))
        self._test_datacenters_in_air_tree(expected_path)
        expected_dir = expected_path.joinpath(PATH_PREFIX_AIR)
        logging.info("_test_air_struct() expected_dir={}".format(expected_dir))
        self._test_limits_files(expected_dir, LIMITS_AIR_MUST_HAVE_KEYS)
        self._test_racks_files(expected_dir)

    def _test_air_power_struct(self, expected_path):
        logging.info("_test_air_power_struct() expected_path={}".format(expected_path))
        self._test_datacenters_in_air_power_tree(expected_path)
        expected_dir = expected_path.joinpath(PATH_PREFIX_AIR_POWER)
        logging.info("_test_air_power_struct() expected_dir={}".format(expected_dir))
        self._test_limits_files(expected_dir, LIMITS_AIR_POWER_MUST_HAVE_KEYS)
        self._test_racks_files(expected_dir)

    def _test_root_path(self, expected_relative_path):
        expected_path = self.arcadia_path / expected_relative_path
        assert expected_path.is_dir()
        logging.info("expected_path={} is a directory".format(expected_path))

        return expected_path

    def _test_datacenters_in_power_tree(self, expected_path):
        return self._test_datacenters_in_tree(
            expected_path=expected_path,
            dcs_glob="{}/*".format(PATH_PREFIX_POWER),
            expected_dcs=DCS_HAVING_POWER_TREE
        )

    def _test_datacenters_in_air_tree(self, expected_path):
        return self._test_datacenters_in_tree(
            expected_path=expected_path,
            dcs_glob="{}/*".format(PATH_PREFIX_AIR),
            expected_dcs=DCS_HAVING_AIR_TREE
        )

    def _test_datacenters_in_air_power_tree(self, expected_path):
        return self._test_datacenters_in_tree(
            expected_path=expected_path,
            dcs_glob="{}/*".format(PATH_PREFIX_AIR_POWER),
            expected_dcs=DCS_HAVING_AIR_POWER_TREE
        )

    def _test_datacenters_in_tree(self, expected_path, dcs_glob, expected_dcs):
        children_gen = expected_path.glob(dcs_glob)
        children = [_ for _ in children_gen if _.is_dir()]
        logging.info("_test_datacenters_in_tree ({}) children = {}".format(dcs_glob, children))
        datacenters_count = len(children)
        assert datacenters_count >= len(expected_dcs)
        logging.info("_test_datacenters_in_tree ({}) datacenters_count = {}".format(dcs_glob, datacenters_count))
        actual_dcs = [_.name for _ in children]
        logging.info("_test_datacenters_in_tree ({}) actual_dcs = {}".format(dcs_glob, actual_dcs))

        actual_dcs_set = set(actual_dcs)
        for expected_dc in expected_dcs:
            assert expected_dc in actual_dcs_set
            logging.info("_test_datacenters_in_tree ({}) {} found in {}".format(dcs_glob, expected_dc, actual_dcs_set))

        return actual_dcs

    def _test_limits_files(self, expected_path, must_have_keys):
        for dirpath, dirnames, filenames in os.walk(str(expected_path)):
            logging.info("-" * 40)
            dirnames.sort()
            logging.info("_test_limits_files() dirpath={}".format(dirpath))
            logging.info("_test_limits_files() dirnames={}".format(dirnames))
            limits_path = os.path.join(dirpath, LIMITS_FILENAME)
            if os.path.isfile(limits_path):
                logging.info("limits_path={}".format(limits_path))
                with open(limits_path) as f:
                    limits_yml = yaml.load(f)

                    logging.info("yaml loaded, {}".format(type(limits_yml)))
                    logging.info("limits_yml={}".format(limits_yml))
                    assert type(limits_yml) == dict

                    for must_have_key in must_have_keys:
                        logging.info("_test_limits_files() must_have_key={}".format(must_have_key))
                        assert must_have_key in limits_yml

    def _test_racks_files(self, expected_path):
        for dirpath, dirnames, filenames in os.walk(str(expected_path)):
            logging.info("-" * 40)
            dirnames.sort()
            logging.info("_test_racks_files() dirpath={}".format(dirpath))
            logging.info("_test_racks_files() dirnames={}".format(dirnames))
            racks_path = os.path.join(dirpath, RACKS_FILENAME)
            if os.path.isfile(racks_path):
                logging.info("racks_path={}".format(racks_path))
                with open(racks_path) as f:
                    racks_yml = yaml.load(f)

                    logging.info("yaml loaded, {}".format(type(racks_yml)))
                    logging.info("racks_yml={}".format(racks_yml))
                    assert type(racks_yml) == list
