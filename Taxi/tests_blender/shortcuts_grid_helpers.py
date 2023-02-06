import dataclasses
from typing import Dict
from typing import List
from typing import Optional
import uuid

MEANINGLESS_HEADERS = {
    'X-Yandex-UID': '12345',
    'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
}

STANDART_HEIGHT = 2


@dataclasses.dataclass
class Shortcut:
    title: str
    tags: List[str]
    promo_id: str

    def __init__(self, title, tags, promo_id=None):
        self.title = title
        self.tags = tags
        self.promo_id = promo_id

    def to_dict(self, scenario):
        result = {
            'id': str(uuid.uuid4()),
            'scenario': scenario,
            'content': {
                'image_tag': 'string',
                'title': self.title,
                'subtitle': 'string',
                'color': 'string',
                'overlays': [{'text': 'overlay_text'}],
            },
            'scenario_params': self._scenario_params(scenario),
            'tags': self.tags,
        }
        if self.tags:
            result['tags'] = self.tags
        return result

    def _scenario_params(self, scenario):
        params = {scenario + '_params': {'action_type': scenario}}
        if self.promo_id is not None:
            params['promo_id'] = self.promo_id
        return params

    @staticmethod
    def get_promo_id(shortcut_dict: Dict):
        try:
            return shortcut_dict['scenario_params']['promo_id']
        except KeyError:
            return None


@dataclasses.dataclass
class GridCell:
    title: str
    width: int
    height: int
    shortcut_id: str
    scenario: str

    def __eq__(self, other):
        if isinstance(other, list):
            if len(other) == 2:
                return (
                    other == [self.title, self.width]
                    and self.height == STANDART_HEIGHT
                )
            if len(other) == 3:
                return other == [self.title, self.width, self.height]
            return False
        return (
            self.title == other.title
            and self.width == other.width
            and self.height == other.height
            and self.shortcut_id == other.shortcut_id
            and self.scenario == other.scenario
        )


@dataclasses.dataclass
class Block:
    slug: str
    shortcut_ids: List[str]
    titles: List[str]
    title_key: Optional[str]
    title: Optional[str]

    def __eq__(self, other):
        if isinstance(other, list):
            if len(other) == 2:
                return other[0] == self.slug and set(other[1]) == set(
                    self.titles,
                )
            return False

        return (
            self.slug == other.slug
            and self.shortcut_ids == other.shortcut_ids
            and self.titles == other.titles
            and self.title_key == other.title_key
            and self.title == other.title
        )


@dataclasses.dataclass
class Response:
    layout: list
    blocks: List[Block]
    shop_shortcuts: Optional[List[dict]]


