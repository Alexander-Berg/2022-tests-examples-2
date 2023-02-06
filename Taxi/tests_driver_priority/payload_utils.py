import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


_COLOR_WHITE = '#FFFFFF'
_COLOR_LIGHT_GRAY = '#C4C2BE'
_COLOR_GRAY = '#9E9B98'
_COLOR_DARK_GRAY = '#21201F'
_COLOR_LIGHT_RED = '#F5523A'
_COLOR_DARK_RED = '#FA3E2C'
_COLOR_YELLOW = '#FCB000'

_COLOR_MINOR_TEXT = 'minor_text'
_COLOR_MAIN_TEXT = 'main_text'
_COLOR_MAIN_ICON = 'main_icon'


@dataclasses.dataclass
class RankedPriority:
    priority: int
    tag_value: str
    text: str


def _header_payload(payload_header, payload_text):
    items = [
        {
            'type': 'header',
            'subtitle': payload_header,
            'center': False,
            'horizontal_divider_type': 'none',
        },
        {
            'type': 'text',
            'text': payload_text,
            'horizontal_divider_type': 'none',
        },
    ]
    _ui = {'primary': {'items': items}}
    return {'type': 'navigate_priority_description', 'ui': _ui}


def _ui_left_tip_icon_item(
        is_disabled: bool, is_negative: bool, is_new_icon: bool,
):
    item = {'tint_color': _COLOR_WHITE}

    icon_type = 'check'
    if is_disabled:
        icon_type = 'lock'
    elif is_negative:
        icon_type = 'warning4' if is_new_icon else 'minus'

    item['icon_type'] = icon_type

    return item


def get_ranked_payload(
        subtitle: str,
        main_title: str,
        priorities: List[RankedPriority],
        matched_item_index: int,
        has_button=True,
):
    ranked_items = [
        {
            'detail': priority.text,
            'horizontal_divider_type': 'none',
            'id': f'generated_id_{i+1}',
            'left_tip': {
                'background_color': (
                    'main_line' if i < matched_item_index else 'main_control'
                ),
                'icon': {
                    'tint_color': 'main_bg',
                    'icon_type': (
                        'circle_18' if i < matched_item_index else 'check'
                    ),
                },
            },
            'primary_text_color': (
                'main_text' if i == matched_item_index else 'minor_text'
            ),
            'detail_primary_text_color': (
                'main_text' if i == matched_item_index else 'minor_text'
            ),
            'title': '{sign}{priority}'.format(
                sign='+' if priority.priority > 0 else '',
                priority=priority.priority,
            ),
            'accent_title': True,
            'type': 'tip_line_detail',
        }
        for i, priority in enumerate(priorities)
    ]

    # fill colors on items scale
    for i in range(len(priorities)):
        update = {}
        if i + 1 < len(priorities):
            update['bottom_line'] = {
                'color': (
                    'main_line' if i < matched_item_index else 'main_control'
                ),
            }
        if i > 0:
            update['top_line'] = {
                'color': (
                    'main_line' if i <= matched_item_index else 'main_control'
                ),
            }
        ranked_items[i].update(update)

    ranked_items.append(
        {
            'horizontal_divider_type': 'bottom_gap',
            'text': main_title,
            'type': 'text',
        },
    )

    result = {
        'type': 'navigate_priority_details',
        'ui': {'primary': {'items': ranked_items}},
        'title': subtitle,
    }
    if has_button:
        result.update(
            {
                'secondary_button_title': 'Это кнопка',
                'secondary_button_payload': {
                    'type': 'navigate_url',
                    'url': 'ya.ru',
                    'title': 'Это ссылка',
                    'is_external': True,
                },
            },
        )
    return result


def get_payload(subtitle, text):
    return {
        'type': 'navigate_priority_details',
        'ui': {
            'primary': {
                'items': [
                    {
                        'horizontal_divider_type': 'none',
                        'subtitle': subtitle,
                        'gravity': 'left',
                        'type': 'header',
                    },
                    {
                        'horizontal_divider_type': 'none',
                        'text': text,
                        'type': 'text',
                    },
                ],
            },
        },
        'button_title': 'Это кнопка',
        'button_payload': {
            'type': 'navigate_url',
            'url': 'ya.ru',
            'title': 'Это ссылка',
            'is_external': True,
        },
    }


def get_activity_payload(items):
    return {
        'type': 'navigate_priority_details',
        'ui': {'primary': {'items': items}},
        'title': 'Для тестов',
    }


def ui_header_item(
        title='Высокий приоритет',
        subtitle='Все заказы для вас одного',
        payload_header='Приоритет',
        payload_text='У вас обычный приоритет',
        is_new_radar_ui: bool = False,
):
    return {
        'type': 'default',
        'title': title,
        'subtitle': subtitle,
        'accent': True,
        'center': not is_new_radar_ui,
        'right_icon': 'navigate',
        'payload': _header_payload(payload_header, payload_text),
        'horizontal_divider_type': ('top_gap' if is_new_radar_ui else 'none'),
    }


def ui_priority_item(
        priority: int,
        title: str,
        subtitle: Optional[str],
        is_matched: bool,
        is_disabled=False,
        is_temporary=False,
        payload=None,
        new_icon=False,
        ranker_priority_max_value: Optional[int] = None,
        use_new_divider_type: bool = False,
):
    is_negative = priority < 0
    result: Dict[str, Any] = {
        'type': 'tip_detail',
        'detail': '{sign}{priority}'.format(
            sign='+' if priority > 0 else '', priority=priority,
        ),
        'accent': True,
        'horizontal_divider_type': (
            'top_bold_s' if use_new_divider_type else 'top_gap'
        ),
        'left_tip': {
            'background_color': (
                _COLOR_LIGHT_GRAY
                if is_disabled
                else _COLOR_LIGHT_RED
                if is_negative
                else _COLOR_YELLOW
            ),
            'icon': _ui_left_tip_icon_item(is_disabled, is_negative, new_icon),
        },
        'right_icon': 'navigate',
        'title': title,
    }
    if ranker_priority_max_value is not None:
        result['subdetail'] = f'из {ranker_priority_max_value}'
        result['detail_secondary_text_color'] = _COLOR_MINOR_TEXT

    if subtitle:
        result['subtitle'] = subtitle

    if is_temporary:
        result['left_tip']['animated'] = True

    if not is_matched:
        result['primary_text_color'] = _COLOR_MINOR_TEXT
        result['detail_primary_text_color'] = _COLOR_MINOR_TEXT
        result['right_icon_color'] = _COLOR_MAIN_ICON
    elif is_negative:
        result['right_icon_color'] = _COLOR_DARK_RED
        result['primary_text_color'] = _COLOR_DARK_RED
        result['detail_primary_text_color'] = _COLOR_DARK_RED
    else:
        result['primary_text_color'] = _COLOR_MAIN_TEXT
        result['detail_primary_text_color'] = _COLOR_MAIN_TEXT
        result['right_icon_color'] = _COLOR_MAIN_ICON

    if payload is not None:
        result['payload'] = payload

    return result
