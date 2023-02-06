# pylint: disable=too-many-lines
import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


BLOCK_TITLE_KEY = 'some_tanker_key'
BLOCK_TITLE_VALUE = 'some tanker value'
BLOCK_TRANSLATED_TITLE = 'some value that already translated'

DEFAULT_ATTRIBUTED_TEXT_HEADER: dict = {
    'title': {
        'items': [
            {
                'type': 'text',
                'text': BLOCK_TITLE_VALUE,
                'font_size': 14,
                'font_weight': 'regular',
                'font_style': 'normal',
                'color': '#000000',
            },
        ],
    },
}
TANKER_ATTRIBUTED_TEXT_HEADER: dict = {
    'title': {
        'items': [
            {
                'color': '#AABBCC',
                'font_size': 1,
                'font_style': 'normal',
                'font_weight': 'medium',
                'meta_style': 'title-semibold',
                'text': 'aweq',
                'type': 'text',
            },
            {
                'text': {
                    'color': '#AABBCC',
                    'font_size': 1,
                    'font_style': 'normal',
                    'font_weight': 'medium',
                    'meta_style': 'title-semibold',
                    'text': 'hello',
                    'type': 'text',
                },
                'type': 'link',
                'link': 'hi.ru',
            },
            {
                'color': '#AABBCC',
                'font_size': 1,
                'font_style': 'normal',
                'font_weight': 'medium',
                'meta_style': 'title-semibold',
                'text': 'weqwe',
                'type': 'text',
            },
        ],
    },
}
NATIVE_SECTION_TITLE_PARAMS = {
    'font_size': 14,
    'font_weight': 'regular',
    'font_style': 'normal',
    'color': '#000000',
    'enabled': True,
}


def get_typed_header(expected=False):
    if expected:
        lead_text = 'ololo'
        trail_text = 'trail_text'
    else:
        lead_text = {'text': 'ololo'}
        trail_text = {'text': 'trail_text'}

    return {
        'type': 'list_item',
        'lead': {
            'type': 'app_title',
            'title': {'text': lead_text},
            'icon_tag': 'default_icon_tag',
        },
        'trail': {
            'type': 'subtitle',
            'title': {
                'attributed_text': {
                    'items': [
                        {
                            'type': 'image',
                            'image_tag': 'default_image_tag',
                            'width': 100,
                        },
                        {
                            'type': 'text',
                            'text': trail_text,
                            'font_size': 20,
                            'font_weight': 'bold',
                            'font_style': 'normal',
                            'color': '#9E9B98',
                        },
                    ],
                },
            },
        },
    }


@pytest.mark.parametrize('block_slugs', (['organic'], ['organic', 'other']))
async def test_blocks_as_sections(taxi_shortcuts, block_slugs):
    blocks = []
    request_shortcuts = []
    expected_sections = []
    for block_slug in block_slugs:
        block_shortcuts = [
            {
                **copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT),
                **{'id': f'{block_slug}_{i}'},
            }
            for i in range(3)
        ]
        shortcut_ids = [bs['id'] for bs in block_shortcuts]
        request_shortcuts.extend(block_shortcuts)
        block = {
            'id': 'block_id_does_not_matter',
            'slug': block_slug,
            'shortcut_ids': shortcut_ids,
        }
        blocks.append(block)
        expected_sections.append(
            {
                'type': 'items_linear_grid',
                'shortcut_ids': block['shortcut_ids'],
            },
        )
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=blocks,
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert data['sections'] == expected_sections


SEPARATOR_TANKER_KEY = 'shortcuts_separator'


def build_separator(
        shortcut_id,
        title_tk=SEPARATOR_TANKER_KEY,
        width=6,
        height=1,
        deeplink='',
):
    return {
        'shortcut_id': shortcut_id,
        'title_tanker_key': title_tk,
        'width': width,
        'height': height,
        'background_color': '#FFFFFF',
        'deeplink': deeplink,
    }


