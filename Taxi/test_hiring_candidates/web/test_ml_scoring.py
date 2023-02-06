import datetime
import json
import typing

import pytest

from generated.clients import hiring_data_markup
from generated.models import hiring_data_markup as data_markup_models


ROUTE = '/v1/ml-score/execute'


@pytest.mark.parametrize(
    'request_type, case, score, data_markup_fail, status',
    [
        ('valid', 'SCORE_NO_ZENDESK', 1, False, 200),
        ('valid', 'SCORE_WITH_ZENDESK', 1, False, 200),
        ('valid', 'SCORE_WITH_ZENDESK', 0, False, 200),
        ('valid', 'SCORE_WITH_ZENDESK', 1, True, 400),
        ('invalid', 'NO_PHONE', 0, True, 400),
    ],
)
async def test_scoring(
        stq,
        patch,
        load_binary,
        load_json,
        web_app_client,
        personal,
        request_type,
        case,
        score,
        data_markup_fail,
        status,
):
    @patch('hiring_candidates.internal.yt_operations.download_file')
    async def _yt_file(*args, **kwargs):
        if args[2].endswith('.json'):
            model_name = args[2].split('/')[-1].replace('.json', '')
            _data = json.dumps(load_json('yt_config.json')[model_name])
        else:
            _data = load_binary('yt_model.cbm')
        return Reader(_data)

    @patch(
        'hiring_candidates.internal.yt_operations.'
        'select_dynamic_table_rows',
    )
    async def _yt_table(*args, **kwargs):
        return GeneratorMock(
            {'phone': 'somestring', 'db_id': 0, 'driver_id': 1},
        )

    @patch(
        'hiring_candidates.internal.models.MLModel.'
        '_model_predict_classification',
    )
    async def _score_mock(*args, **kwargs):
        return score

    @patch(
        'hiring_candidates.internal.ml_manager.Manager._request_data_markup',
    )
    async def _data_markup(*args, **kwargs):
        if not data_markup_fail:
            return hiring_data_markup.ExperimentsPerform200(
                DataMarkup.success(args[1]),
            )
        return hiring_data_markup.ExperimentsPerform400(DataMarkup.error())

    request_data = load_json('requests.json')[request_type][case]
    body = request_data['REQUEST']
    params = request_data['PARAMS']
    response = await web_app_client.post(ROUTE, json=body, params=params)
    assert response.status == status
    if case == 'SCORE_WITH_ZENDESK' and status == 200:
        assert stq.hiring_infranaim_api_updates.times_called == 1
        data = stq.hiring_infranaim_api_updates.next_call()
        assert data
        fields = data['kwargs']['ticket_data']['params']
        if score:
            assert fields['new_field'] == 'NEW_VALUE'
        else:
            assert fields['old_field'] == 'OLD_VALUE'
    elif case == 'NO_PHONE':
        assert not stq.hiring_infranaim_api_updates.times_called
        response_data = await response.json()
        assert response_data['details']['errors'][0]['code'] == 'MISSING_PHONE'
    else:
        assert not stq.hiring_infranaim_api_updates.times_called


class Reader:
    def __init__(self, data):
        if isinstance(data, str):
            self.data = bytes(data, encoding='utf8')
        else:
            self.data = data

    def read(self):
        return self.data


class GeneratorMock:
    def __init__(self, data):
        self.data = data

    def __next__(self):
        return self.data


class DataMarkup:
    @staticmethod
    def success(request_fields: typing.List[data_markup_models.Field]):
        decision = next(
            (item.value for item in request_fields if item.name == 'decision'),
            None,
        )
        if decision is None:
            raise TypeError
        fields = [
            data_markup_models.Field(name='new_field', value='NEW_VALUE'),
        ]
        if decision == 0:
            fields = [
                data_markup_models.Field(name='old_field', value='OLD_VALUE'),
            ]
        return data_markup_models.ResponseExperimentsPerform(
            data_markup_models.PerformResultSuccess(
                fields=fields,
                flow='SOME_FLOW',
                tags_add=['a_tag'],
                tags_remove=['the_tag'],
                ticket_id='1',
            ),
        )

    @staticmethod
    def error():
        return data_markup_models.ResponseError(
            code='ERROR',
            message='Error',
            details=data_markup_models.ResponseErrorDetails(
                occurred_at=datetime.datetime.now(), errors=[],
            ),
        )
