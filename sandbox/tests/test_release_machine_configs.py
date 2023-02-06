from __future__ import print_function

from collections import (
    defaultdict,
    deque,
    Iterable,
)
import functools
import inspect
import unittest
import six

from sandbox.projects.release_machine.core import releasable_items as ri
import sandbox.projects.release_machine.core.const as rm_const
import sandbox.projects.release_machine.components.configs as configs
import sandbox.projects.release_machine.components.config_core.release_block as release_block
import sandbox.projects.release_machine.components.config_core.yappy as yappy_cfg
import sandbox.projects.release_machine.components.configs.all as cfg
import sandbox.projects.release_machine.components.configs.release_machine_test as test_cfg
import sandbox.projects.release_machine.components.config_core.notifications as notifications_config
import sandbox.projects.release_machine.components.job_graph.job_data as jg_job_data
import sandbox.projects.release_machine.components.job_graph.stages.build_stage as jg_build
import sandbox.projects.release_machine.components.job_graph.utils as jg_utils
import sandbox.projects.release_machine.components.job_graph.job_arrows as jg_arrows
import sandbox.projects.release_machine.components.job_graph.job_triggers as jg_job_triggers
import sandbox.projects.release_machine.components.job_graph.stages.release_stage as jg_release

from release_machine.common_proto import events_pb2
from release_machine.release_machine.proto.structures import table_pb2


class TestMergeJobParamsFunction(unittest.TestCase):
    GOOD_CASES = [
        (
            {'key1': {'key2': 'aa'}, 'key3': 'dd'},
            {'key1': {'key2': 'bb', 'key4': 'cc'}},
            {'key1': {'key2': 'aa', 'key4': 'cc'}, 'key3': 'dd'},
        ),
        (
            {"apiargs": {"hidden": False, "requirements": {"platform": "linux"}}},
            {"apiargs": {"requirements": {"disk_space": 123}}},
            {
                "apiargs": {
                    "hidden": False,
                    "requirements": {
                        "platform": "linux",
                        "disk_space": 123,
                    }
                }
            },
        ),
        (
            None,
            None,
            {},
        ),
        (
            {'key1': {'key2': 'aa'}, 'key3': 'dd'},
            None,
            {'key1': {'key2': 'aa'}, 'key3': 'dd'},
        ),
        (
            None,
            {'key1': {'key2': 'aa'}, 'key3': 'dd'},
            {'key1': {'key2': 'aa'}, 'key3': 'dd'},
        )
    ]

    def testGoodCases(self):
        for user_data, default_data, result_data in self.GOOD_CASES:
            merged_data = jg_utils.merge_job_params(user_data, default_data)
            self.assertEqual(
                merged_data,
                result_data,
                "Wrong merge result for user_params: {user_data} and default_params: {default_data}. "
                "Result is {merged_data}, true answer is {result_data}".format(
                    user_data=user_data,
                    default_data=default_data,
                    merged_data=merged_data,
                    result_data=result_data,
                ),
            )


class TestComponentConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg_i_list = [cfg_cls() for cfg_cls in cfg.ALL_CONFIGS.values()]
        cls.cfg_i_te_list = [i for i in cls.cfg_i_list if not isinstance(i, configs.ReferenceCIConfig)]

    def test__component_name_correctness(self):
        for cfg_i in self.cfg_i_list:
            for symbol in cfg_i.name:
                self.assertIn(
                    symbol, rm_const.COMPONENT_NAME_VALID_SYMBOLS,
                    "Got forbidden symbol in component_name [{}]: '{}'. "
                    "Allowed only lower english letters, numbers and underscores".format(cfg_i.name, symbol)
                )

    def test__component_group(self):
        for cfg_i in self.cfg_i_list:

            if isinstance(cfg_i, configs.ReferenceBranchedConfig) or isinstance(cfg_i, configs.ReferenceTaggedConfig):

                self.assertNotEqual(
                    cfg_i.component_group,
                    "component_info_general",
                    "'component_info_general' component group is not suitable for {} config. "
                    "Consider using another component group or removing it completely".format(
                        cfg_i.__class__.__name__,
                    ),
                )

    def _test_change_tests_frequencies(self, cfg_instance):
        frequencies = cfg_instance.testenv_cfg.job_patch.change_frequency
        self.assertIsInstance(
            frequencies, dict,
            "[{}] change_frequency has type {}. Expected dict".format(cfg_instance.name, type(frequencies))
        )
        for test, freq in frequencies.items():
            self.assertTrue(
                type(freq) == dict and "frequency" in freq.keys(),
                "Wrong test frequency {test} in component {component}. "
                "You should use rm_const.TestFrequencies (plural). "
                "Didn't you confuse it with rm_const.TestFrequency?".format(
                    test=test,
                    component=cfg_instance.name
                )
            )

    def _get_supported_event_types(self):
        return [
            f.message_type.name.rpartition('Data')[0]
            for f in events_pb2.EventData.DESCRIPTOR.oneofs_by_name['specific_data'].fields
        ]

    def _get_notification_conditions_join_strategies(self):
        return table_pb2.NotificationCondition.ConditionJoinStrategy.keys()

    def _get_notification_condition_operators(self):
        return table_pb2.NotificationConditionItem.ConditionOperatorType.keys()

    def test_declarative_notifications_correctness(self):

        supported_event_types = self._get_supported_event_types()
        notification_conditions_join_strategies = self._get_notification_conditions_join_strategies()

        for c_name, cfg_cls in cfg.ALL_CONFIGS.items():

            c_cfg = cfg_cls()

            if not c_cfg.notify_cfg.notifications:
                continue

            self.assertIsInstance(
                c_cfg.notify_cfg.notifications,
                Iterable,
                "{} configuration error: `Notify.notifications` setting should be an iterable (e.g., a list)".format(
                    c_name,
                )
            )

            for notification_index, notification in enumerate(c_cfg.notify_cfg.notifications):
                self.assertIsInstance(
                    notification,
                    notifications_config.Notification,
                    self._get_config_notification_error_message(
                        'Incorrect type. `Notification` object expected, got {}'.format(type(notification)),
                        c_name,
                        notification_index,
                    )
                )

                self.assertIn(
                    notification.event_type,
                    supported_event_types,
                    self._get_config_notification_error_message(
                        'Unknown event type "{}". Supported event types: {}'.format(
                            notification.event_type,
                            supported_event_types,
                        ),
                        c_name,
                        notification_index,
                    )
                )

                self.assertIn(
                    notification.conditions.join_strategy,
                    notification_conditions_join_strategies,
                    self._get_config_notification_error_message(
                        'Unknown join strategy "{}". Supported join strategies: {}'.format(
                            notification.conditions.join_strategy,
                            notification_conditions_join_strategies,
                        ),
                        c_name,
                        notification_index,
                    )
                )

                self.assertIsInstance(
                    notification.conditions.conditions,
                    Iterable,
                    self._get_config_notification_error_message(
                        '`{cls_name}.Notify.notifications.conditions.conditions` should be iterable'.format(
                            cls_name=cfg_cls.__name__,
                        ),
                        c_name,
                        notification_index,
                    )
                )

                for condition_index, condition in enumerate(notification.conditions.conditions):

                    self.assertIsInstance(
                        condition.field,
                        six.string_types,
                        self._get_config_notification_error_message(
                            '`{cls_name}.Notify.notifications.conditions.conditions[{condition_index}]` '
                            'should be a string (got {condition_type})'.format(
                                cls_name=cfg_cls.__name__,
                                condition_index=condition_index,
                                condition_type=type(condition),
                            ),
                            c_name,
                            notification_index,
                        )
                    )

                try:
                    notification.to_protobuf()
                except TypeError as te:
                    self.fail(self._get_config_notification_error_message(
                        'Cannot build protobuf message based on this data. '
                        'Please check types. Original error: {}'.format(te),
                        c_name,
                        notification_index,
                    ))

    def _check_notification_condition(self, condition, condition_index, notification_index, c_name):

        for field in ('field', 'operator', 'value'):
            self.assertIsInstance(
                condition.field,
                six.string_types,
                self._get_config_notification_error_message(
                    'Error in condition #{index} `{field}`. String expected, got `{field_type}`'.format(
                        index=condition_index,
                        field=field,
                        field_type=type(condition.field),
                    ),
                    c_name,
                    notification_index,
                )
            )

        self.assertIn(
            condition.operator,
            self._get_notification_condition_operators(),
            self._get_config_notification_error_message(
                'Unknown condition operator "{op}" in condition #{index}. Supported operators: {operators}'.format(
                    op=condition.operator,
                    index=condition_index,
                    operators=self._get_notification_condition_operators(),
                ),
                c_name,
                notification_index,
            )
        )

    def test_config_structure(self):
        for c_name, cfg_cls in cfg.ALL_CONFIGS.iteritems():
            self.assertTrue(
                issubclass(cfg_cls, configs.ReferenceConfig),
                self._get_config_structure_error_message(
                    "`{cfg_cls}` should inherit `ReferenceConfig`",
                    c_name,
                    cfg_cls,
                ),
            )
            self.assertFalse(
                hasattr(cfg_cls, 'JobPatch'),
                self._get_config_structure_error_message("`JobPatch` should be nested in `Testenv`", c_name, cfg_cls),
            )
            self.assertFalse(
                hasattr(cfg_cls, 'Mail'),
                self._get_config_structure_error_message("`Mail` should be nested in `Notify`", c_name, cfg_cls),
            )
            self.assertFalse(
                hasattr(cfg_cls, 'Telegram'),
                self._get_config_structure_error_message("`Telegram` should be nested in `Notify`", c_name, cfg_cls),
            )
            self.assertFalse(
                hasattr(cfg_cls, 'Startrek'),
                self._get_config_structure_error_message("`Startrek` should be nested in `Notify`", c_name, cfg_cls),
            )
            if hasattr(cfg_cls, 'Testenv'):
                self.assertTrue(
                    issubclass(cfg_cls.Testenv, configs.RmTestenvCfg),
                    self._get_config_structure_error_message(
                        "`Testenv` should inherit `RmTestenvCfg`",
                        c_name,
                        cfg_cls,
                    ),
                )

            if hasattr(cfg_cls, 'Yappy'):
                self.assertTrue(
                    issubclass(cfg_cls.Yappy, yappy_cfg.YappyBaseCfg),
                    self._get_config_structure_error_message(
                        "`Yappy` should inherit `YappyBaseCfg`",
                        c_name,
                        cfg_cls,
                    ),
                )

    def test_yappy_configuration(self):
        for c_name, cfg_cls in six.iteritems(cfg.ALL_CONFIGS):

            if not hasattr(cfg_cls, 'Yappy'):
                continue

            cfg_obj = cfg_cls()

            if not cfg_obj.yappy_cfg or not cfg_obj.yappy_cfg.betas:
                continue

            for beta_conf_type, beta_cfg in six.iteritems(cfg_obj.yappy_cfg.betas):

                self.assertIsInstance(
                    beta_conf_type,
                    six.string_types,
                    "Unexpected type of `Yappy.betas` key {} of {}".format(beta_conf_type, cfg_obj.name),
                )

                self.assertIsInstance(
                    beta_cfg,
                    (yappy_cfg.YappyBetaCfg, yappy_cfg.YappyTemplateCfg),
                    "`Yappy.betas` values are expected to be instances of {}, but {} got for {}".format(
                        (yappy_cfg.YappyBetaCfg, yappy_cfg.YappyTemplateCfg),
                        type(beta_cfg),
                        beta_conf_type,
                    ),
                )

    def test_get_release_numbers(self):
        for cfg_i in self.cfg_i_te_list:
            self.assertIsNone(self._test_get_release_numbers_by_url(cfg_i, "arcadia:/trunk/arcadia"))
            if cfg_i.is_branched:
                self._test_change_tests_frequencies(cfg_i)
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom/arcadia@4321234".format(cfg_i.svn_cfg.tag_path(1, 1))
                ))
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom/arcadia".format(cfg_i.svn_cfg.tag_path(1, 1))
                ))
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom/".format(cfg_i.svn_cfg.tag_path(1, 1))
                ))
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom".format(cfg_i.svn_cfg.tag_path(1, 1))
                ))
                self.assertIsNotNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}/arcadia@123456".format(cfg_i.svn_cfg.tag_path(1, 1))
                ))
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom/arcadia".format(cfg_i.svn_cfg.branch_path(2))
                ))
                self.assertIsNotNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}/arcadia@123456".format(cfg_i.svn_cfg.branch_path(2))
                ))
            elif cfg_i.is_tagged:
                self.assertIsNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}-custom/arcadia".format(cfg_i.svn_cfg.tag_path(1))
                ))
                self.assertIsNotNone(self._test_get_release_numbers_by_url(
                    cfg_i, "{}/arcadia@123456".format(cfg_i.svn_cfg.tag_path(1))
                ))
            elif cfg_i.is_trunk:
                self.assertIsNotNone(self._test_get_release_numbers_by_url(cfg_i, "arcadia:/trunk/arcadia@123456"))

    def test_required_attributes(self):
        for cfg_i in self.cfg_i_list:
            common_attrs = [
                (cfg_i, "name"),
                (cfg_i, "responsible"),
                (cfg_i, "release_cycle_type"),
                (cfg_i, "notify_cfg"),
                (cfg_i.svn_cfg, "name"),
                (cfg_i.notify_cfg, "mail"),
                (cfg_i.notify_cfg, "tg"),
                (cfg_i.releases_cfg, "resources_info"),
            ]
            no_trunk_attrs = [
                (cfg_i.svn_cfg, "tag_folder_name"),
                (cfg_i.svn_cfg, "tag_folder_pattern"),
            ]
            branch_attrs = [
                (cfg_i.svn_cfg, "branch_prefix"),
                (cfg_i.svn_cfg, "branch_folder_pattern"),
                (cfg_i.testenv_cfg, "db_template"),
                (cfg_i.testenv_cfg, "trunk_task_owner"),
            ]
            startrek_attrs = [
                (cfg_i.notify_cfg.st, "assignee"),
                (cfg_i.notify_cfg.st, "queue"),
                (cfg_i.notify_cfg.st, "summary_template"),
            ]
            for obj, attr in common_attrs:
                self._check_attr_implemented(obj, attr, cfg_i)
            if not cfg_i.is_trunk:
                for obj, attr in no_trunk_attrs:
                    self._check_attr_implemented(obj, attr, cfg_i)
            if cfg_i.is_branched:
                for obj, attr in branch_attrs:
                    self._check_attr_implemented(obj, attr, cfg_i)
            if cfg_i.notify_cfg.use_startrek:
                for obj, attr in startrek_attrs:
                    self._check_attr_implemented(obj, attr, cfg_i)

    def test_branch_dir(self):
        for cfg_i in self.cfg_i_list:
            if cfg_i.is_branched:
                self.assertIsNotNone(
                    getattr(cfg_i.svn_cfg, "branch_dir", None),
                    "[{}] Component does not have attribute 'branch_dir' in svn_cfg".format(cfg_i.name)
                )
            else:
                self.assertFalse(hasattr(cfg_i.changelog_cfg, "branch_dir"))

    def test_tag_dir(self):
        for cfg_i in self.cfg_i_list:
            if not cfg_i.is_trunk:
                self.assertIsNotNone(
                    getattr(cfg_i.svn_cfg, "tag_dir", None),
                    "[{}] Component does not have attribute 'tag_dir' in svn_cfg".format(cfg_i.name)
                )
            else:
                self.assertFalse(hasattr(cfg_i.changelog_cfg, "tag_dir"))

    def test_start_letter(self):
        for cfg_i in self.cfg_i_list:
            expected_subj = u"[{}] New release process started".format(cfg_i.name)
            rm_link = (
                u"Follow release process in UI: "
                u"<a href=\"https://rm.z.yandex-team.ru/component/{name}/manage\">{name}</a>".format(name=cfg_i.name)
            )
            expected_content = "\n".join([expected_subj, rm_link])
            letter = cfg_i.notify_cfg.mail.get_start_letter()
            self.assertEqual(expected_subj, letter["subject"])
            self.assertEqual(expected_content, letter["body"])
            major_release_num = 1
            revision = 5555555
            st_issue_key = "ISSUE-123"
            expected_subj = u'[{}] New release process started. Major release num: {}. Revision: {}'.format(
                cfg_i.name, major_release_num, revision
            )
            expected_content = u"\n".join([
                (
                    u'[{}] New release process started. Major release num: {}. '.format(cfg_i.name, major_release_num) +
                    u'Revision: <a href="https://a.yandex-team.ru/arc/commit/{rev}">{rev}</a>'.format(rev=revision)
                ),
                rm_link,
                u'Ticket: <a href="https://st.yandex-team.ru/{key}">{key}</a>'.format(key=st_issue_key)
            ])
            letter = cfg_i.notify_cfg.mail.get_start_letter(
                major_release_num=major_release_num,
                revision=revision,
                st_issue_key=st_issue_key,
            )
            self.assertEqual(expected_subj, letter["subject"])
            self.assertEqual(expected_content, letter["body"])

    def test_get_major_release_number(self):
        for cfg_i in self.cfg_i_te_list:
            self.assertEquals(self._test_get_major_release_number_by_url(cfg_i, "arcadia:arc/trunk/arcadia"), 0)
            if cfg_i.is_branched:
                for bad_url in [
                    "{}-custom".format(cfg_i.svn_cfg.branch_path(444)),
                    "{}-custom/".format(cfg_i.svn_cfg.branch_path(333)),
                    "{}-custom/arcadia".format(cfg_i.svn_cfg.branch_path(222)),
                ]:
                    self.assertEquals(self._test_get_major_release_number_by_url(cfg_i, bad_url), 0)
                self.assertEquals(
                    self._test_get_major_release_number_by_url(
                        cfg_i, "{}/arcadia".format(cfg_i.svn_cfg.branch_path(123))
                    ),
                    123
                )

    @staticmethod
    def _check_attr_implemented(obj, attr, cfg_i):
        try:
            getattr(obj, attr)
        except NotImplementedError:
            raise AssertionError("[{}] Object '{}' should have '{}' attr implemented".format(
                cfg_i.name, obj.__class__.__name__, attr
            ))

    @staticmethod
    def _get_config_structure_error_message(msg, c_name, cfg_cls):
        return ("Config structure error for {c_name}: " + msg).format(
            c_name=c_name,
            cfg_cls=cfg_cls,
        )

    @staticmethod
    def _get_config_notification_error_message(msg, c_name, notification_index):
        return "{c_name} configuration error: Incorrect notification #{index}\n{msg}".format(
            c_name=c_name,
            index=notification_index,
            msg=msg,
        )

    def _test_get_major_release_number_by_url(self, cfg_instance, arcadia_url):
        major_release_num = cfg_instance.svn_cfg.get_major_release_num(arcadia_url)
        self.assertIsInstance(major_release_num, int)
        return major_release_num

    def _test_get_release_numbers_by_url(self, cfg_instance, arcadia_url):
        release_numbers = cfg_instance.svn_cfg.get_release_numbers(arcadia_url)
        if release_numbers is not None:
            self.assertIsInstance(
                release_numbers, tuple,
                "[{}] Method get_release_numbers should return tuple, got {}".format(cfg_instance.name, release_numbers)
            )
            self.assertEqual(
                len(release_numbers), 2,
                "[{}] Method get_release_numbers should return tuple of exactly two elements, got {}".format(
                    cfg_instance.name, release_numbers
                )
            )
        return release_numbers

    def test_releasable_items(self):
        # not_switched = []
        for cfg_i in self.cfg_i_list:
            # if not cfg_i.releases_cfg.releasable_items and cfg_i.releases_cfg.resources_info:
            #     not_switched.append(cfg_i.name)
            self._assertIsInstance(cfg_i.releases_cfg.releasable_items, (list, tuple), cfg_i)
            for item in cfg_i.releases_cfg.releasable_items:
                self._assertIsInstance(item, ri.AbstractReleasableItem, cfg_i)
                if isinstance(item, ri.ReleasableItem):
                    self._assertIsInstance(
                        item.data, (ri.SandboxResourceData, ri.DockerImageData), cfg_i
                    )
                elif isinstance(item, ri.DynamicReleasableItem):
                    self._assertIsInstance(
                        item.data, ri.SandboxResourceData, cfg_i
                    )
                if item.deploy_infos is not None:
                    self._assertIsInstance(item.deploy_infos, (list, tuple), cfg_i)
                    for deploy_info in item.deploy_infos:
                        self._assertIsInstance(deploy_info, ri.DeployInfo, cfg_i)
                        for service in deploy_info.services:
                            self._assertIsInstance(service, ri.DeployService, cfg_i)
            self._releasable_items_unique_names(cfg_i.releases_cfg.releasable_items)
        # assert False, len(not_switched)

    def _releasable_items_unique_names(self, releasable_items):
        registered = set()
        for item in releasable_items:
            self.assertNotIn(
                item.name, registered,
                "All releasable items should have unique names. Found duplicate: {}".format(item.name)
            )
            registered.add(item.name)

    def _assertIsInstance(self, obj, cls, cfg_i):
        self.assertIsInstance(
            obj, cls,
            "[{}] {!r} must be an instance of {!r}, got: {}".format(
                cfg_i.name, obj, cls, type(obj)
            )
        )


