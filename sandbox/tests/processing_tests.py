from __future__ import absolute_import

import pytest

from .api_tests import MongoTestCase
from ..event_processing import action_should_be_scheduled
from ..models.action_config import is_free
from ..models import Event, EventDep, ActionConfig


class FakeRecord(dict):
    def __getattr__(self, item):
        return self.get(item)

    def free_params(self):
        params = []
        for ev_dep in self.event_deps:
            for k, v in ev_dep.params.items():
                if is_free(v):
                    params.append(k)
        return params


@pytest.mark.xfail(run=False)
class ProcessingTestCase(MongoTestCase):

    def test_simple_run(self):
        r = action_should_be_scheduled(
            ActionConfig(
                task_params={
                    'action_id': 'external:stjob-regular/test_action',
                },
                event_deps=[
                    EventDep(
                        name='test_event',
                        params={
                            'param1': 'value1',
                            'param2': None
                        }
                    )
                ]
            ),
            Event(
                name='test_event',
                params={
                    'param1': 'value1',
                    'param2': 'value2'
                }
            ),
            Event.objects
        )
        self.assertDictEqual(r['params'], {'param2': 'value2'})

    def test_wrong_param(self):
        r = action_should_be_scheduled(
            ActionConfig(
                task_params={
                    'action_id': 'external:stjob-regular/test_action',
                },
                event_deps=[
                    EventDep(
                        name='test_event',
                        params={
                            'param1': 'value1',
                            'param2': None
                        }
                    )
                ]
            ),
            Event(
                name='test_event',
                params={
                    'param1': 'value01',
                    'param2': 'value2'
                }
            ),
            Event.objects
        )
        self.assertFalse(r['should_be_scheduled'])

    def test_two_deps_one_lost(self):
        r = action_should_be_scheduled(
            ActionConfig(
                task_params={
                    'action_id': 'external:stjob-regular/test_action',
                },
                event_deps=[
                    EventDep(
                        name='test_event_1',
                        params={
                            'param1': 'value1',
                            'param2': None
                        }
                    ),
                    EventDep(
                        name='test_event_2',
                        params={}
                    )
                ]
            ),
            Event(
                name='test_event_1',
                params={
                    'param1': 'value1',
                    'param2': 'value2'
                }
            ),
            Event.objects
        )
        self.assertFalse(r['should_be_scheduled'])

    def test_two_deps(self):
        Event(
            name='test_event_2',
            params={
                'param2': 'value2'
            }
        ).save()

        r = action_should_be_scheduled(
            ActionConfig(
                task_params={
                    'action_id': 'external:stjob-regular/test_action',
                },
                event_deps=[
                    EventDep(
                        name='test_event_1',
                        params={
                            'param1': 'value1',
                            'param2': None
                        }
                    ),
                    EventDep(
                        name='test_event_2',
                        params={
                            'param2': None
                        }
                    )
                ]
            ),
            Event(
                name='test_event_1',
                params={
                    'param1': 'value1',
                    'param2': 'value2'
                }
            ),
            Event.objects
        )
        self.assertDictEqual(r['params'], {'param2': 'value2'})

    def test_real_postprocessing(self):
        Event(name='mapreduce__day_load_closed',
              params=dict(mrbasename='hahn', date='2016-01-01', logtype='redir-log')).save()

        r = action_should_be_scheduled(
            ActionConfig(
                task_params={
                    'action_id': 'mapreduce/postprocessing',
                },
                event_deps=[
                    EventDep(
                        name='mapreduce__day_load_closed',
                        params={
                            'mrbasename': None,
                            'logtype': 'access-log',
                            'date': None
                        }
                    ),
                    EventDep(
                        name='mapreduce__day_load_closed',
                        params={
                            'mrbasename': None,
                            'logtype': 'redir-log',
                            'date': None
                        }
                    )
                ]
            ),
            Event(
                name='mapreduce__day_load_closed',
                params={
                    'mrbasename': 'hahn',
                    'date': '2016-01-01',
                    'logtype': 'access-log'
                }
            ),
            Event.objects
        )

        self.assertEqual({'mrbasename': 'hahn', 'date': '2016-01-01'}, r['params'])
