import pytest

import localization.overrides as overrides


@pytest.mark.parametrize(
    'keys, expected',
    [
        pytest.param(['keyset1'], ['override_yango'], id='single1'),
        pytest.param(
            ['keyset2'],
            ['override_aze', 'override_uber', 'override_yango'],
            id='multiple1',
        ),
        pytest.param(
            ['keyset1', 'keyset2', 'keyset3'],
            ['override_aze', 'override_uber', 'override_yango'],
            id='multiple2',
        ),
        pytest.param(['new_keyset'], [], id='empty'),
    ],
)
def test_taximeter_overrides_overwriters(
        library_context, load_json, keys, expected,
):
    # arrange
    overrider = overrides.TaximeterOverrides(library_context.config)
    # assert
    assert sorted(overrider.overwriters(keys)) == sorted(expected)


@pytest.mark.parametrize(
    'keyset,app,expected',
    [
        ['keyset1', 'Vezet', ['keyset1']],
        ['keyset1', 'uber', ['keyset1']],
        ['keyset2', 'uBEr', ['override_uber', 'keyset2']],
        ['keyset2', 'aZ', ['override_aze', 'keyset2']],
        ['unknown_keyset', 'az', ['unknown_keyset']],
    ],
)
def test_taximeter_overrides_detect_overwriter(
        library_context, load_json, keyset, app, expected,
):
    # arrange
    overrider = overrides.TaximeterOverrides(library_context.config)
    # assert
    assert overrider.detect_overwriter(keyset, app) == expected
