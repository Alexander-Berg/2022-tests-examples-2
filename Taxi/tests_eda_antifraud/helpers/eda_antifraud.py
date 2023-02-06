async def validate(
        taxi_eda_antifraud,
        courier_id,
        app_info,
        expected_status,
        expected_response_json,
):
    headers = {
        'X-YaEda-CourierId': courier_id,
        'Content-Type': 'application/json; charset=UTF-8',
    }

    response = await taxi_eda_antifraud.post(
        '/v1/eda-antifraud/validate', {'appInfo': app_info}, headers=headers,
    )

    response_json = response.json()

    assert expected_status == response.status_code, (
        expected_status,
        response.status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
