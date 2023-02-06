from cargo_tests.utils import requests_helper


def test_run_cargo_services(cargo_claims, cargo_dispatch, cargo_orders):
    response = cargo_claims.ping()
    assert response.status_code == 200, response.text
    response = cargo_dispatch.ping()
    assert response.status_code == 200, response.text
    response = cargo_orders.ping()
    assert response.status_code == 200, response.text


def test_create_claim(cargo_claims):
    project_root = requests_helper.get_project_root()
    response = cargo_claims.create_claim(
        json=requests_helper.build_request(
            username='test',
            phone='+79993333333',
            comment='comment',
            request=project_root / 'test_data/default.json',
            corp_client_id='5e36732e2bc54e088b1466e08e31c486',
            taxi_class='courier',
            dont_skip_confirmation=False,
            post_payment=None,
        ),
    )
    assert response.status_code == 200, response.text

    response = cargo_claims.wait_for_claim_status(
        claim_id=response.json()['id'],
        statuses=('new', 'estimating'),
        wait=60,
    )
    assert response.status_code == 200, response.text
    assert response['status'] in (
        'new',
        'estimating',
        'ready_for_approval',
    ), 'Invalid claim status'
