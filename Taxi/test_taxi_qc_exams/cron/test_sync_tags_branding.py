from aiohttp import web
import pytest

from taxi.util import dates

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils

KNOWN_REVISION = '0_1548838800_3'


@pytest.mark.config(QC_JOB_SETTINGS=dict(branding_tags=utils.job_settings()))
@pytest.mark.parametrize(
    'expected, amenities, tags, confirmations',
    [
        # no branding
        ([], [], [], dict(lightbox_confirmed=False, sticker_confirmed=False)),
        # park enabled stickers
        (
            [],
            ['sticker'],
            [],
            dict(lightbox_confirmed=False, sticker_confirmed=False),
        ),
        # stickers confirmed
        (
            ['sticker'],
            ['sticker'],
            [],
            dict(lightbox_confirmed=False, sticker_confirmed=True),
        ),
        # stickers have been confirmed early
        (
            None,
            ['sticker'],
            ['sticker'],
            dict(lightbox_confirmed=False, sticker_confirmed=True),
        ),
        # exam deadline missing
        (
            [],
            ['sticker'],
            ['sticker'],
            dict(lightbox_confirmed=False, sticker_confirmed=False),
        ),
        # park enable lightbox and reset exam's result
        (
            [],
            ['lightbox', 'sticker'],
            ['sticker'],
            dict(lightbox_confirmed=False, sticker_confirmed=False),
        ),
        # full-branding confirmed
        (
            ['lightbox', 'sticker'],
            ['lightbox', 'sticker'],
            ['sticker'],
            dict(lightbox_confirmed=True, sticker_confirmed=True),
        ),
        # full-branding no changes
        (
            None,
            ['lightbox', 'sticker'],
            ['lightbox', 'sticker'],
            dict(lightbox_confirmed=True, sticker_confirmed=True),
        ),
        # park remove branding information. Qc exams haven't synced yet
        (
            [],
            [],
            ['lightbox', 'sticker'],
            dict(lightbox_confirmed=True, sticker_confirmed=True),
        ),
        # only stickers confirmed by qc exam
        (
            ['sticker'],
            ['lightbox', 'sticker'],
            [],
            dict(lightbox_confirmed=False, sticker_confirmed=True),
        ),
    ],
)
async def test_sync_tags_branding(
        mock_fleet_vehicles,
        mock_tags,
        expected,
        amenities,
        confirmations,
        tags,
):
    @mock_fleet_vehicles('/v1/vehicles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        vehicles = []
        if revision != KNOWN_REVISION:
            data = dict(car_id='1', park_id='1', amenities=amenities)
            data.update(confirmations)
            vehicles = [
                dict(park_id_car_id='1_1', revision=KNOWN_REVISION, data=data),
            ]
        return web.json_response(
            data=dict(
                vehicles=vehicles,
                last_revision=KNOWN_REVISION,
                last_modified=dates.timestring(dates.utcnow(), 'UTC'),
            ),
            headers={'X-Polling-Delay-Ms': '0'},
        )

    @mock_tags('/v1/bulk_match')
    async def _v1_bulk_match(request):
        return web.json_response(
            data=dict(entities=[dict(id='1_1', tags=tags)]),
        )

    @mock_tags('/v1/assign')
    async def _v1_assign(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [f'taxi_qc_exams.crontasks.sync_tags.branding', '-t', '0'],
    )

    if expected is None:
        assert _v1_assign.times_called == 0
        return

    assert _v1_assign.times_called == 1
    request_json = _v1_assign.next_call()['request'].json
    assert request_json.pop('provider', None) == 'qc_branding'
    assert request_json.pop('entities') == [
        dict(name='1_1', type='park_car_id', tags={x: {} for x in expected}),
    ]


@pytest.mark.config(QC_JOB_SETTINGS=dict(branding_tags=utils.job_settings()))
async def test_sync_tags_branding_no_data(mock_fleet_vehicles, mock_tags):
    @mock_fleet_vehicles('/v1/vehicles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        vehicles = []
        if revision != KNOWN_REVISION:
            vehicles = [dict(park_id_car_id='1_1', revision=KNOWN_REVISION)]
        return web.json_response(
            data=dict(
                vehicles=vehicles,
                last_revision=KNOWN_REVISION,
                last_modified=dates.timestring(dates.utcnow(), 'UTC'),
            ),
            headers={'X-Polling-Delay-Ms': '0'},
        )

    @mock_tags('/v1/bulk_match')
    async def _v1_bulk_match(request):
        return web.json_response(data=dict(entities=[dict(id='1_1', tags=[])]))

    @mock_tags('/v1/assign')
    async def _v1_assign(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [f'taxi_qc_exams.crontasks.sync_tags.branding', '-t', '0'],
    )

    assert _v1_assign.times_called == 1
    request_json = _v1_assign.next_call()['request'].json
    assert request_json.pop('provider', None) == 'qc_branding'
    assert request_json.pop('entities') == [
        dict(name='1_1', type='park_car_id', tags={}),
    ]


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(branding_tags=utils.job_settings(enabled='dry-run')),
)
async def test_sync_tags_branding_dry_run(mock_fleet_vehicles, mock_tags):
    @mock_fleet_vehicles('/v1/vehicles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        vehicles = []
        if revision != KNOWN_REVISION:
            data = dict(
                car_id='1',
                park_id='1',
                amenities=['sticker'],
                sticker_confirmed=True,
            )
            vehicles = [
                dict(park_id_car_id='1_1', revision=KNOWN_REVISION, data=data),
            ]
        return web.json_response(
            data=dict(
                vehicles=vehicles,
                last_revision=KNOWN_REVISION,
                last_modified=dates.timestring(dates.utcnow(), 'UTC'),
            ),
            headers={'X-Polling-Delay-Ms': '0'},
        )

    @mock_tags('/v1/bulk_match')
    async def _v1_bulk_match(request):
        return web.json_response(data=dict(entities=[dict(id='1_1', tags=[])]))

    @mock_tags('/v1/assign')
    async def _v1_assign(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [f'taxi_qc_exams.crontasks.sync_tags.branding', '-t', '0'],
    )

    assert _v1_assign.times_called == 0


@pytest.mark.ticked_time
@pytest.mark.config(QC_JOB_SETTINGS=dict(branding_tags=utils.job_settings()))
async def test_sync_tags_branding_tags_error(mock_fleet_vehicles, mock_tags):
    data = dict(
        car_id='1', park_id='1', amenities=['sticker'], sticker_confirmed=True,
    )
    vehicles = [dict(park_id_car_id='1_1', revision=KNOWN_REVISION, data=data)]
    should_generate_error = True

    @mock_fleet_vehicles('/v1/vehicles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        return web.json_response(
            data=dict(
                vehicles=vehicles if revision != KNOWN_REVISION else [],
                last_revision=KNOWN_REVISION,
                last_modified=dates.timestring(dates.utcnow(), 'UTC'),
            ),
            headers={'X-Polling-Delay-Ms': '0'},
        )

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    def _mock_retrieve(request):
        return web.json_response(data=dict(vehicles=vehicles))

    @mock_tags('/v1/bulk_match')
    async def _v1_bulk_match(request):
        return web.json_response(data=dict(entities=[dict(id='1_1', tags=[])]))

    @mock_tags('/v1/assign')
    async def _v1_assign(request):
        nonlocal should_generate_error
        if should_generate_error:
            should_generate_error = False
            return web.json_response(status=500, data={})
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [f'taxi_qc_exams.crontasks.sync_tags.branding', '-t', '0'],
    )

    assert _v1_assign.times_called == 2
