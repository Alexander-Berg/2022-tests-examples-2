import pathlib
import typing

from testsuite.utils import yaml_util


def load_all_widget_types(source_dir) -> typing.Set[str]:
    widgets: typing.Set[str] = set()

    widgets_dir: pathlib.Path = source_dir / 'src/widgets'

    for file_path in widgets_dir.iterdir():
        if not file_path.is_dir():
            continue

        meta_yaml = file_path / 'meta.yaml'
        if not meta_yaml.is_file():
            continue

        data = yaml_util.load_file(meta_yaml)
        if 'widget' not in data:
            raise Exception(
                f'Invalid widget {meta_yaml}: missing required field "widget"',
            )

        widget = data['widget']
        if widget != 'layout_widget':
            widgets.add(data['widget'])

    return widgets


def get_field(data: dict, path: typing.List[str]):
    if not path:
        return data

    value = data
    for item in path:
        if item not in value:
            raise Exception(
                f'cannot get field at path {path}: missing {item} field',
            )

        value = value[item]

    return value


async def test_get_widget_templates_types(
        taxi_eats_layout_constructor, service_source_dir,
):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/widget-templates/types/',
    )
    types = {
        template_type['type'] for template_type in response.json()['types']
    }

    assert types == load_all_widget_types(service_source_dir)


async def test_widget_templates_spec(service_source_dir):
    """
    Проверяет, что в спеке сервиса перечислены все типы виджетов
    """

    spec_file = (
        service_source_dir / 'docs/yaml/api/constructor_widget_templates.yaml'
    )
    assert spec_file.is_file()

    data = yaml_util.load_file(spec_file)
    spec_types = set(
        get_field(data, ['components', 'schemas', 'WidgetType', 'enum']),
    )

    widgets = load_all_widget_types(service_source_dir)
    # Добавляем виждеты коллекций, которые не являются самостоятельными
    widgets.add('collection_carousel')
    widgets.add('view_header')

    assert widgets == spec_types
