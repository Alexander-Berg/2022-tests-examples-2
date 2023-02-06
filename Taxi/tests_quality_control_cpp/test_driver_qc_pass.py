import pytest


@pytest.mark.parametrize(
    'pass_id, xservice_response, expected_code, expected_response',
    [
        ('5d485be9e0eda8c4aafc4e91', {}, 200, {}),
        (
            '5d485be9e0eda8c4aafc4e92',
            {'modified': '2017-04-25T07:00:00+00:00', 'text': 'some text'},
            200,
            {
                'modified': '2017-04-25T07:00:00+00:00',
                'text': 'Снимки отправлены.',
            },
        ),
        ('5d485be9e0eda8c4aafc4e91', None, 400, None),
    ],
)
async def test_driver_qc_pass(
        taxi_quality_control_cpp,
        load_binary,
        driver_authorizer,
        taximeter_xservice,
        quality_control,
        pass_id,
        xservice_response,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session('park_id', 'driver_session', 'driver_uuid')
    if xservice_response is not None:
        taximeter_xservice.set_qc_pass(pass_id, xservice_response)
    quality_control.set_pass(pass_id, 'qc_pass_response_not_bio.json')

    response = await taxi_quality_control_cpp.post(
        '/driver/qc/pass',
        params={
            'db': 'park_id',
            'session': 'driver_session',
            'exam': 'rqc',
            'media_code': 'front',
            'pass_id': pass_id,
        },
        data=load_binary('test_image.jpg'),
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'Content-Type': 'image/jpeg',
        },
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == expected_response