@pytest.mark.translations(
    client_messages={
        consts.DELIVERY_TIME_KEY: consts.DELIVERY_TIME_TEMPLATES,
        consts.EATS_TANKER_KEY: {'ru': 'badge_text'},
        SEPARATOR_TANKER_KEY: {'ru': 'separator_title'},
    },
)
async def test_blocks(taxi_shortcuts, add_experiment):
    # setup badges to test them later

    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {
            'badges': {
                'eats:place': {
                    '__default__': helpers.make_default_badge(
                        shape='bubble', tanker_key=consts.EATS_TANKER_KEY,
                    ),
                },
            },
        },
    )

    blocks_experiment_value = {
        # Add separators
        'organic': {
            'before_separators': [
                build_separator('before_0'),
                build_separator('before_1'),
            ],
            'after_separators': [
                build_separator('after_0'),
                build_separator('after_1'),
            ],
        },
    }
    add_experiment(consts.BLOCKS_EXPERIMENT, blocks_experiment_value)
    blocks = []
    request_shortcuts = []
    separators_before_shortcut = {}  # shortcut_id: [separators]
    separators_after_shortcut = {}
    for block_type, block_value in blocks_experiment_value.items():
        # build shortcut for request
        block_shortcuts = [
            {
                **copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT),
                **{'id': f'{block_type}_{i}'},
            }
            for i in range(3)
        ]
        shortcut_ids = [bs['id'] for bs in block_shortcuts]
        request_shortcuts.extend(block_shortcuts)
        blocks.append(
            {
                'id': 'block_id_does_not_matter',
                'slug': block_type,
                # IMPORTANT: reverse blocks to ensure sort in shortcuts
                'shortcut_ids': list(reversed(shortcut_ids)),
            },
        )
        before_separators = block_value.get('before_separators')
        if before_separators:
            separators_before_shortcut[shortcut_ids[0]] = before_separators
        after_separators = block_value.get('after_separators')
        if after_separators:
            separators_after_shortcut[shortcut_ids[-1]] = after_separators

    # we need unique ids for blocks testing
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts, blocks=blocks,
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()

    shortcuts = data['offers']['items']

    # check separators
    def check_separators(shortcut_id):
        def compare_separators(sid, result_seps, expected_seps):
            assert len(result_seps) == len(expected_seps), sid
            for got, expected in zip(result_seps, expected_seps):
                for field in ('shortcut_id', 'height', 'width'):
                    assert got[field] == expected[field]
                assert got['title'] == 'separator_title'
                assert got['action']['deeplink'] == expected['deeplink']
                assert (
                    got['background']['color'] == expected['background_color']
                )

        # find index of a shortcut in response array
        index = [
            i
            for i, rs in enumerate(shortcuts)
            if rs['shortcut_id'] == shortcut_id
        ][0]

        # check elements before and after it, they should be separators
        if shortcut_id in separators_before_shortcut:
            expected_seps = separators_before_shortcut[shortcut_id]
            result_separators = shortcuts[index - len(expected_seps) : index]
            compare_separators(shortcut_id, result_separators, expected_seps)
        if shortcut_id in separators_after_shortcut:
            expected_seps = separators_after_shortcut[shortcut_id]
            result_separators = shortcuts[
                index + 1 : index + len(expected_seps) + 1
            ]
            compare_separators(shortcut_id, result_separators, expected_seps)

    for result_shortcut in shortcuts:
        check_separators(result_shortcut['shortcut_id'])


@pytest.mark.translations(
    client_messages={SEPARATOR_TANKER_KEY: {'ru': 'separator_title'}},
)
async def test_pseudobuttons_sections(taxi_shortcuts, add_experiment):
    before_seaparator_id = 'before_sep_id'
    after_separator_id = 'after_sep_id'
    shortcut = copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)
    shortcut_id = consts.DEFAULT_EATS_SHORTCUT['id']
    blocks_experiment_value = {
        # Add separators
        'organic': {
            'before_separators': [build_separator(before_seaparator_id)],
            'after_separators': [build_separator(after_separator_id)],
        },
    }
    add_experiment(consts.BLOCKS_EXPERIMENT, blocks_experiment_value)
    request_shortcuts = [shortcut]
    blocks = [
        {
            'id': 'block_id_does_not_matter',
            'slug': 'organic',
            'shortcut_ids': [shortcut_id],
        },
    ]
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=blocks,
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    assert data['sections'][0]['shortcut_ids'] == [
        before_seaparator_id,
        shortcut_id,
        after_separator_id,
    ]


