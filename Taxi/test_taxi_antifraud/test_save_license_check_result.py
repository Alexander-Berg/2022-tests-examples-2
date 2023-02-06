import datetime

import pytest


@pytest.mark.now('2021-05-27T20:06:15.677Z')
async def test_save_license_check_result(
        db, web_app_client, patch_aiohttp_session, response_mock,
):
    response = await web_app_client.post(
        '/v1/save_license_check_result',
        json={
            'Type': 'Result',
            'ID': 1537657,
            'Callback': 'taxi-testing',
            'CallbackData': '9921295539 2020-12-02',
            'Data': {
                'Status': 'Success',
                'LicenseNumber': '9921295539',
                'LicenseIssueDate': '2020-12-02',
                'LicenseExpireDate': '2030-12-02',
                'LicenseBirthDate': '1993-08-05',
                'Deprivations': [],
            },
        },
    )

    assert response.status == 200
    assert await response.json() is None

    assert (
        await db.antifraud_license_checks_mdb.find({}, {'_id': False}).to_list(
            None,
        )
        == [
            {
                'Callback': 'taxi-testing',
                'CallbackData': '9921295539 2020-12-02',
                'Data': {
                    'Deprivations': [],
                    'LicenseExpireDate': '2030-12-02',
                    'LicenseIssueDate': '2020-12-02',
                    'LicenseBirthDate': '1993-08-05',
                    'LicenseNumber': '9921295539',
                    'Status': 'Success',
                },
                'ID': 1537657,
                'Type': 'Result',
                'processed': datetime.datetime(2021, 5, 27, 20, 6, 15, 677000),
            },
        ]
    )