class TestConfigJobGraph(unittest.TestCase):
    def setUp(self):
        self.cfg_i_list = [cfg_cls() for cfg_cls in cfg.ALL_CONFIGS.values()]
        self.cfg_i_te_list = [i for i in self.cfg_i_list if not isinstance(i, configs.ReferenceCIConfig)]

    def test_job_graph_elements_different_names(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            job_graph_element_names = set()
            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_name = job_graph_element.job_params.get("job_name", "") or rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                self.assertTrue(
                    len(job_name) <= 100,
                    "Job name {} is too big. Names need to be smaller than 100 symbols. (RMDEV-3263)".format(job_name)
                )
                self.assertNotIn(job_name, job_graph_element_names)
                job_graph_element_names.add(job_name)

    @unittest.skip("RMDEV-2623")
    def test_job_graph_build_resources(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            resources_info = defaultdict(set)
            for res in cfg_i.releases_cfg.resources_info:
                resources_info[res.resource_name].add(res.resource_type)
            if cfg_i.releases_cfg.releasable_items:
                for releasable_item in cfg_i.releases_cfg.releasable_items:
                    if releasable_item.name in resources_info:
                        continue
                    if isinstance(releasable_item.data, ri.SandboxResourceData):
                        resources_info[releasable_item.name].add(releasable_item.data.resource_type)

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                if not isinstance(job_graph_element, jg_release.JobGraphElementReleaseBase):
                    continue

                for job_arrow in job_graph_element.job_arrows:
                    if isinstance(job_arrow, jg_job_triggers.JobTriggerBuild):
                        for parent_job_data in job_arrow.parent_job_data:
                            if (
                                isinstance(parent_job_data, jg_job_data.ParentDataDict)
                                and parent_job_data.input_key == "component_resources"
                            ):
                                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                                    job_graph_element.job_params["job_type"],
                                    cfg_i.name,
                                    job_graph_element.job_params.get("job_name_parameter", ""),
                                )
                                self.assertIn(
                                    parent_job_data.dict_key,
                                    resources_info,
                                    "[{name}] got resource_name `{res_name}` from JobGraphElement "
                                    "`{JGE_name}` not in the resources_info list `{resources_info}`".format(
                                        name=cfg_i.name,
                                        res_name=parent_job_data.dict_key,
                                        JGE_name=job_graph_element_name,
                                        resources_info=resources_info,
                                    ),
                                )
                                self.assertIn(
                                    parent_job_data.resource_name,
                                    resources_info[parent_job_data.dict_key],
                                    "[{name}] got resource_type `{res_type}` from JobGraphElement "
                                    "`{JGE_name}` not in the resources_info list `{resources_info}`".format(
                                        name=cfg_i.name,
                                        res_type=parent_job_data.resource_name,
                                        JGE_name=job_graph_element_name,
                                        resources_info=resources_info,
                                    ),
                                )

    def test_job_graph_has_correct_compare_test_task_arrows(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                if "compare_job_triggers" not in job_params:
                    continue

                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                compare_job_triggers = job_params["compare_job_triggers"]
                for trigger in compare_job_triggers:
                    if trigger and isinstance(trigger, jg_arrows.JobTrigger):
                        for job_data in trigger.parent_job_data:
                            trigger_name = rm_const.JobTypes.rm_job_name(
                                trigger.job_type,
                                cfg_i.name,
                                trigger.job_name_parameter,
                            )
                            self.assertTrue(
                                isinstance(job_data, jg_job_data.CompareJobData),
                                "[{name}] Got trigger `{trigger_name}` contains job_data "
                                "which is not an instance of "
                                "`CompareJobData` in JGE `{JGE_name}`".format(
                                    name=cfg_i.name,
                                    trigger_name=trigger_name,
                                    JGE_name=job_graph_element_name,
                                ),
                            )

    def test_job_graph_resource_names_are_not_empty_in_build_package(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                if isinstance(job_graph_element, jg_build.JobGraphElementBuildPackageBranched):
                    self.assertTrue(
                        job_graph_element.job_params["ctx"]["resource_type"],
                        "[{name}] Got resource_names empty in JobGraphElementBuildPackageBranched `{JGE_name}`".format(
                            name=cfg_i.name,
                            JGE_name=job_graph_element_name,
                        ),
                    )

    def test_job_graph_transform(self):
        for cfg_i in self.cfg_i_te_list:
            if cfg_i.name == "quasar_jbl":
                continue

            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                for job_arrow in job_graph_element.job_arrows:
                    if not job_arrow:
                        continue

                    if isinstance(job_arrow, jg_arrows.JobTrigger):
                        job_trigger_name = job_arrow.this_job_name(cfg_i.name)
                        parent_job_data = job_arrow.parent_job_data
                        for job_data in parent_job_data:
                            if job_data:
                                if isinstance(job_data, jg_job_data.ParentDataOutput):
                                    self.assertTrue(
                                        callable(job_data.transform),
                                        "[{name}] Got transform that is not a function in JobGraphElement "
                                        "`{JGE_name}` in trigger `{trigger_name}`".format(
                                            name=cfg_i.name,
                                            JGE_name=job_graph_element_name,
                                            trigger_name=job_trigger_name,
                                        ),
                                    )
                                    if isinstance(job_data.transform, functools.partial):
                                        args_number = (
                                            job_data.transform.func.__code__.co_argcount -
                                            len(job_data.transform.keywords.keys())
                                        )
                                    else:
                                        args_number = job_data.transform.__code__.co_argcount
                                    self.assertTrue(
                                        args_number == 2,
                                        "[{name}] Got {args_num} instead of 2 in transform function in JobGraphElement "
                                        "`{JGE_name}` in trigger `{trigger_name}`".format(
                                            name=cfg_i.name,
                                            args_num=args_number,
                                            JGE_name=job_graph_element_name,
                                            trigger_name=job_trigger_name,
                                        )
                                    )
                    elif type(job_arrow) == jg_arrows.ParentsData or type(job_arrow) == jg_arrows.ParamsData:
                        self.assertTrue(
                            callable(job_arrow.transform),
                            "[{name}] Got transform that is not a function in JobGraphElement "
                            "`{JGE_name}` in {job_arrow_class}".format(
                                name=cfg_i.name,
                                JGE_name=job_graph_element_name,
                                job_arrow_class=(
                                    "ParentsData" if isinstance(job_arrow, jg_arrows.ParentsData) else "ParamsData"
                                ),
                            ),
                        )
                        if isinstance(job_arrow.transform, functools.partial):
                            args_number = (
                                job_arrow.transform.func.__code__.co_argcount -
                                len(job_arrow.transform.keywords.keys())
                            )
                        else:
                            args_number = job_arrow.transform.__code__.co_argcount
                        if isinstance(job_arrow, jg_arrows.ParamsData):
                            self.assertTrue(
                                args_number == 2,
                                "[{name}] Got {args_num} instead of 2 in transform function in JobGraphElement "
                                "`{JGE_name}` in ParamsData".format(
                                    name=cfg_i.name,
                                    args_num=args_number,
                                    JGE_name=job_graph_element_name,
                                )
                            )

    def test_job_graph_transform_no_closure(self):
        for cfg_i in self.cfg_i_te_list:
            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                for job_arrow in job_graph_element.job_arrows:
                    if not job_arrow:
                        continue

                    if isinstance(job_arrow, jg_arrows.JobTrigger):
                        job_trigger_name = job_arrow.this_job_name(cfg_i.name)
                        parent_job_data = job_arrow.parent_job_data
                        for job_data in parent_job_data:
                            if job_data:
                                if isinstance(job_data, jg_job_data.ParentDataOutput):
                                    if isinstance(job_data.transform, functools.partial):
                                        co_freevars = job_data.transform.func.func_code.co_freevars
                                    else:
                                        co_freevars = job_data.transform.func_code.co_freevars
                                    self.assertTrue(
                                        co_freevars == (),
                                        "[{name}] Got transform that has freevars in JobGraphElement `{JGE_name}` "
                                        "in trigger `{trigger_name}`. Freevars are forbidden "
                                        "since RMINCIDENTS-449".format(
                                            name=cfg_i.name,
                                            JGE_name=job_graph_element_name,
                                            trigger_name=job_trigger_name,
                                        ),
                                    )
                    elif isinstance(job_arrow, jg_arrows.ParentsData) or isinstance(job_arrow, jg_arrows.ParamsData):
                        self.assertTrue(
                            job_arrow.transform.func_code.co_freevars == (),
                            "[{name}] Got transform that has freevars `{freevars}` in JobGraphElement `{JGE_name}` in "
                            "`{job_arrow_class}`, `{input_name}`. Freevars are forbidden since RMINCIDENTS-449".format(
                                name=cfg_i.name,
                                freevars=job_arrow.transform.func_code.co_freevars,
                                JGE_name=job_graph_element_name,
                                job_arrow_class=(
                                    "ParentsData" if isinstance(job_arrow, jg_arrows.ParentsData) else "ParamsData"
                                ),
                                input_name=job_arrow.input_key,
                            ),
                        )

    def test_job_graph_arrows_different_input_keys(self):

        ignore = [
            "asr_server",  # RMDEV-2624
        ]

        for cfg_i in self.cfg_i_te_list:

            if cfg_i.name in ignore:
                continue

            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_arrows_input_keys = dict()
                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_graph_element.job_params["job_type"],
                    cfg_i.name,
                    job_graph_element.job_params.get("job_name_parameter", ""),
                )
                for job_arrow in job_graph_element.job_arrows:
                    if not job_arrow:
                        continue
                    if isinstance(job_arrow, jg_arrows.JobTrigger):
                        parent_job_data = job_arrow.parent_job_data
                        for job_data in parent_job_data:
                            if job_data:
                                if isinstance(job_data, jg_job_data.ParentDataDict):
                                    job_data_input_key = job_data.input_key + ":" + job_data.dict_key
                                else:
                                    job_data_input_key = job_data.input_key
                                override = job_data.override
                                if job_data_input_key in job_arrows_input_keys:
                                    if job_arrows_input_keys[job_data_input_key] == override:
                                        job_trigger_name = job_arrow.this_job_name(cfg_i.name)
                                        self.assertNotIn(
                                            job_data_input_key,
                                            job_arrows_input_keys,
                                            "[{name}] Got the same override value `{val}` in JobGraphElement "
                                            "`{JGE_name}` in trigger `{trigger_name}` in {keys}".format(
                                                name=cfg_i.name,
                                                val=job_data_input_key,
                                                JGE_name=job_graph_element_name,
                                                trigger_name=job_trigger_name,
                                                keys=job_arrows_input_keys,
                                            ),
                                        )
                                else:
                                    job_arrows_input_keys[job_data_input_key] = override
                    else:
                        job_arrow_input_key = job_arrow.input_key
                        override = job_arrow.override
                        if job_arrow_input_key in job_arrows_input_keys:
                            if job_arrows_input_keys[job_arrow_input_key] == override:
                                self.assertNotIn(
                                    job_arrow_input_key,
                                    job_arrows_input_keys,
                                    "[{name}] Got the same override value `{val}` in JobGraphElement "
                                    "`{JGE_name}` in {keys}".format(
                                        name=cfg_i.name,
                                        val=job_arrow_input_key,
                                        JGE_name=job_graph_element_name,
                                        keys=job_arrows_input_keys,
                                    ),
                                )
                        else:
                            job_arrows_input_keys[job_arrow_input_key] = override
                if "ctx" in job_graph_element.job_params:
                    job_graph_element_ctx = job_graph_element.job_params["ctx"] or {}
                    for ctx_element in job_graph_element_ctx:
                        self.assertNotIn(
                            ctx_element,
                            job_arrows_input_keys,
                            "[{name}] Got the same override value in ctx `{val}` in {keys}".format(
                                name=cfg_i.name,
                                val=ctx_element,
                                keys=job_arrows_input_keys,
                            ),
                        )

    def test_check_all_branch_jobs_dont_use_filter_targets(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                should_add_to_db = job_params.get("should_add_to_db", "")
                if should_add_to_db and should_add_to_db is jg_utils.should_add_to_db_branch:
                    job_graph_element_name = rm_const.JobTypes.rm_job_name(
                        job_params["job_type"],
                        cfg_i.name,
                        job_params.get("job_name_parameter", ""),
                    )
                    self.assertFalse(
                        job_params.get("filter_targets", ""),
                        "[{name}] got `filter_targets` in job_params in JobGraphElement `{JGE_name}`. This flag "
                        "doesn't work in branch bases in Testenv, you should remove it from JobGraph config. "
                        "More details at "
                        "https://wiki.yandex-team.ru/releasemachine/faq/#checkallbranchjobsdontusefiltertargets".format(
                            name=cfg_i.name,
                            JGE_name=job_graph_element_name,
                        ),
                    )

    def test_check_notifications_in_apiargs(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                notifications = job_params.get("apiargs", {}).get("notifications", [])
                if notifications:
                    job_graph_element_name = rm_const.JobTypes.rm_job_name(
                        job_params["job_type"],
                        cfg_i.name,
                        job_params.get("job_name_parameter", ""),
                    )
                    self.assertTrue(
                        isinstance(notifications, list),
                        "[{name}] got bad `notifications` in job_params['apiargs'] in JobGraphElement `{JGE_name}`. "
                        "This object should be list with dicts, i.e. 'notifications': [{{"
                        "'transport': jg_utils.TaskNotifications.Transport.EMAIL,"
                        "'statuses': [jg_utils.TaskStatus.SUCCESS, jg_utils.TaskStatus.FAILURE],"
                        "'recipients': [CURRENT_PERSON_ON_DUTY],"
                        "}}, ...], please fix it.".format(
                            name=cfg_i.name,
                            JGE_name=job_graph_element_name,
                        ),
                    )
                    self.assertTrue(
                        all([isinstance(notification, dict) for notification in notifications]),
                        "[{name}] got bad `notifications` in job_params['apiargs'] in JobGraphElement `{JGE_name}`. "
                        "Some elements in `notifications` are not dicts, please fix it. "
                        "All `notification` elements should look like {{"
                        "'transport': jg_utils.TaskNotifications.Transport.EMAIL,"
                        "'statuses': [jg_utils.TaskStatus.SUCCESS, jg_utils.TaskStatus.FAILURE],"
                        "'recipients': [CURRENT_PERSON_ON_DUTY],"
                        "}}.".format(
                            name=cfg_i.name,
                            JGE_name=job_graph_element_name,
                        ),
                    )

    def test_check_should_add_to_db_correctness(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                should_add_to_db = job_params.get("should_add_to_db", "")
                frequency = job_params.get("frequency", "")
                if should_add_to_db:
                    if isinstance(should_add_to_db, dict) or isinstance(frequency, dict):
                        job_graph_element_name = rm_const.JobTypes.rm_job_name(
                            job_params["job_type"],
                            cfg_i.name,
                            job_params.get("job_name_parameter", ""),
                        )
                        self.assertIsInstance(
                            frequency, dict,
                            "[{name}] got `should_add_to_db` as dict and `frequency` not dict in JobGraphElement "
                            "`{JGE_name}`. If you one of this parameters is dict with fields `trunk` and `branch`, "
                            "so the other should be dict too.".format(
                                name=cfg_i.name,
                                JGE_name=job_graph_element_name,
                            ),
                        )

                        self.assertIsInstance(
                            should_add_to_db, dict,
                            "[{name}] got `frequency` as dict and `should_add_to_db` not dict in JobGraphElement "
                            "`{JGE_name}`. If you one of this parameters is dict with fields `trunk` and `branch`, "
                            "so the other should be dict too.".format(
                                name=cfg_i.name,
                                JGE_name=job_graph_element_name,
                            ),
                        )

                        self.assertTrue(
                            "trunk" in frequency and "branch" in frequency,
                            "[{name}] `frequency` parameter should be a dict with keys `trunk` and `branch` in "
                            "JobGraphElement `{JGE_name}`.".format(
                                name=cfg_i.name,
                                JGE_name=job_graph_element_name,
                            ),
                        )

                        self.assertTrue(
                            "trunk" in frequency and "branch" in should_add_to_db,
                            "[{name}] `should_add_to_db` parameter should be a dict with keys `trunk` and `branch` "
                            "in JobGraphElement `{JGE_name}`.".format(
                                name=cfg_i.name,
                                JGE_name=job_graph_element_name,
                            ),
                        )

    def test_all_jg_elements_are_not_empty(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                self.assertTrue(
                    job_graph_element,
                    "[{name}] got empty JobGraphElement that is forbidden. "
                    "Please don't add empty elements in JobGraph, just skip them.".format(
                        name=cfg_i.name,
                    ),
                )

    def test_observed_paths_in_jg_prerelease_if_using_arc(self):
        failed_component_names = []

        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.is_branched or not cfg_i.svn_cfg.use_arc:
                continue

            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for jge in cfg_i.testenv_cfg.job_graph.graph:
                job_name = jge.construct_job_name(cfg_i.name)

                if "ACTION_PRE_RELEASE" in job_name:
                    observed_paths = jge.job_params.get("observed_paths")
                    if not observed_paths:
                        failed_component_names.append(cfg_i.name)
                        break

        self.assertFalse(
            failed_component_names,
            "ACTION_PRE_RELEASE job should have `arcadia` in observed_paths in case `use_arc` is enabled.\n"
            "Broken components: {}".format(
                ", ".join(failed_component_names),
            ),
        )

    def test_log_merge_not_in_jg_if_not_using_startrek(self):

        failed_component_names = []

        for cfg_i in self.cfg_i_te_list:

            if cfg_i.notify_cfg.use_startrek:
                continue

            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for jge in cfg_i.testenv_cfg.job_graph.graph:

                job_name = jge.construct_job_name(cfg_i.name)

                if "_LOG_MERGE__" in job_name:
                    failed_component_names.append(cfg_i.name)
                    break

        self.assertFalse(
            failed_component_names,
            "_LOG_MERGE__... should not appear in job graphs of the following components "
            "since the do not use Tracker: {}".format(
                ", ".join(failed_component_names),
            ),
        )

    def test_compare_jobs_are_diff(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                if "compare_task_name" in job_params:
                    job_graph_element_name = rm_const.JobTypes.rm_job_name(
                        job_params["job_type"],
                        cfg_i.name,
                        job_params.get("job_name_parameter", ""),
                    )
                    self.assertTrue(
                        job_params.get("test_type", jg_utils.TestType.CHECK_TEST) == jg_utils.TestType.DIFF_TEST,
                        "[{name}] Got JobGraphElement `{JGE_name}` with `CompareTaskName` "
                        "but test_type != DIFF_TEST. You should change test_type to DIFF_TEST.".format(
                            name=cfg_i.name,
                            JGE_name=str(job_graph_element_name),
                        ),
                    )

    def test_frequencies_are_tuples(self):
        for cfg_i in self.cfg_i_te_list:
            if not cfg_i.testenv_cfg.job_graph or not cfg_i.testenv_cfg.job_graph.graph:
                continue

            for job_graph_element in cfg_i.testenv_cfg.job_graph.graph:
                job_params = job_graph_element.job_params
                job_graph_element_name = rm_const.JobTypes.rm_job_name(
                    job_params["job_type"],
                    cfg_i.name,
                    job_params.get("job_name_parameter", ""),
                )
                if "frequency" in job_params:
                    common_msg = "[{}] got JobGraphElement '{}' with `frequency` '{}'. ".format(
                        cfg_i.name, job_graph_element_name, job_params["frequency"]
                    )
                    if isinstance(job_params["frequency"], dict):
                        self._check_correct_frequency(job_params["frequency"]["trunk"], common_msg)
                        self._check_correct_frequency(job_params["frequency"]["branch"], common_msg)
                    else:
                        self._check_correct_frequency(job_params["frequency"], common_msg)

    def _check_correct_frequency(self, frequency, common_msg):
        self.assertTrue(len(frequency) == 2, common_msg + "Frequency should be tuple with two elements.")
        self.assertIsInstance(
            frequency[0], jg_utils.TestFrequency,
            common_msg + "Frequency should be an instance of 'jg_utils.TestFrequency', got {}".format(frequency[0])
        )

    def test_release_block_types(self):
        for cfg_i in self.cfg_i_list:
            for block in cfg_i.releases_cfg.block_on_test_results:
                self.assertIsInstance(block, release_block.BlockConfBase)


class TestTestenv(unittest.TestCase):
    def test_loadable_configs(self):
        all_configs = cfg.ALL_CONFIGS
        for c_name in ["base", "begemot", "cores", "release_machine", "report"]:
            self.assertIn(c_name, all_configs, "Missing Autoloaded config {}".format(c_name))

    def test_ignoring_changelog_revisions(self):
        rev_data1 = {
            "revision": 1,
            "author": "author",
            "date": "date",
            "msg": "rev1",
            "paths": [
                ("A", "/trunk/arcadia/desired/path/file"),
            ],
        }
        rev_data2 = {
            "revision": 2,
            "author": "author",
            "date": "date",
            "msg": "rev2",
            "paths": [
                ("M", "/trunk/arcadia/desired/path/file1"),
                ("M", "/trunk/arcadia/desired/path/file2"),
                ("A", "/trunk/arcadia/some/other/path/file"),
            ],
        }
        rev_data3 = {
            "revision": 3,
            "author": "author",
            "date": "date",
            "msg": "rev3",
            "paths": [
                ("M", "/trunk/arcadia/undesired/path/file"),
                ("A", "/trunk/arcadia/some/other/path/file"),
            ],
        }
        rev_data4 = {
            "revision": 4,
            "author": "author",
            "date": "date",
            "msg": "rev4",
            "paths": [
                ("M", "/trunk/arcadia/undesired/path/file1"),
                ("M", "/trunk/arcadia/undesired/path/file2"),
            ],
        }
        rev_data5 = {
            "revision": 5,
            "author": "author",
            "date": "date",
            "msg": "rev5",
            "paths": [
                ("M", "/branches/qq/stable-111/arcadia/undesired/path/file1"),
            ],
        }
        cfg_i = test_cfg.ReleaseMachineTestCfg()

        self.assertFalse(cfg_i.changelog_cfg.should_skip_revision(rev_data1))
        cfg_i.changelog_cfg.svn_paths_filter = configs.ChangelogPathsFilter(
            rm_const.PermissionType.ALLOWED, ["arcadia/desired/path"]
        )
        self.assertFalse(cfg_i.changelog_cfg.should_skip_revision(rev_data1))
        self.assertFalse(cfg_i.changelog_cfg.should_skip_revision(rev_data2))
        self.assertTrue(cfg_i.changelog_cfg.should_skip_revision(rev_data3))
        cfg_i.changelog_cfg.svn_paths_filter = configs.ChangelogPathsFilter(
            rm_const.PermissionType.BANNED, ["arcadia/undesired/path"]
        )
        self.assertFalse(cfg_i.changelog_cfg.should_skip_revision(rev_data3))
        self.assertTrue(cfg_i.changelog_cfg.should_skip_revision(rev_data4))
        self.assertTrue(cfg_i.changelog_cfg.should_skip_revision(rev_data5))

    def test_set_paths_importance(self):
        path1 = "/trunk/arcadia/some/other/path"
        path2 = "/trunk/arcadia/desired/path/file.txt"
        path3 = "/branches/qq/stable-111/arcadia/undesired/path/file1"
        path4 = "/trunk/arcadia/very/important/path"
        path5 = "/trunk/arcadia/undesired/path/subpath/file"
        cfg_i = test_cfg.ReleaseMachineTestCfg()
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path1),
            (1, "arcadia/some/other/path")
        )
        cfg_i.changelog_cfg.svn_paths_filter = configs.ChangelogPathsFilter(
            rm_const.PermissionType.ALLOWED, ["arcadia/desired/path"]
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path1),
            (0, "arcadia/some/other/path")
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path2),
            (1, "arcadia/desired/path/file.txt")
        )
        cfg_i.changelog_cfg.svn_paths_filter = configs.ChangelogPathsFilter(
            rm_const.PermissionType.BANNED, ["arcadia/undesired/path"]
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path1),
            (1, "arcadia/some/other/path")
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path3),
            (0, "arcadia/undesired/path/file1")
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path5),
            (0, "arcadia/undesired/path/subpath/file")
        )
        cfg_i.changelog_cfg.svn_paths_filter = configs.ChangelogPathsFilter(
            rm_const.PermissionType.CHANGED, ["arcadia/very/important/path"], importance=6
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path1),
            (1, "arcadia/some/other/path")
        )
        self.assertEquals(
            cfg_i.changelog_cfg.set_paths_importance(path4),
            (6, "arcadia/very/important/path")
        )

    def test_ignored_jobs_redefine(self):
        should_be_ignored = (
            "MERGE_FUNCTIONAL",
            "ROLLBACK_TRUNK_AND_MERGE_FUNCTIONAL",
            "ROLLBACK_TRUNK_FUNCTIONAL"
        )
        should_not_be_ignored = (
            "HYPOTHETICAL_NOT_IGNORED_JOB",
        )
        cfg_instance = test_cfg.ReleaseMachineTestCfg()
        really_ignored = cfg_instance.testenv_cfg.job_patch.ignore_match
        name = cfg_instance.testenv_cfg.job_patch.name
        for i in should_be_ignored:
            self.assertIn(i.format(name), really_ignored)
        for i in should_not_be_ignored:
            self.assertNotIn(i.format(name), really_ignored)