async def test_unknown_block_slug(taxi_shortcuts, add_experiment):
    block_slug = 'random_slug'
    request_shortcuts = []
    expected_sections = []
    block_shortcuts = [
        {
            **copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT),
            **{'id': f'{block_slug}_{i}'},
        }
        for i in range(3)
    ]
    # imitate that blocks_experiment has matched, but has no slugs in it
    add_experiment(consts.BLOCKS_EXPERIMENT, {})
    shortcut_ids = [bs['id'] for bs in block_shortcuts]
    request_shortcuts.extend(block_shortcuts)
    block = {
        'id': 'block_id_does_not_matter',
        'slug': block_slug,
        'shortcut_ids': shortcut_ids,
    }
    expected_sections.append(
        {'type': 'items_linear_grid', 'shortcut_ids': block['shortcut_ids']},
    )
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert data['sections'] == expected_sections


@pytest.mark.parametrize(
    'exp_matched,pseudotitle_enabled',
    [(True, True), (True, False), (False, True)],
)
@pytest.mark.parametrize('use_translated_title', [True, False])
@pytest.mark.translations(
    client_messages={BLOCK_TITLE_KEY: {'ru': BLOCK_TITLE_VALUE}},
)
async def test_block_title(
        taxi_shortcuts,
        add_experiment,
        exp_matched,
        pseudotitle_enabled,
        use_translated_title,
):
    # receiving title_key for block should insert pseudoshortcut with
    # translation
    pseudotitle_props = {
        'background_color': '#ffffff',
        'deeplink': 'yandextaxi://',
    }
    block_id = 'some_block_id'
    if exp_matched:
        add_experiment(
            consts.COLLECTION_PSEUDOTITLE_PARAMS,
            {**pseudotitle_props, 'enabled': pseudotitle_enabled},
        )
    request_shortcuts = [copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)]
    block = {
        'id': block_id,
        'slug': 'random_slug',
        'shortcut_ids': [bs['id'] for bs in request_shortcuts],
        'title_key': BLOCK_TITLE_KEY,
    }
    if use_translated_title:
        block.update({'title': BLOCK_TRANSLATED_TITLE})
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    if not (exp_matched and pseudotitle_enabled):
        assert len(data['sections'][0]['shortcut_ids']) == 1
        shortcut = data['offers']['items'][0]
        assert shortcut['shortcut_id'] == consts.DEFAULT_EATS_SHORTCUT['id']
        return

    assert len(data['sections'][0]['shortcut_ids']) == 2
    pseudoshortcut = data['offers']['items'][0]
    pseudoshortcut.pop('shortcut_id')
    expected_title = (
        BLOCK_TRANSLATED_TITLE if use_translated_title else BLOCK_TITLE_VALUE
    )
    assert pseudoshortcut == {
        'title': expected_title,
        'type': 'deeplink',
        'width': 6,
        'height': 1,
        'background': {'color': pseudotitle_props['background_color']},
        'action': {'deeplink': pseudotitle_props['deeplink']},
    }


@pytest.mark.parametrize(
    'exp_matched,native_title_enabled',
    [(True, True), (True, False), (False, True)],
)
@pytest.mark.translations(
    client_messages={BLOCK_TITLE_KEY: {'ru': BLOCK_TITLE_VALUE}},
)
async def test_native_block_title(
        taxi_shortcuts, add_experiment, exp_matched, native_title_enabled,
):
    native_section_title_params = {
        'font_size': 14,
        'font_weight': 'regular',
        'font_style': 'normal',
        'color': '#000000',
        'enabled': native_title_enabled,
    }
    block_id = 'some_block_id'
    if exp_matched:
        add_experiment(
            consts.NATIVE_SECTION_TITLE_PARAMS, native_section_title_params,
        )
    request_shortcuts = [copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)]
    block = {
        'id': block_id,
        'slug': 'random_slug',
        'shortcut_ids': [bs['id'] for bs in request_shortcuts],
        'title_key': BLOCK_TITLE_KEY,
    }
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    section = data['sections'][0]
    if not (exp_matched and native_title_enabled):
        assert 'header' not in section
        return

    assert section['header'] == DEFAULT_ATTRIBUTED_TEXT_HEADER


