import datetime

import pytest


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=False)
async def test_nothing_if_disabled(step_buy_contacts):
    step = await step_buy_contacts('three_latest_resumes.json')

    flags = [res['need_processing'] for res in step.resumes]
    has_resumes = bool(flags)
    all_stay_unprocessed = all(flags)
    no_attempts_to_buy = not step.contacts_handler.has_calls

    assert has_resumes and all_stay_unprocessed and no_attempts_to_buy


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_FETCH_UNPROCESSED_LIMIT=1)
@pytest.mark.parametrize('run_cron_times', [1, 3])
async def test_max_unprocessed_limit(step_buy_contacts, run_cron_times):
    step = await step_buy_contacts(
        'three_latest_resumes.json', run_cron_times=run_cron_times,
    )

    processed = [1 for res in step.resumes if not res['need_processing']]
    # process only one resume per cron run, other stay unprocessed
    assert len(processed) == run_cron_times


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
async def test_all_updated_in_history(step_buy_contacts):
    step = await step_buy_contacts('three_latest_resumes.json')

    # 3 resumes in file, 3 were processed
    assert len(step.resumes) == 3
    assert len(step.history) == 6


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_MAX_CONTACTS_TO_BUY=1)
@pytest.mark.parametrize('run_cron_times', [1, 3])
async def test_max_contacts_to_buy(step_buy_contacts, run_cron_times):
    step = await step_buy_contacts(
        'three_suitable_resumes.json', run_cron_times=run_cron_times,
    )

    processed = [1 for res in step.resumes if not res['need_processing']]
    bought = [
        1
        for res in step.resumes
        if res['suitable'] and not res['need_processing']
    ]
    # buy only one resume per cron run, other stay unprocessed
    assert len(processed) == len(bought)
    assert len(bought) == run_cron_times
    assert len(bought) == step.contacts_handler.times_called


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_CONTACTS_EXPIRATION_SECONDS=110)
async def test_dont_buy_contacts_until_expired(
        _step_got_expired_on_100_seconds_contact, step_buy_contacts,
):
    await _step_got_expired_on_100_seconds_contact()
    step = await step_buy_contacts('resumes_that_lost_contacts.json')
    # don't buy expired contacts
    assert not step.contacts_handler.has_calls


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_CONTACTS_EXPIRATION_SECONDS=90)
async def test_buy_contacts_if_not_expired(
        _step_got_expired_on_100_seconds_contact, step_buy_contacts,
):
    await _step_got_expired_on_100_seconds_contact()
    step = await step_buy_contacts('resumes_that_lost_contacts.json')
    # it's not expired anymore, full contact was requested
    assert step.contacts_handler.has_calls


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_CONTACTS_EXPIRATION_SECONDS=1)
async def test_keep_phones(
        _step_got_expired_on_100_seconds_contact, step_buy_contacts,
):
    await _step_got_expired_on_100_seconds_contact()

    # Resume 206026688 previously has phones
    step = await step_buy_contacts('resumes_that_lost_contacts.json')

    assert len(step.buy_contacts_calls) == 1
    last_mod_date = step.buy_contacts_calls[0]['resumes'][-1]['mod_date']

    # resume was updated with last call of `buy_contacts.py` but keeps
    # previously known phone
    assert step.resumes[0]['raw_doc']['mod_date'] == last_mod_date
    assert step.resumes[0]['has_phones']


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
async def test_process_even_unsuitable(step_buy_contacts):
    step = await step_buy_contacts('three_latest_resumes.json')
    assert any(not r['suitable'] for r in step.resumes)
    assert all(not r['need_processing'] for r in step.resumes)


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_CONTACTS_EXPIRATION_SECONDS=100500100500)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=False)
async def test_what_is_suitable_and_unsuitable(step_buy_contacts):
    step = await step_buy_contacts('suitable_and_unsuitable.json')

    # Total 3 resumes
    assert len(step.resumes) == 3

    # 123 is suitable
    # 456 is not driver
    # 789 is in an area we don't work
    suitable = [r for r in step.resumes if r['suitable']]
    assert len(suitable) == 1 and suitable[0]['id'] == 123


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_CONTACTS_EXPIRATION_SECONDS=100500100500)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=True)
async def test_what_is_suitable_and_unsuitable_wf(step_buy_contacts):
    step = await step_buy_contacts('wide_funnel.json')

    # Total 3 resumes
    assert len(step.resumes) == 3

    # 123 is suitable
    # 456 is not driver
    # 789 is in an area we don't work
    suitable = [r for r in step.resumes if r['suitable']]
    assert len(suitable) == 1 and suitable[0]['id'] == 123


@pytest.fixture
async def _step_got_expired_on_100_seconds_contact(
        step_auth_and_get_latest, update_resume_fields,
):
    async def _wrapper():
        filename = 'resumes_that_lost_contacts.json'
        step = await step_auth_and_get_latest(filename)
        past = datetime.datetime.utcnow() - datetime.timedelta(seconds=100)
        await update_resume_fields(
            step.resumes[0]['id'], contacts_updated=past,
        )
        return step

    return _wrapper
