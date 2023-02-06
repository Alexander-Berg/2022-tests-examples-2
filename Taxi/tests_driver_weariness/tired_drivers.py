# flake8: noqa I101
# pylint: disable=C1801
from typing import Optional, Dict, List


class TiredDriverEntry:
    def __init__(self, tired_status: str, block_time: str, block_till: str):
        self.tired_status = tired_status
        self.block_time = block_time
        self.block_till = block_till


def _verify_tired_drivers_response(
        udid: str,
        expected_driver: Optional[TiredDriverEntry],
        tired_drivers: List[Dict[str, str]],
):
    filtered = list(
        filter(lambda x: x['unique_driver_id'] == udid, tired_drivers),
    )
    if expected_driver is None:
        assert len(filtered) == 0
        return

    assert len(filtered) == 1
    driver = filtered[0]
    assert driver['tired_status'] == expected_driver.tired_status
    assert driver['block_time'] == expected_driver.block_time
    assert driver['block_till'] == expected_driver.block_till


async def verify_tired_drivers(
        taxi_driver_weariness,
        udid: str,
        is_tired: bool,
        expected_response: Dict[str, str],
):
    tired_drivers = await taxi_driver_weariness.get('v1/tired-drivers')

    assert tired_drivers.status_code == 200
    expected_driver = None

    if is_tired:
        expected_driver = TiredDriverEntry(
            expected_response['tired_status'],
            expected_response['block_time'],
            expected_response['block_till'],
        )

    _verify_tired_drivers_response(
        udid, expected_driver, tired_drivers.json()['items'],
    )
