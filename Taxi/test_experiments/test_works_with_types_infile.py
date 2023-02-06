import typing

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files


class Case(typing.NamedTuple):
    response_status: int
    infile_type: str
    file_type: str
    content: bytes


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(
            response_status=200,
            file_type='string',
            infile_type='string',
            content=(
                b'5ab66ff9cab04dfcb778147be85f1297\n'
                b'e2ed1c509f8f47eb82cb2d7fc42a6ee2\n'
            ),
        ),
        Case(
            response_status=200,
            file_type='str',
            infile_type='string',
            content=(
                b'5ab66ff9cab04dfcb778147be85f1297\n'
                b'e2ed1c509f8f47eb82cb2d7fc42a6ee2\n'
            ),
        ),
        Case(
            response_status=200,
            file_type='int',
            infile_type='int',
            content=b'1234\n5464576\n',
        ),
        Case(
            response_status=200,
            file_type='integer',
            infile_type='int',
            content=b'1234\n5464576\n',
        ),
        Case(
            response_status=400,
            file_type='string',
            infile_type='double',
            content=b'1.24334\n6464.300',
        ),
        Case(
            response_status=409,
            file_type='string',
            infile_type='int',
            content=b'vvvvvvv',
        ),
        Case(
            response_status=400,
            file_type='string',
            infile_type='full_bad_type',
            content=b'vvvvvvv',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_works_with_types_infile(
        response_status, file_type, infile_type, content, taxi_exp_client,
):
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', content, file_type=file_type,
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    predicate = {
        'type': 'in_file',
        'init': {
            'arg_name': 'phone_id',
            'file': file_id,
            'set_elem_type': infile_type,
        },
    }

    data = experiment.generate_default(match_predicate=predicate)

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == response_status
