import pytest


_REQUEST = {
    'id': '8472bfd9416c4830886aae8b526196d1',
    'entity_id': (
        '7ad36bc7560449998acbe2c57a75c293_bed51f6d85214821b7e5708776dbedd6'
    ),
    'is_created_by_service': False,
    'created_by': 'vdovkin',
    'can_activate_until': '2020-06-17T16:16:17.133422+00:00',
    'duration_minutes': 100,
    'type': 'commission',
    'country': 'rus',
    'currency': 'RUB',
    'tags': ['tag1', 'tag2'],
    'tariffs': ['econom'],
    'zones': ['test-zone1'],
}


def _make_experiment():
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {'predicate': {'type': 'true'}, 'value': {'enabled': True}},
        ],
    }


@pytest.mark.experiments3(**_make_experiment())
async def test_base(taxi_uantifraud):
    for _ in range(10):
        response = await taxi_uantifraud.post(
            '/v1/driver/promocode/check', json=_REQUEST,
        )
        assert response.status_code == 200
        assert response.json() == {'status': 'allow'}


@pytest.mark.experiments3(**_make_experiment())
async def test_triggered(taxi_uantifraud, testpoint):
    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {
            'id': '8472bfd9416c4830886aae8b526196d1',
            'entity_id': (
                '7ad36bc7560449998acbe2c57a75c293_'
                'bed51f6d85214821b7e5708776dbedd6'
            ),
            'is_created_by_service': False,
            'created_by': 'vdovkin',
            'can_activate_until': '2020-06-17T16:16:17.133Z',
            'duration_minutes': 100,
            'type': 'commission',
            'country': 'rus',
            'currency': 'RUB',
            'tags': ['tag1', 'tag2'],
            'tariffs': ['econom'],
            'zones': ['test-zone1'],
            'auto_entity_map': {},
        }
        return {'status': 'block'}

    for _ in range(10):
        response = await taxi_uantifraud.post(
            '/v1/driver/promocode/check', json=_REQUEST,
        )
        assert response.status_code == 200
        assert response.json() == {
            'status': 'block',
            'reason': 'test_triggered1',
        }

        await test_args_tp.wait_call()
