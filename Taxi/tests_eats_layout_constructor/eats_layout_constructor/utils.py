import base64
import copy
import dataclasses
import json
import typing

import psycopg2

# pylint: disable=import-error
from eats_analytics import eats_analytics

EATER_ID = '12345'


def order_stats_response(retail_orders_count=0, restaurant_orders_count=0):
    counters = []

    if retail_orders_count != 0:
        counters.append(
            {
                'first_order_at': '2021-08-19T13:04:05+0000',
                'last_order_at': '2021-09-19T13:04:05+0000',
                'properties': [
                    {'name': 'brand_id', 'value': '1'},
                    {'name': 'business_type', 'value': 'retail'},
                    {'name': 'delivery_type', 'value': 'native'},
                    {'name': 'place_id', 'value': '1'},
                ],
                'value': retail_orders_count,
            },
        )
    if restaurant_orders_count != 0:
        counters.append(
            {
                'first_order_at': '2021-08-19T13:04:05+0000',
                'last_order_at': '2021-09-19T13:04:05+0000',
                'properties': [
                    {'name': 'brand_id', 'value': '1'},
                    {'name': 'business_type', 'value': 'restaurant'},
                    {'name': 'delivery_type', 'value': 'native'},
                    {'name': 'place_id', 'value': '1'},
                ],
                'value': restaurant_orders_count,
            },
        )

    return {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': EATER_ID},
                'counters': counters,
            },
        ],
    }


class MatchingSet:
    def __init__(self, values: typing.List):
        self._set: typing.Set = set(values)

    def __repr__(self):
        return self._set

    def __eq__(self, other):
        return self._set == set(other)


@dataclasses.dataclass
class MetaWidget:
    type: str
    slug: str
    name: str
    settings: typing.Dict
    meta_widget_id: typing.Optional[int] = None


@dataclasses.dataclass
class Layout:
    layout_id: int
    name: str
    slug: str


@dataclasses.dataclass
class WidgetTemplate:
    widget_template_id: int
    type: str
    name: str
    meta: typing.Dict
    payload: typing.Dict
    payload_schema: typing.Dict


@dataclasses.dataclass
class LayoutWidget:
    name: str
    widget_template_id: int
    layout_id: int
    meta: typing.Dict
    payload: typing.Dict
    meta_widget_id: typing.Optional[int] = None
    url_id: typing.Optional[int] = None


@dataclasses.dataclass
class Widget:
    name: str
    type: str
    meta: typing.Dict
    payload: typing.Optional[typing.Dict] = None
    payload_schema: typing.Optional[typing.Dict] = None
    meta_widget: typing.Optional[MetaWidget] = None


def find_widget_payload(widget_id: str, collections: list):
    for collection in collections:
        if collection['id'] == widget_id:
            return collection['payload']

    assert False, 'could not find payload for widget_id={}'.format(widget_id)
    return None


def decode_widget_payload(widgets: typing.Dict) -> dict:
    """
    Получает typing.Dict с payload-ом виджета,
    возвращате тот же payload, но поле context
    расшифровано из base64 в объект
    """
    result = copy.deepcopy(widgets)
    for place in result['places']:
        encoded_value = place['context']
        context = json.loads(base64.b64decode(encoded_value))
        place['context'] = context
        if 'analytics' in place:
            place['analytics'] = eats_analytics.decode(place['analytics'])
    return result


def create_layout(pgsql, slug: str, widgets: typing.List[Widget]):
    layout = add_layout(pgsql, Layout(layout_id=0, name=slug, slug=slug))

    for widget in widgets:
        template = add_widget_template(
            pgsql,
            WidgetTemplate(
                widget_template_id=0,
                type=widget.type,
                name=widget.name + '_template',
                meta={},
                payload={},
                payload_schema=widget.payload_schema
                if widget.payload_schema
                else {},
            ),
        )

        meta_widget_id: typing.Optional[int] = None
        if widget.meta_widget is not None:
            widget.meta_widget = add_meta_widget(pgsql, widget.meta_widget)
            meta_widget_id = widget.meta_widget.meta_widget_id

        add_widget(
            pgsql,
            LayoutWidget(
                name=widget.name,
                widget_template_id=template.widget_template_id,
                layout_id=layout.layout_id,
                meta=widget.meta if widget.meta else {},
                payload=widget.payload if widget.payload else {},
                meta_widget_id=meta_widget_id,
            ),
        )


