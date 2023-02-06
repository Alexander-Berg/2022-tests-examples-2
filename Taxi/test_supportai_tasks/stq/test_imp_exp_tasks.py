import copy
import datetime
import io
import json
from typing import Dict
from typing import List

import pandas as pd
import pytest
import xlsxwriter

from supportai_lib.tasks import base_task
from supportai_lib.tasks import constants

from supportai_tasks.generated.stq3 import stq_context
from supportai_tasks.stq import runner


SAMPLE_PROJECT: Dict[str, List[Dict]] = {
    'tags': [
        {'id': 1, 'slug': 'tag1'},
        {'id': 2, 'slug': 'tag2'},
        {'id': 3, 'slug': 'tag3'},
    ],
    'topics': [
        {'id': 1, 'parent_id': None, 'slug': 'topic1', 'title': 'Тема 1'},
        {'id': 2, 'parent_id': 1, 'slug': 'topic2', 'title': 'Тема 2'},
        {'id': 3, 'parent_id': 1, 'slug': 'topic3', 'title': 'Тема 3'},
        {'id': 4, 'parent_id': 2, 'slug': 'topic4', 'title': 'Тема 4'},
    ],
    'entities': [
        {
            'id': '1',
            'slug': 'entity1',
            'title': 'Entity 1',
            'type': 'str',
            'extractor': '{"type": "choice_from_variants", "variants": [{"regular_expression": "a|A", "value": "A"}]}',  # noqa
        },
        {
            'id': '2',
            'slug': 'entity2',
            'title': 'Entity 2',
            'type': 'str',
            'extractor': (
                '{"type": "custom", "extractor_type": "custom_extractor"}'
            ),
        },
    ],
    'features': [
        {
            'id': 1,
            'slug': 'feature1',
            'description': 'Feature 1',
            'type': 'int',
            'is_array': False,
            'domain': '["1"]',
            'default_value': None,
            'clarification_type': 'external',
            'force_question': None,
            'clarifying_question': None,
            'entity_slug': None,
            'entity_extract_order': None,
            'is_calculated': True,
            'predicate': 'last_user_message is not none',
        },
        {
            'id': 2,
            'slug': 'feature2',
            'description': 'Feature 2',
            'type': 'float',
            'is_array': False,
            'domain': '["0.1", "0.2"]',
            'default_value': None,
            'clarification_type': 'from_text',
            'force_question': False,
            'clarifying_question': None,
            'entity_slug': 'entity1',
            'entity_extract_order': 0,
            'is_calculated': False,
            'predicate': None,
        },
        {
            'id': 3,
            'slug': 'feature3',
            'description': 'Feature 3',
            'type': 'str',
            'is_array': True,
            'domain': '[]',
            'default_value': 'default',
            'clarification_type': 'from_text',
            'force_question': True,
            'clarifying_question': 'Clarify question',
            'entity_slug': 'entity2',
            'entity_extract_order': None,
            'is_calculated': False,
            'predicate': None,
        },
        {
            'id': 4,
            'slug': '4',
            'description': 'Feature 3',
            'type': 'str',
            'is_array': False,
            'domain': '[]',
            'default_value': 'default',
            'clarification_type': 'external',
            'force_question': False,
            'clarifying_question': None,
            'entity_slug': None,
            'entity_extract_order': None,
            'is_calculated': False,
            'predicate': None,
        },
    ],
    'lines': [{'id': 1, 'slug': 'line1'}, {'id': 2, 'slug': 'line2'}],
    'scenarios': [
        {
            'id': 1,
            'topic_slug': 'topic1',
            'title': 'Сценарий 1 1й тематики',
            'rule_value': 'feature1 and feature2',
            'reply_macros_text': None,
            'defer_time_sec': 20,
            'line_slug': None,
            'close_status': True,
            'available': True,
            'tags': '["tag1", "tag2"]',
            'features': '["feature2", "feature1"]',
            'actions': '[{"type": "change_state", "features": [{"key": "feature1", "value": "Feature 1"}]}]',  # noqa
            'extra': '{"some": "value"}',
        },
        {
            'id': 2,
            'topic_slug': 'topic3',
            'title': 'Сценарий 1 3й тематики',
            'rule_value': 'True\n||\nFalse',
            'reply_macros_text': 'Спасибо, разберемся',
            'defer_time_sec': None,
            'line_slug': 'line2',
            'close_status': False,
            'available': True,
            'tags': '["tag1", "tag3"]',
            'features': '["feature3"]',
            'actions': '[{"type": "custom", "action_type": "action", "parameters": {"some": "value"}}]',  # noqa
            'extra': None,
        },
        {
            'id': 3,
            'topic_slug': None,
            'title': 'Сценарий c пустыми тегами',
            'rule_value': '1',
            'reply_macros_text': 'Спасибо, разберемся\n||\nДа, ок',
            'defer_time_sec': None,
            'line_slug': '',
            'close_status': False,
            'available': True,
            'tags': '[]',
            'features': '["4"]',
            'actions': '[]',
            'extra': '',
        },
    ],
}


