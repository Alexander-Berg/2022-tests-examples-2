import json


import pytest


from clownductor.internal.deployments import models as deploy_models
from clownductor.internal.utils import postgres


@pytest.fixture(name='get_ticket')
def _get_ticket(mockserver):
    @mockserver.json_handler(
        r'/startrek/issues/(?P<ticket>[\w-]+)', regex=True,
    )
    async def do_it(_, ticket):
        if ticket == 'TAXIREL-2':
            return {'status': {'key': 'open'}}
        return {'status': {'key': 'closed'}}

    return do_it


@pytest.fixture(name='create_comment')
def _create_comment(mockserver):
    @mockserver.json_handler('/startrek/issues/TAXIREL-2/comments', regex=True)
    def _comments(request):
        assert 'Deployment was' in request.json.get('text')

    return _comments


async def _get_deployments(web_context, service_id):
    query, args = web_context.sqlt.jobs_get_by_service_id_with_filtration(
        service_id=service_id,
        limit=None,
        names=[deploy_models.DEPLOY_JOBS],
        offset=None,
    )
    async with postgres.primary_connect(web_context) as conn:
        result = await conn.fetch(query, *args)
    return result


@pytest.mark.pgsql('clownductor', files=['test_retry_data.sql'])
@pytest.mark.parametrize(
    'data, expected',
    [
        pytest.param(
            {'deployment_id': 3},
            200,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={
                        'enable_search_deployment_ticket': True,
                    },
                ),
            ],
            id='found ticket from last job',
        ),
        pytest.param(
            {'deployment_id': 3},
            400,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={
                        'enable_search_deployment_ticket': False,
                    },
                ),
            ],
            id='old way without  taxirel_ticket',
        ),
        pytest.param(
            {'deployment_id': 3, 'taxirel_ticket': 'TAXIREL-2'},
            200,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={
                        'enable_search_deployment_ticket': False,
                    },
                ),
            ],
            id='old way',
        ),
        pytest.param(
            {'deployment_id': 3, 'taxirel_ticket': 'TAXIREL-5'},
            400,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={
                        'enable_search_deployment_ticket': True,
                    },
                ),
            ],
            id='test taxirel_ticket cannot override',
        ),
    ],
)
@pytest.mark.features_on('locks_for_deploy')
async def test_double_deploy_retry(
        web_app_client,
        web_context,
        create_comment,
        get_ticket,
        data,
        expected,
):
    response = await web_app_client.post(
        f'/v1/service/deployment/retry/',
        json=data,
        headers={'X-Yandex-Login': 'elrusso'},
    )

    assert response.status == expected
    if expected == 200:
        response_text = json.loads(await response.text())
        assert response_text['deployment_id'] == 5
        deployments_final = await _get_deployments(web_context, 1)
        assert len(deployments_final) == 4
        locks = await web_context.locks.find(name='Deploy.test_service_stable')
        assert len(locks) == 1
        assert locks[0]['job_id'] == 4
        assert get_ticket.times_called == 1
        assert create_comment.times_called == 1


@pytest.mark.parametrize(
    'job_id, expected_lock_for_job_id', [(3, 4), (4, None)],
)
@pytest.mark.pgsql('clownductor', files=['test_retry_data.sql'])
@pytest.mark.features_on('locks_for_deploy')
async def test_deploy_cancel(
        web_app_client, web_context, job_id, expected_lock_for_job_id,
):
    response = await web_app_client.post(
        f'/v1/service/deployment/cancel/',
        params={'deployment_id': job_id},
        headers={'X-Yandex-Login': 'elrusso'},
    )

    assert response.status == 200
    deployments_final = await _get_deployments(web_context, 1)
    assert len(deployments_final) == 3
    locks = await web_context.locks.find(name='Deploy.test_service_stable')
    if expected_lock_for_job_id:
        assert len(locks) == 1
        assert locks[0]['job_id'] == 4
    else:
        assert not locks