@pytest.mark.config(
    EXTENDED_TEMPLATE_STYLES_MAP={
        'custom_style': {
            'font_size': 1,
            'font_weight': 'medium',
            'font_style': 'normal',
            'color': '#AABBCC',
            'meta_style': 'title-semibold',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'existing_tanker_key': {
            'ru': (
                '<custom_style>aweq'
                '<a href="hi.ru">hello</a>weqwe</custom_style>'
            ),
        },
        BLOCK_TITLE_KEY: {'ru': BLOCK_TITLE_VALUE},
    },
)
@pytest.mark.parametrize(
    'attr_text_tanker_key, extected_attr_text',
    [
        ('existing_tanker_key', TANKER_ATTRIBUTED_TEXT_HEADER),
        ('unknown_tanker_key', DEFAULT_ATTRIBUTED_TEXT_HEADER),
    ],
)
async def test_tanker_header_attributed_text(
        taxi_shortcuts,
        add_experiment,
        attr_text_tanker_key,
        extected_attr_text,
):
    native_section_title_params = {
        'use_at_from_tanker': attr_text_tanker_key,
        'font_size': 14,
        'font_weight': 'regular',
        'font_style': 'normal',
        'color': '#000000',
        'enabled': True,
    }
    add_experiment(
        consts.NATIVE_SECTION_TITLE_PARAMS, native_section_title_params,
    )
    request_shortcuts = [copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)]
    block = {
        'id': 'some_block_id',
        'slug': 'random_slug',
        'shortcut_ids': [bs['id'] for bs in request_shortcuts],
        'title_key': BLOCK_TITLE_KEY,
    }
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    section = data['sections'][0]
    assert section['header'] == extected_attr_text


@pytest.mark.parametrize(
    'block_slug,expected_tags',
    [('organic', ['grey_separator', 'random_tag']), ('media', None)],
)
async def test_section_tags(
        taxi_shortcuts, add_experiment, block_slug, expected_tags,
):
    add_experiment(
        consts.BLOCKS_EXPERIMENT,
        {'organic': {'tags': ['grey_separator', 'random_tag']}},
    )
    request_shortcuts = [copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)]
    block = {
        'id': 'block_id_is_irrelevant',
        'slug': block_slug,
        'shortcut_ids': [bs['id'] for bs in request_shortcuts],
        'title_key': BLOCK_TITLE_KEY,
    }
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': 'items_linear_grid'}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    section = data['sections'][0]
    assert section.get('tags') == expected_tags


