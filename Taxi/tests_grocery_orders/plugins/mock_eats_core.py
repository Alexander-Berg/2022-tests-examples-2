import datetime
import json
from typing import cast
from typing import List
from typing import Union

import pytest

from tests_grocery_orders import models


def _validate(date_text):
    # will throw if format is wrong
    datetime.datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S%z')


@pytest.fixture(name='eats_core')
def mock_eats_core_eater(mockserver):
    class Context:
        def __init__(self):
            self.next_response = None

        def set_next_response(
                self,
                groups: Union[
                    List[models.LogisticGroupResponse],
                    models.LogisticGroupsErrorResponse,
                ],
        ):
            if groups is models.LogisticGroupsErrorResponse:
                self.next_response = mockserver.make_response(
                    json.dumps(
                        {
                            'isSuccess': False,
                            'statusCode': 400,
                            'type': 'error',
                            'errors': [],
                            'context': 'error',
                        },
                    ),
                    status=400,
                )
                return

            self.next_response = {
                'meta': {
                    'count': len(
                        cast(List[models.LogisticGroupResponse], groups),
                    ),
                },
                'payload': [
                    {
                        'id': group.group_id,
                        'places': group.places,
                        'metaGroupId': group.meta_group_id,
                    }
                    for group in cast(
                        List[models.LogisticGroupResponse], groups,
                    )
                ],
            }

    context = Context()

    @mockserver.json_handler('/eats-core/v1/surge/logistic-groups')
    def _mock_logistic_groups(request):
        if 'updatedSince' in request.json['filter']:
            _validate(request.json['filter']['updatedSince'])

        return context.next_response

    return context