class TestConfigGeneralRequirements(unittest.TestCase):

    FORBIDDEN_DEPENDENCIES = ['sandbox.sdk2']

    def traverse_bfs(self, node, forbidden_list, max_depth=7):
        queue = deque([(node, 0)])
        seen = set([])
        while queue:
            current, depth = queue.popleft()
            if depth > max_depth:
                continue
            for name, member in inspect.getmembers(current, lambda obj: not inspect.isbuiltin(obj)):
                if name.startswith('__'):
                    continue
                module = inspect.getmodule(member)
                if (not module) or not hasattr(module, '__file__'):
                    continue
                try:
                    path = inspect.getabsfile(module)
                except TypeError:
                    continue
                if path in seen or 'venv/lib/python' in path:
                    continue
                seen.add(path)
                if module.__name__ in forbidden_list:
                    self.fail(
                        u"Forbidden dependency: {module}.\n"
                        u"`{node}` should not import the following properties neither directly nor implicitly: "
                        u"{forbidden_list}"
                        u"\n".format(
                            module=module,
                            node=node.__name__,
                            forbidden_list=forbidden_list,
                        )
                    )
                queue.append((module, depth + 1))

    def test_no_forbidden_dependencies_present(self):
        self.traverse_bfs(configs, self.FORBIDDEN_DEPENDENCIES)


if __name__ == '__main__':
    unittest.main()
