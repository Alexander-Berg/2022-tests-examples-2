import pytest
import yt.wrapper

from taxi import yt_wrapper


@pytest.mark.parametrize(
    'input_attrs, expected_attrs, error',
    [
        ((None, None, None), ([None], [None], None), False),
        (('prefix', None, None), (['prefix'], [None], 1), False),
        (('prefix', None, 2), (['prefix', 'prefix'], [None, None], 2), False),
        ((['prefix'], None, 2), None, True),
        (('prefix', {}, None), (['prefix'], [{}], 1), False),
        (('prefix', ({},), 1), (['prefix'], ({},), 1), False),
        ((('prefix',), ({},), None), (('prefix',), ({},), None), False),
    ],
)
@pytest.mark.nofilldb()
def test_prepare_tmp_attrs(input_attrs, expected_attrs, error):
    # pylint: disable=protected-access
    if error:
        with pytest.raises(yt_wrapper.IncorrectTempAttributesError):
            yt_wrapper._prepare_tmp_attrs(*input_attrs)
    else:
        assert expected_attrs == yt_wrapper._prepare_tmp_attrs(*input_attrs)


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
@pytest.mark.nofilldb()
def test_yt_rpc_driver_bindings():
    try:
        yt.wrapper.native_driver.lazy_import_driver_bindings(
            backend_type='rpc', allow_fallback_to_native_driver=False,
        )
    except TypeError:  # backward compatibility with old driver
        yt.wrapper.native_driver.lazy_import_driver_bindings()
    assert yt.wrapper.native_driver.driver_bindings is not None
