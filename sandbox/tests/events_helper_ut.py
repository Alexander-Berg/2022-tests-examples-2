import json
import os
import types
import unittest

from sandbox.projects.release_machine.helpers import events_helper
from sandbox.projects.release_machine.components import all as rmc


def get_test_data():
    import yatest.common

    path = os.path.join(
        os.path.dirname(yatest.common.test_source_path()),
        'tests',
        'events_helper_ut_data.json',
    )

    with open(path, 'r') as f:
        data = json.loads(f.read())
    return data


class EventHelperTestCase(unittest.TestCase):

    def setUp(self):

        test_data = get_test_data()

        self._tasks_data = test_data['task_info_objects']['task_info_list_branched_correct']

    def _check_generated_object(self, generator_item):
        self.assertIsInstance(
            generator_item,
            tuple,
            "Event data generator expected to yield tuples but got {}".format(type(generator_item)),
        )
        generator_item_length = len(generator_item)
        self.assertEqual(
            generator_item_length,
            2,
            "Event data generator expected to yield 2 generator_items "
            "(task_info, event_type, rm_event_data), but got {}".format(
                generator_item_length,
            ),
        )

    def _check_defaults(self, task_info, event_type):
        self.assertIsInstance(task_info, types.DictType)
        self.assertIsInstance(event_type, types.StringTypes)

    def test_rm_event_data_generator(self):
        for data in self._tasks_data:
            task_info_list = data['task_info_list']
            c_info = rmc.get_component(data['component_name'])
            generator = events_helper.rm_event_data_by_task_info_generator(c_info, task_info_list)
            self.assertIsInstance(
                generator,
                types.GeneratorType,
                "{name} expected to be a generator but it's a {obj_type}".format(
                    name=events_helper.rm_event_data_by_task_info_generator.__name__,
                    obj_type=type(events_helper.rm_event_data_by_task_info_generator),
                )
            )
            for item in generator:
                self._check_generated_object(item)
                task_info, event_type = item
                self._check_defaults(task_info, event_type)

    def test_updated_rm_event_data_generator(self):
        for data in self._tasks_data:
            task_info_list = data['task_info_list']
            c_info = rmc.get_component(data['component_name'])
            generator = events_helper.updated_rm_event_data_by_task_info_generator(c_info, task_info_list)
            self.assertIsInstance(
                generator,
                types.GeneratorType,
                "{name} expected to be a generator but it's a {obj_type}".format(
                    name=events_helper.rm_event_data_by_task_info_generator.__name__,
                    obj_type=type(events_helper.rm_event_data_by_task_info_generator),
                )
            )
            for item in generator:

                self._check_generated_object(item)

                task_info, event_type = item

                self._check_defaults(task_info, event_type)

                self._check_gsid_info(task_info, event_type, c_info)

    def _check_gsid_info(self, task_info, event_type, c_info):
        gsid_info = events_helper.GSIDInfo(task_info['context.__GSID'])
        gsid_info.upd_svn_info(event_type)
        gsid_info.upd_te_info(c_info)

        self.assertNotEqual(gsid_info.revision, "")
        self.assertIsNotNone(gsid_info.revision)

        self.assertNotEqual(gsid_info.job_name, "")
        self.assertIsNotNone(gsid_info.job_name)

        self.assertNotEqual(gsid_info.scope_number, "")
        self.assertIsNotNone(gsid_info.scope_number)
        self.assertIsInstance(gsid_info.scope_number, types.StringTypes)
        self.assertTrue(gsid_info.scope_number.isdigit())
