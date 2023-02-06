import pytest
from infranaim.utils import taxi_secdist


@pytest.mark.parametrize('use_patch,', [True, False])
def test_secdist(patch, load_json, use_patch):
    if use_patch:
        @patch('infranaim.utils.taxi_secdist.cached_secdist')
        def _get_secdist(*args, **kwargs):
            data = load_json('secdist.json')
            return taxi_secdist.Secdist(data)

    value = taxi_secdist.secdist_or_env('TEST_KEY')
    if use_patch:
        assert value == 'TEST_VALUE1'
    else:
        assert value is None