class ResponceFetcher:
    def __init__(self, taxi_blender, load_json):
        self._taxi_blender = taxi_blender
        self._empty_request = load_json('empty_request.json')

    def _make_request_body(
            self,
            scenario_to_top,
            scenario_to_prediction,
            known_orders,
            title_to_tags,
            showcases,
    ):
        req = self._empty_request.copy()
        req['scenario_tops'] = [
            {
                'scenario': scenario,
                'shortcuts': [
                    s.to_dict(scenario)
                    if isinstance(s, Shortcut)
                    else Shortcut(s, title_to_tags.get(s, [])).to_dict(
                        scenario,
                    )
                    for s in top
                ],
            }
            for scenario, top in scenario_to_top.items()
        ]
        if scenario_to_prediction is not None:
            req['scenario_predictions'] = [
                {'relevance': prediction, 'scenario': scenario}
                for scenario, prediction in scenario_to_prediction.items()
            ]
        if known_orders is not None:
            req['state'] = {
                'known_orders': [
                    ko + ':order_id:version' for ko in known_orders
                ],
            }
        if showcases is not None:
            req['showcases'] = showcases
        return req

    def _validate_blocks(self, layout, blocks):
        if not blocks:
            return
        blocks_shortcut_ids = []

        # block shortcut ids are unique
        for block in blocks:
            for sh_id in block.shortcut_ids:
                assert sh_id not in blocks_shortcut_ids
                blocks_shortcut_ids.append(sh_id)

        # every cell is presented in blocks
        for cell in layout:
            assert cell.shortcut_id in blocks_shortcut_ids

        # no gaps in blocks
        sh_id_to_block_index = {}
        for index, block in enumerate(blocks):
            for sh_id in block.shortcut_ids:
                sh_id_to_block_index[sh_id] = index

        block_indexes = [
            sh_id_to_block_index[cell.shortcut_id] for cell in layout
        ]
        assert block_indexes == sorted(block_indexes)

    async def response(
            self,
            scenario_to_top,
            scenario_to_prediction=None,
            known_orders=None,
            check_params=True,
            title_to_tags=None,
            showcases=None,
    ):
        if title_to_tags is None:
            title_to_tags = dict()

        req_body = self._make_request_body(
            scenario_to_top,
            scenario_to_prediction,
            known_orders,
            title_to_tags,
            showcases,
        )
        response = await self._taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=req_body,
            headers=MEANINGLESS_HEADERS,
        )
        assert response.status_code == 200
        resp_body = response.json()
        assert 'grid' in resp_body
        if check_params:
            for cell in resp_body['grid']['cells']:
                response_shortcut = cell['shortcut']
                assert (
                    response_shortcut['scenario_params']
                    == Shortcut(
                        '', [], Shortcut.get_promo_id(response_shortcut),
                    ).to_dict(response_shortcut['scenario'])['scenario_params']
                )

        assert 'blocks' in resp_body['grid']

        for cell in resp_body['grid']['cells']:
            assert 'overlays' in cell['shortcut']['content']

        layout = [
            GridCell(
                title=cell['shortcut']['content']['title'],
                width=cell['width'],
                height=cell['height'],
                shortcut_id=cell['shortcut']['id'],
                scenario=cell['shortcut']['scenario'],
            )
            for cell in resp_body['grid']['cells']
        ]

        id_to_title = {cell.shortcut_id: cell.title for cell in layout}

        blocks = [
            Block(
                slug=block['slug'],
                shortcut_ids=block['shortcut_ids'],
                titles=[id_to_title[id] for id in block['shortcut_ids']],
                title_key=block.get('title_key'),
                title=block.get('title'),
            )
            for block in resp_body['grid']['blocks']
        ]
        self._validate_blocks(layout=layout, blocks=blocks)
        return Response(
            layout=layout,
            blocks=blocks,
            shop_shortcuts=resp_body.get('shop_shortcuts'),
        )


def split_to_lines(objects, width_function=lambda x: x):
    result = []
    current_line = []
    current_sum = 0
    for obj in objects:
        current_line.append(obj)
        current_sum += width_function(obj)
        assert current_sum <= 6
        if current_sum == 6:
            result.append(current_line)
            current_line = []
            current_sum = 0
    assert current_sum == 0
    return result


def check_layout_without_gaps(layout):
    split_to_lines(layout, width_function=lambda cell: cell.width)


def check_layout_diversity(layout):
    widths = [cell.width for cell in layout]
    lines = split_to_lines(widths)

    diversity_guarantee_span = 3
    for i in range(max(len(lines) - diversity_guarantee_span + 1, 0)):
        for shift in range(1, diversity_guarantee_span):
            assert lines[i] != lines[i + shift]


def check_layout_scenarios(layout, expected_scenarios):
    actual_scenarios = {cell.scenario for cell in layout}
    assert actual_scenarios == expected_scenarios, actual_scenarios


def pretty_print(layout):
    lines = split_to_lines(layout, width_function=lambda cell: cell.width)
    unit_text_size = 6

    def cell_to_str(cell):
        title, width = cell.title, cell.width
        text_size = unit_text_size * width - 6
        if text_size < len(title):
            cut_title = title[:text_size]
        else:
            padding = text_size - len(title)
            left_padding = padding // 2
            right_padding = padding - left_padding
            cut_title = left_padding * ' ' + title + right_padding * ' '

        return f' | {cut_title} | '

    def line_to_str(line):
        return ''.join(cell_to_str(c) for c in line)

    print('\n'.join(line_to_str(l) for l in lines))