@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize('send_supported_sections', [False, True])
async def test_sections(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        send_supported_sections,
        expect_buttons,
):
    add_appearance_experiments()
    env = helpers.EnvSetup()

    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    else:
        env.header_params_experiment['buttons']['show_from'] = 10
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    supported_sections = (
        env.all_supported_sections if send_supported_sections else None
    )
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_sections=supported_sections,
        supported_actions=env.all_supported_actions,
        cells=[
            {
                'height': 2,
                'width': 2,
                'shortcut': consts.DEFAULT_TAXI_SHORTCUT,
            },
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    offers = data['offers']

    bricks_section = {
        'shortcut_ids': [b['shortcut_id'] for b in offers.get('header', [])],
        'type': 'header_linear_grid',
    }

    buttons_section = {
        'button_ids': [b['id'] for b in offers.get('buttons', [])],
        'type': 'buttons_container',
    }

    shortcuts_section = {
        'shortcut_ids': [s['shortcut_id'] for s in offers.get('items', [])],
        'type': 'items_linear_grid',
    }

    expected_sections = (
        [buttons_section, shortcuts_section]
        if expect_buttons
        else [bricks_section, shortcuts_section]
    )

    assert data.get('sections', {}) == (
        expected_sections if send_supported_sections else {}
    )


@pytest.mark.parametrize(
    'supported_section',
    ['items_linear_grid', 'items_horizontal_scrollable_grid'],
)
@pytest.mark.parametrize('has_typed_header', [True, False])
async def test_section_blocks_appearance_overrides(
        taxi_shortcuts, add_experiment, supported_section, has_typed_header,
):
    blocks_exp_value = {
        'organic': {'title': 'ololo', 'section_type': supported_section},
    }
    if has_typed_header:
        blocks_exp_value['organic']['typed_header'] = get_typed_header()
    add_experiment(consts.BLOCKS_EXPERIMENT, blocks_exp_value)
    add_experiment(consts.BLOCKS_EXPERIMENT, blocks_exp_value)
    add_experiment(
        consts.NATIVE_SECTION_TITLE_PARAMS, NATIVE_SECTION_TITLE_PARAMS,
    )
    request_shortcuts = [copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)]
    block = {
        'id': 'block_id_is_irrelevant',
        'slug': 'organic',
        'shortcut_ids': [bs['id'] for bs in request_shortcuts],
    }
    payload = helpers.make_payload_with_shortcuts(
        request_shortcuts,
        blocks=[block],
        supported_sections=[{'type': supported_section}],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data['sections']) == 1
    section = data['sections'][0]
    assert section['type'] == supported_section
    assert section['header'] == {
        'title': {
            'items': [
                {
                    'color': '#000000',
                    'font_size': 14,
                    'font_style': 'normal',
                    'font_weight': 'regular',
                    'text': 'ololo',
                    'type': 'text',
                },
            ],
        },
    }
    if has_typed_header:
        assert section['typed_header'] == get_typed_header(expected=True)
    else:
        assert 'typed_header' not in section


@pytest.mark.parametrize(
    'shortcuts_params, expected_widths',
    [
        (
            [('Title', 2), ('Title', 2), ('Title', 2), ('Title', 2)],
            [3, 2, 2, 2],
        ),
        (
            [
                ('Title', 1),
                ('Title', 2),
                ('Title', 2),
                ('Title Title', 1),
                ('Title', 2),
            ],
            [1, 2, 2, 2, 2],
        ),
        (
            [('Title', 1), ('Title', 4), ('Title', 2), ('Title', 2)],
            [1, 4, 2, 2],
        ),
        ([('Title', 2), ('Title', 4), ('Title', 2)], [3, 4, 2]),
        ([('Title', 6)], [7]),
        ([('', 6)], [7]),
    ],
)
async def test_organic_scrollable(
        taxi_shortcuts, add_experiment, shortcuts_params, expected_widths,
):
    supported_section = 'items_horizontal_scrollable_grid'
    add_experiment(
        consts.BLOCKS_EXPERIMENT,
        {'organic': {'section_type': supported_section}},
    )
    add_experiment(
        consts.NATIVE_SECTION_TITLE_PARAMS, NATIVE_SECTION_TITLE_PARAMS,
    )
    cells = []
    i = 0
    for params in shortcuts_params:
        title, width = params
        shortcut = copy.deepcopy(consts.DEFAULT_TAXI_SHORTCUT)
        shortcut['content']['title'] = title
        shortcut['id'] = shortcut['id'] + str(i)
        cells.append({'height': 2, 'width': width, 'shortcut': shortcut})
        i += 1

    block = {
        'id': 'block_id_is_irrelevant',
        'slug': 'organic',
        'shortcut_ids': [cell['shortcut']['id'] for cell in cells],
    }
    payload = {
        'grid': {'id': 'id', 'width': 6, 'cells': cells, 'blocks': [block]},
        'shortcuts': {'supported_sections': [{'type': supported_section}]},
    }

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert 'items' in data['offers']
    widths = [item['width'] for item in data['offers']['items']]
    assert widths == expected_widths


