JS = """
function init(json_template) {
    template = nunjucks.compile(json_template)
}

function main(user_data) {
    return template.render(user_data)
}
"""

TIMES = 5
COUNT = 100

JSON_TEMPLATE_DICT = """
{
{% set comma = joiner() %}
{% for item in items -%}
  {{ comma() }} "{{ item.key }}": "{{ item.value }}"
{%- endfor %}
}
"""

JSON_TEMPLATE_LIST = """
[
{% set comma = joiner() %}
{% for item in items -%}
  {{ comma() }} "{{ item }}"
{%- endfor %}
]
"""


async def test_basic_dict(taxi_grocery_pro_bdu, testpoint):
    user_data = {
        'items': [
            {'key': f'key{i}', 'value': f'value{i}'} for i in range(COUNT)
        ],
    }
    expected_result = {f'key{i}': f'value{i}' for i in range(COUNT)}

    task_names = []

    @testpoint('js_task_initialize')
    def _js_task_initialize(data):
        nonlocal task_names
        task_names.append(data['task_name'])

    for i in range(TIMES):
        body = {
            'task_name': f'dict{i}',
            'code': JS,
            'json_template': JSON_TEMPLATE_DICT,
            'user_data': user_data,
            'init': 'init',
            'main': 'main',
        }
        response = await taxi_grocery_pro_bdu.post(
            '/driver/v1/grocery-pro-bdu/v1/test/js-engine', json=body,
        )
        assert response.status_code == 200

        response = response.json()
        assert response['result'] == expected_result

    assert (
        task_names == ['dict0', 'dict1'][:TIMES]
    )  # len is min(TIMES, $v8_task_processor_threads)


async def test_basic_list(taxi_grocery_pro_bdu, testpoint):
    user_data = {'items': [f'value{i}' for i in range(COUNT)]}
    expected_result = user_data['items']

    task_names = []

    @testpoint('js_task_initialize')
    def _js_task_initialize(data):
        nonlocal task_names
        task_names.append(data['task_name'])

    for i in range(TIMES):
        body = {
            'task_name': f'list{i}',
            'code': JS,
            'json_template': JSON_TEMPLATE_LIST,
            'user_data': user_data,
            'init': 'init',
            'main': 'main',
        }
        response = await taxi_grocery_pro_bdu.post(
            '/driver/v1/grocery-pro-bdu/v1/test/js-engine', json=body,
        )
        assert response.status_code == 200

        response = response.json()

        assert response['result'] == expected_result

    assert (
        task_names == ['list0', 'list1'][:TIMES]
    )  # len is min(TIMES, $v8_task_processor_threads)
