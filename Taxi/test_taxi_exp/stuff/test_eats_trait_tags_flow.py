import os
from typing import Dict
from typing import List

import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


FILTERS_BY_OBSERVATIONS: Dict = {
    'ios': [{'name': 'eda_app_platform_filter', 'value': 'ios'}],
    'android': [{'name': 'eda_app_platform_filter', 'value': 'android'}],
    'moscow': [{'name': 'user_region_filter', 'value': '213'}],
    'spb': [{'name': 'user_region_filter', 'value': '2'}],
    'without_msk_spb': [
        {'name': 'user_outer_region_filter', 'value': '213 2'},
    ],
}

TICKET_BODY_PATH = os.path.join(
    os.path.dirname(__file__), 'static', 'default', 'ticket_body.txt',
)


@pytest.fixture(name='local_mock')
def local_mock_fixture(patch):
    class TicketInfo:
        title: str
        queue: str
        description: str
        comments: List = []

    class Collector:
        launch_create_observation: int = 0
        ticket_info: TicketInfo = TicketInfo

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(summary, queue, description, *args, **kwargs):
        Collector.ticket_info.title = summary
        Collector.ticket_info.queue = queue
        Collector.ticket_info.description = description
        return {'key': f'{queue}-123'}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, *args, **kwargs):
        Collector.ticket_info.comments.append(text)

    @patch('taxi.clients.coffee.AbExperimentsClient.create_observation')
    async def _create_observation(title, *args, **kwargs):
        Collector.launch_create_observation += 1
        return {
            'obs_id': f'32{Collector.launch_create_observation}_id',
            'title': title,
        }

    return Collector


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {
                'trait_tags_v2': {
                    'prepare-eat-experiment': {'availability': ['__any__']},
                    'eat-experiment-ready': {'availability': ['__any__']},
                },
            },
        },
    },
    EXP_EDA_AB_CREATION_SETTINGS={
        'features': {
            'testids_generation_by_name': True,
            'report_of_group_sizes': True,
        },
        'settings': {
            'filters_by_observations': FILTERS_BY_OBSERVATIONS,
            'queue': 'EDUSA',
        },
    },
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_eats_trait_tags_flow(taxi_exp_client, local_mock):
    # create experiment
    body = experiment.generate(
        trait_tags=['prepare-eat-experiment'],
        owners=['serg-novikov'],
        clauses=[
            experiment.make_clause(
                'group-1',
                predicate=experiment.mod_sha1_predicate(
                    range_from=0, range_to=49,
                ),
            ),
            experiment.make_clause(
                'group-2',
                predicate=experiment.mod_sha1_predicate(
                    range_from=49, range_to=98,
                ),
                enabled=True,
            ),
            experiment.make_clause(
                'group-3',
                predicate=experiment.mod_sha1_predicate(
                    range_from=98, range_to=100,
                ),
                enabled=False,
            ),
        ],
    )
    response = await taxi_exp_client.post(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment.DEFAULT_EXPERIMENT_NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    # running cron
    await cron_run.main(['taxi_exp.stuff.eats_trait_tags_flow', '-t', '0'])

    # check that tag is change
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment.DEFAULT_EXPERIMENT_NAME},
    )
    body = await response.json()
    assert body['trait_tags'] == ['eat-experiment-ready']

    # check create observations
    assert (
        local_mock.launch_create_observation
        == len(FILTERS_BY_OBSERVATIONS) + 1
    )

    # check queue
    assert local_mock.ticket_info.queue == 'EDUSA'

    # check ticket body generation
    text = (
        f'Title:\n{local_mock.ticket_info.title}\n'
        + f'Description:\n{local_mock.ticket_info.description}'
        + '\n'.join(
            f'Comment:\n{comment}'
            for comment in local_mock.ticket_info.comments
        )
    )
    with open(TICKET_BODY_PATH) as doc:
        lines = text.split('\n')
        info = [line.rstrip() for line in doc.readlines()]
        for index, check_info in enumerate(zip(lines, info)):
            ticket_line, expected_line = check_info
            assert (
                ticket_line == expected_line
            ), f'{index + 1}: {lines[index:index+3]}'
