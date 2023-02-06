import os
import pytest
import yatest.common

import metrika.pylib.state as mstate
import metrika.pylib.structures.dotdict as mdd


class TestError(Exception):
    pass


def test_base_state():
    state = mstate.BaseState()

    with pytest.raises(NotImplementedError):
        state.load()

    with pytest.raises(NotImplementedError):
        state.save()

    assert isinstance(state.data, mdd.DotDict)

    state = mstate.BaseState(data={'hello': 'world'})
    assert state.data.hello == 'world'


def test_base_state_update(base_state, monkeypatch):
    def mock_save(*args, **kwargs):
        raise TestError()

    monkeypatch.setattr(base_state, 'save', mock_save)

    with pytest.raises(TestError):
        base_state.update(hello='world')

    assert base_state.data.hello == 'world'


def test_json_state(temp_dir):
    path = os.path.join(temp_dir, 'awesome.state')
    json_state = mstate.JsonFileState(
        path=path,
        data={'hello': 'world'},
    )

    with pytest.raises(IOError):
        assert json_state.load()

    assert json_state.data.hello == 'world'
    assert json_state.save()
    assert json_state.load()
    assert json_state.data.hello == 'world'
    json_state.update(hello='noworld')
    assert json_state.load()
    assert json_state.data.hello == 'noworld'

    json_state = mstate.JsonFileState(
        path=yatest.common.source_path('metrika/pylib/state/tests/test.state'),
    )
    assert json_state.data.awesome == 'value'
