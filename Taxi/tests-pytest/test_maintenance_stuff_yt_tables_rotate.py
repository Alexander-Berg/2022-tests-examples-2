import pytest

from taxi.internal.yt_tools.table_rotate import models
from taxi.internal.yt_tools.table_rotate import schema
from taxi_maintenance.stuff import yt_tables_rotate_merge

TEST_CLUSTER = 'test_env'
RULES_COUNT = 7


@pytest.mark.config(YT_TABLES_ROTATE_SETTINGS={
    'enabled': True,
    'concurrency': 1,
    'skip_prefixes': [],
})
def test_do_stuff(patch):
    get_calls = _setup_env(patch)
    yt_tables_rotate_merge.do_stuff()
    assert get_calls() == RULES_COUNT


@pytest.mark.config(YT_TABLES_ROTATE_SETTINGS={
    'enabled': True,
    'concurrency': 3,
    'skip_prefixes': [],
    'pool': 'production',
})
def test_do_stuff_concurrency(patch):
    get_calls = _setup_env(patch)
    yt_tables_rotate_merge.do_stuff()
    assert get_calls() == RULES_COUNT


@pytest.mark.config(YT_TABLES_ROTATE_SETTINGS={
    'enabled': False,
    'concurrency': 1,
    'skip_prefixes': [],
})
def test_rotation_disabled(patch):
    get_calls = _setup_env(patch)
    yt_tables_rotate_merge.do_stuff()
    assert get_calls() == 0


@pytest.mark.config(YT_TABLES_ROTATE_SETTINGS={
    'enabled': True,
    'concurrency': 2,
    'skip_prefixes': ['rule_'],
})
def test_skip_all_rules(patch):
    get_calls = _setup_env(patch)
    yt_tables_rotate_merge.do_stuff()
    assert get_calls() == 0


@pytest.mark.config(YT_TABLES_ROTATE_SETTINGS={
    'enabled': True,
    'concurrency': 2,
    'skip_prefixes': ['rule_2', 'rule_3', 'rule_4extra'],
})
def test_partial_skip(patch):
    get_calls = _setup_env(patch)
    yt_tables_rotate_merge.do_stuff()
    assert get_calls() == RULES_COUNT - 2


def _setup_env(patch):
    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(client_name, **kwargs):
        return

    class FakeModel(models.BaseModel):
        def __init__(self):
            self.calls_rotate = 0

        def get_tasks_kwargs_for_one_node(self, yt_client, rule_name,
                                          map_node, log_extra=None):
            yield dict(test_case=None)

        def rotate(self, yt_client, **kwargs):
            self.calls_rotate += 1
            return 0

    rules = [
        schema.RotationRule(
            'rule_%s' % num, TEST_CLUSTER, '', FakeModel()
        ) for num in range(RULES_COUNT)
    ]

    @patch('taxi.internal.yt_tools.table_rotate.schema.load_rules')
    def load_rules(*args, **kwargs):
        return rules

    def get_calls():
        calls = 0
        for rule in rules:
            calls_rotate = rule.rotate_model.calls_rotate
            assert calls_rotate <= 1
            calls += calls_rotate
        return calls

    return get_calls
