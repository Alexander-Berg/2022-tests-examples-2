import pytest
from dateutil.relativedelta import relativedelta

from stall.model.courier import Courier


@pytest.mark.parametrize(
    ['years', 'gender', 'appended', 'removed'],
    [
        (
            15,
            'male',
            ['grocery_male_under18_rus'],
            ['grocery_female_under18_rus'],
        ),
        (
            15,
            'female',
            ['grocery_female_under18_rus'],
            ['grocery_male_under18_rus'],
        ),
        (
            15,
            None,
            [],
            ['grocery_male_under18_rus', 'grocery_female_under18_rus'],
        ),
        (
            18,
            'male',
            [],
            ['grocery_male_under18_rus', 'grocery_female_under18_rus'],
        ),
        (
            18,
            'female',
            [],
            ['grocery_male_under18_rus', 'grocery_female_under18_rus'],
        ),
    ]
)
# pylint: disable=too-many-arguments
async def test_common(
        tap, dataset, ext_api, job, now,
        years, gender, appended, removed
):
    birthday = now().date() - relativedelta(years=years)

    _calls = []

    async def handle(request):
        data = await request.json()
        _calls.append(data)
        return {'code': 'OK'}

    with tap.plan(7, 'таск вызывает клиента с правильными параметрами'):
        courier = await dataset.courier(
            birthday=birthday, gender=gender
        )

        await job.put(
            Courier.job_sync_underage_tag,
            courier_id=courier.courier_id,
        )

        async with await ext_api('grocery_tags', handle):
            await job.call(await job.take())

        tap.eq(len(_calls), 1, 'grocery-tags called once')

        if appended:
            tap.eq(
                len(_calls[-1]['append'][0]['tags']), len(appended),
                'appended all tags'
            )
            for tag, expected in zip(_calls[-1]['append'][0]['tags'], appended):
                tap.eq(tag['entity'], courier.external_id,
                       'tag for this courier')
                tap.eq(tag['name'], expected, 'appended expected')
        else:
            tap.ok('append' not in _calls[-1], 'appended none')

        if removed:
            tap.eq(
                len(_calls[-1]['remove'][0]['tags']), len(removed),
                'removed all tags'
            )
            for tag, expected in zip(_calls[-1]['remove'][0]['tags'], removed):
                tap.eq(tag['entity'], courier.external_id,
                       'tag for this courier')
                tap.eq(tag['name'], expected, 'removed expected')
        else:
            tap.ok('remove' not in _calls[-1], 'removed none')
