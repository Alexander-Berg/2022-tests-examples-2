import typing as tp
import uuid

from taxi_qc_exams.helpers import consts


def job_settings(enabled: str = 'on'):
    return dict(
        enabled=enabled,
        clients=dict(__default__=dict(batch=1000, sleep=0)),
        cursor_sync=dict(
            acquire_for='0s',
            lock_for='0s',
            max_operations=1,
            retry_for='0s',
            sync_lag='1s',
            sync_period='2s',
        ),
    )


def make_state(
        entity_id,
        sanctions=None,
        exam='dkk',
        entity_type=None,
        enabled=True,
        has_present=True,
):
    state = dict(
        id=entity_id,
        type=entity_type or consts.qc.Exam.to_type(exam),
        exams=[dict(code=exam, modified='2020-01-01', enabled=enabled)],
    )

    if not has_present:
        return state

    state['exams'][0]['present'] = {'pass': dict(id='pass_id')}

    if sanctions:
        state['exams'][0]['present']['sanctions'] = sanctions

    return state


def make_pass(
        entity_id, exam='medcard', status='resolved', success=True, data=None,
):
    result = dict(
        id=uuid.uuid4().hex,
        entity_id=entity_id,
        entity_type=consts.qc.Exam.to_type(exam),
        exam=exam,
        modified='2020-05-12T16:30:00.000Z',
        status=status.upper(),
    )

    if data:
        for item in data:
            item['required'] = item.get('required', False)
        result['data'] = data

    if result['status'] == consts.Status.RESOLVED:
        result['resolution'] = make_resolution(success=success)

    return result


def make_resolution(success: bool):
    resolution = dict(
        resolved='2020-05-12T16:30:00.000Z',
        identity=dict(yandex_team=dict(yandex_login='assessor')),
    )

    if success:
        resolution['status'] = consts.Resolution.SUCCESS
    else:
        resolution['status'] = consts.Resolution.FAIL
        resolution['reason'] = dict(code='block', keys=['text_bad_photo'])

    return resolution


_T = tp.TypeVar('_T')  # type: ignore


def symmetric_lists_diff(
        first: tp.List[_T], second: tp.List[_T],
) -> tp.List[_T]:
    first = list(first)  # make a mutable copy
    result: tp.List[_T] = []
    for elem in second:
        try:
            first.remove(elem)
        except ValueError:
            result.append(elem)
    return result + first
