import pytest


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=False)
async def test_nothing_if_disabled(step_auth_and_get_latest):
    step = await step_auth_and_get_latest('empty_resumes.json')
    assert not step.auth_handler.has_calls
    assert not step.resumes_handler.has_calls


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
async def test_has_calls_if_enabled(step_auth_and_get_latest):
    step = await step_auth_and_get_latest('empty_resumes.json')
    assert step.auth_handler.has_calls
    assert step.resumes_handler.has_calls


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
async def test_all_new_and_updated_saved(_insert_than_update):
    step = await _insert_than_update(
        'first_resumes.json', 'a_few_resumes_updated.json',
    )
    # total in both files: 10 resumes (5 in first, 5 in second)
    # in lastest file: 3 new, 1 unchanged, 1 modified
    assert len(step.history) == 9
    assert len(step.resumes) == 8


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
async def test_history_keeps_docs(_insert_than_update):
    step = await _insert_than_update(
        'first_version.json', 'second_version.json',
    )
    mod_dates = {x['gzipped_raw_doc']['mod_date'] for x in step.history}
    latest = step.latest_resumes_calls[-1]['resumes'][0]['mod_date']

    # resume keeps last version, history keeps both (previous and current)
    one_resume = len(step.resumes) == 1
    has_latest_version = step.resumes[0]['raw_doc']['mod_date'] == latest
    both_versions_in_history = len(mod_dates) == 2

    assert one_resume and has_latest_version and both_versions_in_history


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.parametrize(
    'filename, expected',
    [
        ('resumes_with_contacts.json', (True, False)),
        ('resumes_without_contacts.json', (False, True)),
    ],
)
async def test_save_contacts_on_insert(
        step_auth_and_get_latest, filename, expected,
):
    step = await step_auth_and_get_latest(filename)
    record = step.resumes[0]
    result = record['has_phones'], record['contacts_updated'] is None
    assert result == expected


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
async def test_keep_removed_contacts(_insert_than_update):
    step = await _insert_than_update(
        'first_version_with_contacts.json',
        'second_version_contacts_removed.json',
    )
    first = step.latest_resumes_calls[0]['resumes'][0]
    last = step.latest_resumes_calls[-1]['resumes'][0]
    db_doc = step.resumes[0]['raw_doc']
    document_modified = db_doc['mod_date'] == last['mod_date']
    phones_saved = db_doc['contact']['phones'] == first['contact']['phones']
    assert document_modified and phones_saved


@pytest.fixture
def _insert_than_update(step_auth_and_get_latest):
    async def _wrapper(*filenames):
        step = await step_auth_and_get_latest(*filenames, run_cron_times=2)
        return step

    return _wrapper
