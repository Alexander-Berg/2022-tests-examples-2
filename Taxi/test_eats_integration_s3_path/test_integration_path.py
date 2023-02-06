import typing

import pytest


class _Sentinel:
    pass


SENTINEL = _Sentinel()


def _format_params(
        task_type: str = 'stocks',
        place_group_id: str = '123',
        origin_place_id: str = '1',
):
    return {
        'task_type': task_type,
        'place_group_id': place_group_id,
        'origin_place_id': origin_place_id,
    }


def make_pytest_params(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        params: typing.Any = SENTINEL,
        prefix: typing.Any = SENTINEL,
        postfix: typing.Any = SENTINEL,
        file_type: typing.Any = SENTINEL,
        s3_path: typing.Any = SENTINEL,
):
    return pytest.param(
        value_or_default(params, _format_params()),
        value_or_default(prefix, ''),
        value_or_default(postfix, ''),
        value_or_default(file_type, 'json'),
        value_or_default(
            s3_path, 'integration/default/stocks/stocks_123_1.json',
        ),
        id=id,
        marks=marks,
    )


def value_or_default(value, default):
    return default if value is SENTINEL else value


@pytest.mark.parametrize(
    ('params', 'prefix', 'postfix', 'file_type', 's3_path'),
    (
        make_pytest_params(id='success'),
        make_pytest_params(
            id='success_config',
            marks=[
                pytest.mark.config(
                    EATS_INTEGRATION_S3_FIELDS_ORDER_SETTINGS={
                        'task_type': 3,
                        'place_group_id': 1,
                        'origin_place_id': 2,
                    },
                ),
            ],
            s3_path='integration/default/stocks/123_1_stocks.json',
        ),
        make_pytest_params(
            id='prefix_postfix',
            marks=[
                pytest.mark.config(
                    EATS_INTEGRATION_S3_FIELDS_ORDER_SETTINGS={'task_type': 1},
                ),
            ],
            prefix='cache',
            postfix='filtered',
            s3_path='integration/default/stocks/cache_stocks_filtered.json',
        ),
    ),
)
async def test_fetch_s3_path(
        library_context, params, prefix, postfix, file_type, s3_path,
):
    result = library_context.integration_path.fetch_path(
        prefix=prefix, postfix=postfix, file_type=file_type, **params,
    )
    assert result == s3_path
