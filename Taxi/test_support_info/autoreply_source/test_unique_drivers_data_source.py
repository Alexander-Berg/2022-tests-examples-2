import pytest

from support_info import app
from support_info.internal import autoreply_source


@pytest.mark.config(
    DRIVER_ML_AUTOREPLY_FIELDS={
        'unique_drivers': {
            'fields': ['dp'],
            'mapping': {'dp': 'driver_points'},
        },
    },
)
@pytest.mark.parametrize(
    ('driver_license', 'expected_result'),
    (('driver_license', {'driver_points': 42}), ('wrong_license', {})),
)
async def test_unique_driver_data_source(
        support_info_app: app.SupportInfoApplication,
        driver_license: str,
        expected_result: dict,
):
    order_source = autoreply_source.UniqueDriversDataSource(
        db=support_info_app.db, config=support_info_app.config,
    )

    result = await order_source.get_data({'driver_license': driver_license})
    assert result == expected_result
