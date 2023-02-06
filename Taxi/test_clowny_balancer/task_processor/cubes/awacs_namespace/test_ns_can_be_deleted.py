import pytest

CUBE_NAME = 'AwacsNamespaceCanBeDeleted'


@pytest.fixture(name='awacs_mock')
def _awacs_mock(load_yaml, awacs_mock):
    return awacs_mock(load_yaml('awacs_data.yaml'))


def case(ns_id: str, can_be_deleted: bool, id_: str):
    return pytest.param(
        {'awacs_namespace_id': ns_id},
        {'namespace_can_be_deleted': can_be_deleted},
        id=id_,
    )


@pytest.mark.parametrize(
    'input_data, payload',
    [
        case('ns-1', True, 'has domain'),
        case('ns-2', False, 'has upstream'),
        case('ns-3', False, 'has backend'),
        case('ns-4', True, 'can be deleted'),
        case('ns-5', False, 'has domain with non default upstream'),
    ],
)
async def test_cube(awacs_mock, call_cube, input_data, payload):
    result = await call_cube(CUBE_NAME, input_data)
    assert result['payload'] == payload
