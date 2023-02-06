import pytest


def _param(*, name, data, id_suffix=''):
    if id_suffix:
        param_id = f'{name}_{id_suffix}'
    else:
        param_id = name

    return pytest.param({name: data}, id=param_id)


@pytest.mark.parametrize(
    ['data'],
    [
        # upper to lower and vice versa
        _param(
            name='indirect-upper-to-lower',
            data={
                'a-required-link': {
                    'b-optional-link': {
                        'a-required-link': {'b-field': 1},
                        'a-field': 2,
                    },
                    'b-field': 3,
                },
                'a-field': 4,
            },
        ),
        _param(
            name='lower-to-indirect-upper',
            data={
                'b-optional-link': {
                    'a-required-link': {'b-field': 1},
                    'a-field': 2,
                },
                'b-field': 3,
            },
        ),
        _param(
            name='upper-to-indirect-lower',
            data={
                'a-optional-link': {
                    'b-required-link': {'a-field': 1},
                    'b-field': 2,
                },
                'a-field': 3,
            },
        ),
        _param(
            name='indirect-lower-to-upper',
            data={
                'b-required-link': {
                    'a-optional-link': {
                        'b-required-link': {'a-field': 1},
                        'b-field': 2,
                    },
                    'a-field': 3,
                },
                'b-field': 4,
            },
        ),
        # type to alias
        _param(
            name='indirect-type-to-alias',
            data={
                'a-optional-link': {
                    'a-optional-link': {'a-field': 1},
                    'a-field': 2,
                },
                'a-field': 3,
            },
        ),
        _param(
            name='alias-to-indirect-type',
            data={
                'a-optional-link': {
                    'a-optional-link': {'a-field': 1},
                    'a-field': 2,
                },
                'a-field': 3,
            },
        ),
        # oneOf to Type
        _param(
            name='indirect-oneof-to-type',
            data={
                'a-required-link': {
                    'b-required-link': {
                        'a-required-link': {'c-field': 1},
                        'a-field': 2,
                    },
                    'b-field': 3,
                },
                'a-field': 4,
            },
        ),
        _param(
            name='type-to-indirect-oneof-alpha',
            data={
                'a-required-link': {
                    'b-required-link': {
                        'a-required-link': {'c-field': 1},
                        'a-field': 2,
                    },
                    'b-field': 3,
                },
                'a-field': 4,
            },
        ),
        # oneOf with discriminator to Type
        _param(
            name='indirect-oneof-discr-to-type',
            data={
                'type': 'bravo',
                'b-required-link': {
                    'type': 'alpha',
                    'a-optional-link': {
                        'type': 'bravo',
                        'b-required-link': {'type': 'alpha', 'a-field': 1},
                        'b-field': 2,
                    },
                    'a-field': 3,
                },
                'b-field': 4,
            },
        ),
        _param(
            name='indirect-oneof-discr-multi-to-type',
            data={
                'type': 'bravo_alt',
                'b-required-link': {
                    'type': 'alpha_alt',
                    'a-optional-link': {
                        'type': 'bravo',
                        'b-required-link': {'type': 'alpha', 'a-field': 1},
                        'b-field': 2,
                    },
                    'a-field': 3,
                },
                'b-field': 4,
            },
        ),
        _param(
            name='type-to-indirect-oneof-discr-bravo',
            data={
                'type': 'bravo',
                'b-required-link': {
                    'type': 'alpha',
                    'a-optional-link': {
                        'type': 'bravo',
                        'b-required-link': {'type': 'alpha', 'a-field': 1},
                        'b-field': 2,
                    },
                    'a-field': 3,
                },
                'b-field': 4,
            },
        ),
        # type to allOf
        _param(
            name='allof-to-indirect-type',
            data={
                'a-optional-link': {
                    'b-optional-link': {'a-field': 1, 'b-field': 2},
                    'a-field': 3,
                    'b-field': 4,
                },
                'a-field': 5,
                'b-field': 6,
            },
        ),
    ],
)
async def test_all(taxi_test_service, mockserver, data):
    @mockserver.json_handler(f'/test-service/recursive-types/all')
    def _handler(_req):
        assert _req.json == data
        return {'value': _req.json}

    response = await taxi_test_service.post(f'recursive-types/all', json=data)

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'value': data}