@pytest.mark.parametrize('expect_buttons', [True, False])
async def test_sections_order_buttons_and_bricks_with_tags(
        taxi_shortcuts,
        add_experiment,
        add_config,
        add_appearance_experiments,
        expect_buttons,
):
    add_experiment(
        consts.BLOCKS_EXPERIMENT,
        {
            'header': {
                'tags': ['header_tag'],
                'tags_to_previous': ['header_tag_to_previous'],
            },
            'buttons': {
                'tags': ['buttons_tag'],
                'tags_to_previous': ['buttons_tag_to_previous'],
            },
        },
    )
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )
    add_appearance_experiments()
    env = helpers.EnvSetup()

    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    else:
        env.header_params_experiment['buttons']['show_from'] = 10
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_sections=env.all_supported_sections,
        supported_actions=env.all_supported_actions,
        cells=[
            {
                'height': 2,
                'width': 2,
                'shortcut': consts.DEFAULT_TAXI_SHORTCUT,
            },
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    offers = data['offers']

    bricks_section = {
        'shortcut_ids': [b['shortcut_id'] for b in offers.get('header', [])],
        'type': 'header_linear_grid',
        'tags': ['header_tag'],
    }

    buttons_section = {
        'button_ids': [b['id'] for b in offers.get('buttons', [])],
        'type': 'buttons_container',
        'tags': ['buttons_tag'],
    }

    shortcuts_section = {
        'shortcut_ids': [s['shortcut_id'] for s in offers.get('items', [])],
        'type': 'items_linear_grid',
        'tags': [
            'buttons_tag_to_previous'
            if expect_buttons
            else 'header_tag_to_previous',
        ],
    }

    expected_sections = (
        [shortcuts_section, buttons_section]
        if expect_buttons
        else [shortcuts_section, bricks_section]
    )
    assert data.get('sections', {}) == expected_sections


async def test_shop_buttons_min_shops_to_display(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    add_appearance_experiments()
    env = helpers.EnvSetup(
        disabled_available_scenarios={helpers.Scenarios.eats_based_shop},
    )
    env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_sections=env.all_supported_sections,
        supported_actions=env.all_supported_actions,
        cells=[
            {
                'height': 2,
                'width': 2,
                'shortcut': consts.DEFAULT_TAXI_SHORTCUT,
            },
        ],
        shop_shortcuts=[consts.DEFAULT_SHOP_SHORTCUT],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200

    response_body = response.json()

    shop_buttons = [
        button
        for button in response_body['offers']['buttons']
        if button.get('service') == 'shop'
    ]

    assert not shop_buttons


@pytest.mark.translations(
    client_messages={
        'buttons_title_key': {'ru': '<buttons_title>Buttons!</buttons_title>'},
    },
)
@pytest.mark.config(
    EXTENDED_TEMPLATE_STYLES_MAP={
        'buttons_title': {'color': '#000000', 'font_size': 14},
    },
)
@pytest.mark.parametrize(
    'title_exp_value, expect_title',
    [
        ({'enabled': False}, False),
        ({'enabled': True}, False),
        ({'enabled': True, 'tanker_key': 'unknown_key'}, False),
        ({'enabled': True, 'tanker_key': 'buttons_title_key'}, True),
    ],
)
async def test_buttons_container_header(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        title_exp_value,
        expect_title,
):
    add_experiment(consts.BUTTONS_CONTAINER_TITLE_EXP, title_exp_value)

    add_appearance_experiments()
    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_sections=env.all_supported_sections,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)

    assert response.status_code == 200

    data = response.json()
    buttons_container = data['sections'][0]

    assert buttons_container['type'] == 'buttons_container'

    if expect_title:
        assert 'header' in buttons_container
        assert buttons_container['header'] == {
            'title': {
                'items': [
                    {
                        'color': '#000000',
                        'font_size': 14,
                        'text': 'Buttons!',
                        'type': 'text',
                    },
                ],
            },
        }
    else:
        assert 'header' not in buttons_container