def _patch_records(records: List[dict]):
    for record in records:
        drop_keys = [key for key, value in record.items() if value is None]

        for key in drop_keys:
            record.pop(key)

        record['id'] = str(record['id'])

        if 'parent_id' in record:
            record['parent_id'] = str(record['parent_id'])


@pytest.fixture(name='mock_supportai_responses')
def mock_supportai_exp(mockserver):

    lines = copy.deepcopy(SAMPLE_PROJECT['lines'])
    tags = copy.deepcopy(SAMPLE_PROJECT['tags'])
    features = copy.deepcopy(SAMPLE_PROJECT['features'])
    entities = copy.deepcopy(SAMPLE_PROJECT['entities'])
    topics = copy.deepcopy(SAMPLE_PROJECT['topics'])
    scenarios = copy.deepcopy(SAMPLE_PROJECT['scenarios'])

    _patch_records(lines)
    _patch_records(tags)
    _patch_records(features)
    _patch_records(entities)
    _patch_records(topics)

    for sample_entity in entities:
        extractor = json.loads(sample_entity['extractor'])
        sample_entity['extractor'] = extractor

    tag_slug_map = {tag['slug']: tag for tag in tags}
    entity_slug_map = {entity['slug']: entity for entity in entities}
    feature_slug_map = {feature['slug']: feature for feature in features}
    topic_slug_map = {topic['slug']: topic for topic in topics}

    for sample_feature in features:
        if 'domain' in sample_feature:
            sample_feature['domain'] = json.loads(sample_feature['domain'])

        if 'entity_slug' in sample_feature:
            sample_feature['entity_id'] = entity_slug_map[
                sample_feature['entity_slug']
            ]['id']
            sample_feature.pop('entity_slug')

    @mockserver.json_handler('/supportai/supportai/v1/features')
    async def _features_resp(request):
        return {'features': features}

    @mockserver.json_handler('/supportai/supportai/v1/entities')
    async def _entities_resp(request):
        return {'entities': entities}

    @mockserver.json_handler('/supportai/supportai/v1/tags')
    async def _tags_resp(request):
        return {'tags': tags}

    @mockserver.json_handler('/supportai/supportai/v1/lines')
    async def _lines_resp(request):
        return {'lines': lines}

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {'topics': topics}

    @mockserver.json_handler('/supportai/supportai/v1/scenarios')
    async def _scenarios_resp(request):
        resp_scenarios = []

        for scenario in scenarios:
            scenario_json = {
                'id': str(scenario['id']),
                'title': scenario['title'],
                'available': scenario['available'],
                'rule': {'parts': scenario['rule_value'].split('\n||\n')},
                'clarify_order': [
                    feature_slug_map[feature]
                    for feature in json.loads(scenario['features'])
                ],
                'tags': [
                    tag_slug_map[feature]
                    for feature in json.loads(scenario['tags'])
                ],
            }

            if scenario['extra']:
                scenario_json['extra'] = json.loads(scenario['extra'])

            if scenario['topic_slug']:
                scenario_json['topic_id'] = topic_slug_map[
                    scenario['topic_slug']
                ]['id']

            resp_action = {'type': 'response'}

            if scenario['defer_time_sec'] is not None:
                resp_action['defer_time_sec'] = scenario['defer_time_sec']

            if scenario['line_slug']:
                resp_action['forward_line'] = scenario['line_slug']

            if scenario['reply_macros_text'] is not None:
                resp_action['texts'] = scenario['reply_macros_text'].split(
                    '\n||\n',
                )

            resp_action['close'] = scenario['close_status']

            scenario_json['actions'] = json.loads(scenario['actions']) + [
                resp_action,
            ]

            resp_scenarios.append(scenario_json)

        return {'scenarios': resp_scenarios}


