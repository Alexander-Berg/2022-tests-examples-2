import uuid

import pytest


@pytest.fixture
def qc_pools(mockserver):
    class QcPoolsContext:
        def __init__(self):
            self.passes = None
            self.entities = None
            self.resolutions = None

        def set_passes(self, passes):
            self.passes = passes

        def set_resolutions(self, resolutions):
            self.resolutions = {
                resolution['id']: resolution['resolution']
                for resolution in resolutions
            }

        def set_entities(self, entities):
            self.entities = {
                entity['id']: entity['tags'] for entity in entities
            }

    context = QcPoolsContext()

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    async def retrieve(request):
        assert request.method == 'POST'
        if request.json.get('cursor') == 'next':
            return {'cursor': 'empty', 'items': []}
        return {'cursor': 'next', 'items': context.passes}

    def make_fields(pass_data):
        return {data['field']: data['value'] for data in pass_data}

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    async def push(request):
        assert request.method == 'POST'
        assert request.json['items']
        processed = {
            pass_['entity_id']: make_fields(pass_['data'])
            for pass_ in request.json['items']
        }

        assert len(request.json['items']) == len(context.passes)

        for pass_ in context.passes:
            if 'data' in pass_:
                for field_ in pass_['data']:
                    assert field_['field'] not in processed[pass_['entity_id']]

        for pass_ in processed:
            if pass_ in context.resolutions:
                assert 'resolution' in processed[pass_]
                assert (
                    processed[pass_]['resolution']
                    == context.resolutions[pass_]
                )
            else:
                assert 'tags' in processed[pass_]
                assert processed[pass_]['tags'] == context.entities.get(
                    pass_, [],
                )

        return {}

    context.retrieve = retrieve  # pylint: disable=W0201
    context.push = push  # pylint: disable=W0201

    return context


@pytest.fixture
def tags(mockserver):
    class TagsContext:
        def __init__(self):
            self.entities = None

        def set_entities(self, entities):
            self.entities = entities

    context = TagsContext()

    @mockserver.json_handler('/tags/v2/match')
    async def match(request):
        assert request.method == 'POST'
        return {'entities': context.entities}

    context.match = match  # pylint: disable=W0201

    return context


def _make_pass(entity_id, entity_type, data=None):
    result = dict(
        id=uuid.uuid4().hex,
        entity_id=entity_id,
        entity_type=entity_type,
        exam='dkvu',
        modified='2020-05-12T16:30:00.000Z',
        status='NEW',
    )

    if data:
        for item in data:
            item['required'] = item.get('required', False)
        result['data'] = data

    return result


def _make_resolution(pass_id, resolution):
    return {'id': pass_id, 'resolution': resolution}


def _make_entity(entity_id, tags_):
    return {'id': entity_id, 'tags': tags_}


@pytest.mark.config(
    QC_EXECUTORS_FETCH_TAGS_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
    },
)
@pytest.mark.parametrize(
    ('passes_', 'entities_', 'resolutions_'),
    [
        pytest.param([], [], [], id='empty'),
        pytest.param(
            [_make_pass('id_1', 'car')],
            [_make_entity('id_1', ['beaten'])],
            [],
            id='car',
        ),
        pytest.param(
            [_make_pass('id_1', 'driver')],
            [_make_entity('id_1', ['medmask_off'])],
            [],
            id='driver',
        ),
        pytest.param(
            [_make_pass('id_1', 'driver')],
            [_make_entity('id_1', [])],
            [],
            id='empty tag',
        ),
        pytest.param([_make_pass('id_1', 'driver')], [], [], id='no tag'),
        pytest.param(
            [_make_pass('id_1', 'QWEQWERQWE')], [], [], id='unknown entity',
        ),
        pytest.param(
            [
                _make_pass('id_1', 'car'),
                _make_pass('id_2', 'driver'),
                _make_pass('id_3', 'driver'),
                _make_pass('id_4', 'driver'),
                _make_pass('id_5', 'QWEQWERQWE'),
            ],
            [
                _make_entity('id_1', ['beaten']),
                _make_entity('id_2', ['medmask_off']),
                _make_entity('id_3', []),
            ],
            [],
            id='bulk',
        ),
        pytest.param(
            [
                _make_pass(
                    'id_1', 'car', [{'field': 'field1', 'value': 'value1'}],
                ),
            ],
            [_make_entity('id_1', ['beaten'])],
            [],
            id='non-empty data',
        ),
        pytest.param(
            [
                _make_pass(
                    'id_1',
                    'car',
                    [
                        {'field': 'field1', 'value': 'value1'},
                        {'field': 'field2', 'value': 'value2'},
                    ],
                ),
            ],
            [],
            [],
            id='non-empty data & no tag',
        ),
    ],
)
async def test_basic_scenarios(
        testpoint,
        taxi_qc_executors,
        qc_pools,  # pylint: disable=W0621
        tags,  # pylint: disable=W0621
        passes_,
        entities_,
        resolutions_,
):
    qc_pools.set_passes(passes_)
    qc_pools.set_entities(entities_)
    qc_pools.set_resolutions(resolutions_)
    tags.set_entities(entities_)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-tags'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
