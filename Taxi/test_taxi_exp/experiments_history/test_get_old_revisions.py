import pytest


NAME = 'experiment_with_revisions'


@pytest.mark.config(
    EXP_HISTORY_DEPTH=10,
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=('revisions.sql',))
async def test(taxi_exp_client):
    # check revisions list
    response = await taxi_exp_client.get(
        '/v1/experiments/revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body == {
        'revisions': [
            {'biz_revision': 1, 'revision': 254570},
            {'biz_revision': 1, 'revision': 254435},
            {'biz_revision': 1, 'revision': 254300},
            {'biz_revision': 1, 'revision': 254164},
            {'biz_revision': 1, 'revision': 254021},
            {'biz_revision': 1, 'revision': 253877},
            {'biz_revision': 1, 'revision': 253732},
            {'biz_revision': 1, 'revision': 253584},
            {'biz_revision': 1, 'revision': 253445},
        ],
    }