@pytest.fixture(name='run_export_task')
def run_export_task_fixture(
        stq3_context: stq_context.Context, create_task, get_task_file,
):
    async def _run_export_task(skip_id_validation: bool):
        task = create_task(type_='export')

        await runner.task(stq3_context, 'test', task_id=task.id)
        print(task.error_message)
        assert (
            task.status == base_task.TaskStatus.COMPLETED.value
        ), task.error_message
        assert task.file_id is not None

        file_data = get_task_file(task.file_id)

        assert file_data is not None

        all_data = pd.read_excel(
            io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
        )

        for data_name, entities in SAMPLE_PROJECT.items():

            assert data_name in all_data

            data_list = all_data[data_name].to_dict('records')

            for row_num, entity in enumerate(entities):
                data = data_list[row_num]

                for name, value in entity.items():
                    assert (
                        name in data
                    ), f'No field {name} in export data: {data_name}'

                    if skip_id_validation and 'id' in name:
                        continue

                    if value is not None or data[name] != '':
                        assert (
                            data[name] == value
                        ), f'Value of field {name} in data {data_name} is incorrect: {data[name]}. Expected: {value}'  # noqa: E501

    return _run_export_task


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_export_task(run_export_task, mock_supportai_responses):
    await run_export_task(True)


@pytest.fixture(name='run_import_task')
def run_import_task_fixture(
        stq3_context: stq_context.Context, create_task, create_task_file,
):
    async def _run_import_task(data: dict, import_topics: bool = False):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        for name, entities in data.items():
            worksheet = workbook.add_worksheet(name)

            for row_num, entity in enumerate(entities):
                if row_num == 0:
                    for col_num, col_name in enumerate(entity.keys()):
                        worksheet.write(0, col_num, col_name)

                for col_num, item in enumerate(entity.items()):
                    data = item[1]
                    worksheet.write(row_num + 1, col_num, data)

        workbook.close()
        output.seek(0)

        file = create_task_file(
            filename='import.xlsx',
            content_type=constants.XLSX_CONTENT_TYPE,
            content=output.read(),
        )

        task = create_task(type_='import', file_id=file.id)

        await runner.task(
            stq3_context,
            'test',
            task_id=task.id,
            task_args={'import_topics': import_topics},
        )

        return task

    return _run_import_task


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_import_task(
        stq3_context: stq_context.Context,
        mockserver,
        run_import_task,
        run_export_task,
):
    features = []
    entities = []
    tags = []
    lines = []
    topics = copy.deepcopy(SAMPLE_PROJECT['topics'])
    scenarios = []

    _patch_records(topics)

    @mockserver.json_handler('/supportai/supportai/v1/features')
    async def _features_resp(request):
        if request.method == 'POST':
            features.extend(request.json['features'])

        return {'features': features}

    @mockserver.json_handler('/supportai/supportai/v1/entities')
    async def _entities_resp(request):
        if request.method == 'POST':
            entities.extend(request.json['entities'])

        return {'entities': entities}

    @mockserver.json_handler('/supportai/supportai/v1/tags')
    async def _tags_resp(request):
        if request.method == 'POST':
            tags.extend(request.json['tags'])

        return {'tags': tags}

    @mockserver.json_handler('/supportai/supportai/v1/lines')
    async def _lines_resp(request):
        if request.method == 'POST':
            lines.extend(request.json['lines'])

        return {'lines': lines}

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {'topics': topics}

    @mockserver.json_handler('/supportai/supportai/v1/scenarios')
    async def _scenarios_resp(request):
        if request.method == 'POST':

            print(request.json['scenarios'])
            scenarios.extend(request.json['scenarios'])

        return {'scenarios': scenarios}

    @mockserver.json_handler('/supportai/supportai/v1/versions/draft/copy')
    async def _version_hidden_resp(request):
        return {
            'id': '2',
            'hidden': True,
            'draft': True,
            'created': datetime.datetime.now().isoformat(),
            'version': 0,
        }

    @mockserver.json_handler('/supportai/supportai/v1/versions/2/reveal')
    async def _version_reveal_resp(request):
        return {
            'id': '2',
            'hidden': False,
            'draft': True,
            'created': datetime.datetime.now().isoformat(),
            'version': 0,
        }

    @mockserver.json_handler('/supportai/supportai/v1/versions/draft')
    async def _version_draft_resp(request):
        return {
            'id': '1',
            'hidden': False,
            'draft': True,
            'created': datetime.datetime.now().isoformat(),
            'version': 0,
        }

    @mockserver.json_handler('/supportai/supportai/v1/versions/1/draft')
    @mockserver.json_handler('/supportai/supportai/v1/versions/2/draft')
    async def _version_delete_resp(request):
        return {}

    task = await run_import_task(SAMPLE_PROJECT, False)

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), f'Incorrect status, error_message: {task.error_message}'

    await run_export_task(True)


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_import_corrupted_data_task(
        stq3_context: stq_context.Context, run_import_task,
):
    def remove_property(data):
        data['scenarios'][0].pop('title')

    def incorrect_feature_type(data):
        data['features'][0]['type'] = 'incorrect'

    def incorrect_feature_domain(data):
        data['features'][0]['domain'] = 'incorrect'

    def incorrect_data_value(data):
        data['scenarios'][0]['close_status'] = 123

    def remove_data_sheet(data):
        data.pop('tags')

    def incorrect_scenario_line_ref(data):
        data['scenarios'][0]['line_slug'] = 'incorrect'

    def incorrect_scenario_topic_ref(data):
        data['scenarios'][0]['topic_slug'] = 'incorrect'

    def incorrect_scenario_tag_ref(data):
        data['scenarios'][0]['tags'] = 'tag1,incorrect'

    def incorrect_scenario_feature_ref(data):
        data['scenarios'][0]['features'] = 'feature1,incorrect'

    def incorrect_scenario_rule(data):
        data['scenarios'][0]['rule_value'] = 'a abracadabra b'

    def incorrect_topics(data):
        data['topics'][0]['parent_id'] = 2

    def incorrect_topic_parent(data):
        data['topics'][2]['parent_id'] = 10

    for corruption_actions in (
            remove_property,
            incorrect_feature_type,
            incorrect_feature_domain,
            incorrect_data_value,
            remove_data_sheet,
            incorrect_scenario_line_ref,
            incorrect_scenario_topic_ref,
            incorrect_scenario_tag_ref,
            incorrect_scenario_feature_ref,
            incorrect_scenario_rule,
            incorrect_topics,
            incorrect_topic_parent,
    ):
        new_data = copy.deepcopy(SAMPLE_PROJECT)
        corruption_actions(new_data)

        task = await run_import_task(new_data, import_topics=True)

        assert task.status == base_task.TaskStatus.ERROR.value
