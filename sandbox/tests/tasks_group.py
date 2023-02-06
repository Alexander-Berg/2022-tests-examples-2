import pprint
import importlib
import collections

from sandbox import common


def test__task_types_and_resources_uniqueness(tasks_modules):
    task_types = collections.defaultdict(set)
    for module_name in tasks_modules:
        task_module = importlib.import_module(module_name)
        for cls in common.projects_handler.load_task_classes(task_module):
            if cls.type and (cls.__module__ == module_name or getattr(task_module, "__Task__", None) == cls):
                task_types[cls.type].add(".".join([cls.__module__, cls.__name__]))

    duplicated_types = filter(lambda tt: len(tt[1]) > 1, task_types.iteritems())
    assert not duplicated_types, "Task classes with same type: {}".format(pprint.pformat(duplicated_types))
