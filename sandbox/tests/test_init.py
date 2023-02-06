import mock
import pytest

from sandbox.projects.browser.ab_experiments.ab_service import Queue
from sandbox.projects.browser.ab_experiments.BrowserExperimentsAbChecklist import checklists
from sandbox.projects.browser.ab_experiments.channels import Channel


@mock.patch.object(checklists, '_CHECKLISTS_BY_AB_QUEUE', {
    Queue.DEBRO: {
        (checklists._ANY, Channel.BROTEAM, checklists._ANY, checklists._ANY): ['a', 'b', 'c'],
        (checklists._ANY, Channel.BETA, checklists._ANY, checklists._ANY): ['d', 'e', 'f'],
    },
})
def test_build_actual_checklist():

    mk_item = checklists.ChecklistItem

    cur_checklist = [
        mk_item('custom_item_1', True),
        mk_item('a', False),
        mk_item('b', True),
        mk_item('c', False),
        mk_item('custom_item_2', False),
    ]

    new_checklist = checklists.build_actual_checklist(cur_checklist, Queue.DEBRO, [(mock.Mock(), Channel.BETA, mock.Mock(), mock.Mock())])
    assert new_checklist == [
        mk_item('b', True),
        mk_item('custom_item_1', True),
        mk_item('custom_item_2', False),
        mk_item('d', False),
        mk_item('e', False),
        mk_item('f', False),
    ]


@mock.patch.object(checklists, '_CHECKLISTS_BY_AB_QUEUE', {
    Queue.DEBRO: {
        (checklists._ANY, Channel.BROTEAM, checklists._ANY, checklists._ANY): ['a', 'b', 'c'],
        (checklists._ANY, Channel.BETA, checklists._ANY, checklists._ANY): ['d', 'e', 'f'],
    },
})
def test_build_actual_checklist_multiple_channels():
    mk_item = checklists.ChecklistItem

    cur_checklist = [
        mk_item('custom_item_1', False),
        mk_item('custom_item_2', True),
    ]

    new_checklist = checklists.build_actual_checklist(
        cur_checklist, Queue.DEBRO, [(mock.Mock(), Channel.BROTEAM, mock.Mock(), mock.Mock()),
                                     (mock.Mock(), Channel.BETA, mock.Mock(), mock.Mock())])
    assert new_checklist == [
        mk_item('custom_item_1', False),
        mk_item('custom_item_2', True),
        mk_item('a', False),
        mk_item('b', False),
        mk_item('c', False),
        mk_item('d', False),
        mk_item('e', False),
        mk_item('f', False),
    ]


@mock.patch.object(checklists, '_get_actual_checklist')
@mock.patch.object(checklists, '_CHECKLISTS_BY_AB_QUEUE', {
    Queue.DEBRO: {
        (checklists._ANY, Channel.BROTEAM, checklists._ANY, checklists._ANY): ['a', 'b', 'c'],
    },
})
def test_build_actual_checklist_only_custom(_get_actual_checklist):
    _get_actual_checklist.return_value = []

    cur_checklist = [
        checklists.ChecklistItem('custom_item_1', True),
        checklists.ChecklistItem('custom_item_2', False),
        checklists.ChecklistItem('custom_item_3', True),
    ]

    new_checklist = checklists.build_actual_checklist(
        cur_checklist, Queue.DEBRO, [(mock.Mock(), Channel.BETA, mock.Mock(), mock.Mock())])
    assert new_checklist == [
        checklists.ChecklistItem('custom_item_1', True),
        checklists.ChecklistItem('custom_item_2', False),
        checklists.ChecklistItem('custom_item_3', True),
    ]


@pytest.mark.parametrize(('queue', 'exp_param', 'result_checklist'), [
    (Queue.GATEWAY, ('ABT', Channel.STABLE, 'ios', 'internal'), ['a', 'b', 'c']),
    (Queue.GATEWAY, ('ABT', Channel.BETA, 'ios', 'external'), []),
    (Queue.DEBRO, ('ABT', Channel.BETA, 'android', ''), ['d', 'e', 'f']),
    (Queue.DEBRO, ('ABT', Channel.BROTEAM, 'android', 'internal'), []),
    (Queue.BROWSER, ('ABT', Channel.ALPHA, 'linux', 'internal'), []),
])
@mock.patch.object(checklists, '_CHECKLISTS_BY_AB_QUEUE', {
    Queue.GATEWAY: {
        ('ABT', Channel.STABLE, 'ios', 'internal'): ('a', 'b', 'c'),
    },
    Queue.DEBRO: {
        ('ABT', Channel.BETA, 'android', checklists._ANY): ('d', 'e', 'f'),
    }
})
def test_get_actual_checklist(queue, exp_param, result_checklist):
    assert checklists._get_actual_checklist(queue, exp_param) == result_checklist


@pytest.mark.parametrize(('queue', 'result_items'), [
    (Queue.DEBRO, set('abcdef')),
    (Queue.BROWSER, set()),
    (Queue.IBRO, set()),
    (Queue.GATEWAY, set()),
])
@mock.patch.object(checklists, '_CHECKLISTS_BY_AB_QUEUE', {
    Queue.DEBRO: {
        (Channel.BROTEAM): ('a', 'b', 'c'),
        (Channel.STABLE): ('d', 'e', 'b', 'f'),
    },
    Queue.BROWSER: {
        (Channel.BROTEAM): (),
    },
    Queue.IBRO: {},
})
def test_get_regular_checklist_items(queue, result_items):
    assert checklists._get_regular_checklist_items(queue) == result_items