def add_layout(pgsql, layout: Layout) -> Layout:
    cursor = pgsql['eats_layout_constructor'].cursor()
    if layout.layout_id > 0:
        cursor.execute(
            """
            INSERT INTO constructor.layouts (
                id,
                name,
                slug,
                author
            ) VALUES (
                %s,
                %s,
                %s,
                'testsuite'
            )
            """,
            (layout.layout_id, layout.name, layout.slug),
        )
        return layout

    cursor.execute(
        """
        INSERT INTO constructor.layouts (
            name,
            slug,
            author
        ) VALUES (
            %s,
            %s,
            'testsuite'
        ) RETURNING id
        """,
        (layout.name, layout.slug),
    )
    layout.layout_id = cursor.fetchone()[0]
    return layout


def add_widget_template(
        pgsql, widget_template: WidgetTemplate,
) -> WidgetTemplate:
    cursor = pgsql['eats_layout_constructor'].cursor()
    if widget_template.widget_template_id > 0:
        cursor.execute(
            """
            INSERT INTO constructor.widget_templates (
                id,
                type,
                name,
                meta,
                payload,
                payload_schema
            ) VALUES (
                %s,
                %s,
                %s,
                %s::jsonb,
                %s::jsonb,
                %s::jsonb
            )
            """,
            (
                widget_template.widget_template_id,
                widget_template.type,
                widget_template.name,
                json.dumps(widget_template.meta),
                json.dumps(widget_template.payload),
                json.dumps(widget_template.payload_schema),
            ),
        )
        return widget_template

    cursor.execute(
        """
        INSERT INTO constructor.widget_templates (
            type,
            name,
            meta,
            payload,
            payload_schema
        ) VALUES (
            %s,
            %s,
            %s::jsonb,
            %s::jsonb,
            %s::jsonb
        ) RETURNING id
        """,
        (
            widget_template.type,
            widget_template.name,
            json.dumps(widget_template.meta),
            json.dumps(widget_template.payload),
            json.dumps(widget_template.payload_schema),
        ),
    )

    widget_template.widget_template_id = cursor.fetchone()[0]
    return widget_template


def add_widget(pgsql, layout_widget: LayoutWidget):

    cursor = pgsql['eats_layout_constructor'].cursor()
    cursor.execute(
        """
        INSERT INTO constructor.layout_widgets (
            name,
            url_id,
            widget_template_id,
            layout_id,
            meta,
            payload,
            meta_widget
        ) VALUES (
            %s,
            COALESCE(%s, nextval('constructor.layout_widgets_url_id_seq')),
            %s,
            %s,
            %s::jsonb,
            %s::jsonb,
            %s
        )
        """,
        (
            layout_widget.name,
            layout_widget.url_id,
            layout_widget.widget_template_id,
            layout_widget.layout_id,
            json.dumps(layout_widget.meta),
            json.dumps(layout_widget.payload),
            layout_widget.meta_widget_id,
        ),
    )


def add_meta_widget(pgsql, meta_widget: MetaWidget) -> MetaWidget:
    cursor = pgsql['eats_layout_constructor'].cursor()
    if meta_widget.meta_widget_id is not None:
        try:
            cursor.execute(
                """
                INSERT INTO constructor.meta_widgets (
                    id,
                    type,
                    slug,
                    name,
                    settings
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s::jsonb
                )
                """,
                (
                    meta_widget.meta_widget_id,
                    meta_widget.type,
                    meta_widget.slug,
                    meta_widget.name,
                    json.dumps(meta_widget.settings),
                ),
            )
        except psycopg2.IntegrityError:
            pass

        return meta_widget

    cursor.execute(
        """
        INSERT INTO constructor.meta_widgets (
            type,
            slug,
            name,
            settings
        ) VALUES (
            %s,
            %s,
            %s,
            %s::jsonb
        ) RETURNING id
        """,
        (
            meta_widget.type,
            meta_widget.slug,
            meta_widget.name,
            json.dumps(meta_widget.settings),
        ),
    )

    meta_widget.meta_widget_id = cursor.fetchone()[0]
    return meta_widget


def assert_request_block(data: dict, block_id: str, expected: dict):
    blocks: typing.List[str] = []
    for block in data['blocks']:
        blocks.append(block['id'])
        if block['id'] == block_id:
            assert block == expected
            return
    assert False, f'missing block with id {block_id}, got {blocks}'
