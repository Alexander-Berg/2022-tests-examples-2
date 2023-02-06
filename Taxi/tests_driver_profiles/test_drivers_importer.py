import pytest


JOB_NAME = 'drivers-importer-worker'

STATIC_ACTIVE_DRIVERS_COUNT = 1
STATIC_ABSENT_DRIVERS_COUNT = 0

IMPORTABLE_DRIVERS_COUNT = 4
IMPORTABLE_DRIVERS_WITH_PD_PHONE_COUNT = 3
ABSENT_DRIVERS_COUNT = 1


def get_drivers_importer_work_mode(mode):
    return {
        'mode': mode,
        'chunk-size': 2,
        'full-updates-limit-per-iteration': 2,
        'interval-ms': 1000,
        'lagging-cursor-delay': 1,
        'pg-timeout-ms': 2000,
    }


PHONE_PD_MAP = {
    'items': [
        {'id': '00000000000000000000000000000000', 'value': '+79505005050'},
        {'id': '00000000000000000000000000000001', 'value': '+795'},
        {'id': '00000000000000000000000000000002', 'value': '+79505005052'},
        {'id': '00000000000000000000000000000003', 'value': '+79505005053'},
        {'id': '00000000000000000000000000000004', 'value': '+79505005054'},
    ],
}

PHONE_PD_MAP_BROKEN = {
    'items': [{'id': '00000000000000000000000000000001', 'value': '+795'}],
}


class PersonalContext:
    def __init__(self):
        self.pd_phones = None
        self.failing = False

    def set_pd_phones(self, phones_map):
        self.pd_phones = phones_map

    def set_failing(self, failing):
        self.failing = failing


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):

    context = PersonalContext()

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_retrieve(request):
        if context.failing:
            return mockserver.make_response('fail', status=500)

        pd_ids = set()
        for pd_id in request.json['items']:
            pd_ids.add(pd_id['id'])

        resp_items = []
        if context.pd_phones:
            for pd_item in context.pd_phones['items']:
                if pd_item['id'] in pd_ids:
                    resp_items.append(pd_item)

        return {'items': resp_items}

    return context


async def wait_iteration(taxi_driver_profiles, job_name, mode, testpoint):
    @testpoint(job_name + '-started')
    def started(data):
        return data

    @testpoint(job_name + '-finished')
    def finished(data):
        return data

    await taxi_driver_profiles.enable_testpoints()
    while True:
        start_status = (await started.wait_call())['data']
        if start_status['mode'] == mode:
            break
    while True:
        finish_status = (await finished.wait_call())['data']
        if finish_status['mode'] == mode:
            return finish_status['stats']
    return []


@pytest.mark.config(
    DRIVERS_IMPORTER_WORK_MODE=get_drivers_importer_work_mode('disabled'),
)
async def test_worker_disabled(
        taxi_driver_profiles, taxi_config, testpoint, mongodb,
):
    await taxi_driver_profiles.invalidate_caches()

    await wait_iteration(taxi_driver_profiles, JOB_NAME, 'disabled', testpoint)

    assert (
        mongodb.drivers.find({'_state': 'absent'}).count()
        == STATIC_ABSENT_DRIVERS_COUNT
    )
    assert (
        mongodb.drivers.find({'_state': 'active'}).count()
        == STATIC_ACTIVE_DRIVERS_COUNT
    )


@pytest.mark.config(
    DRIVERS_IMPORTER_WORK_MODE=get_drivers_importer_work_mode('enabled'),
)
async def test_worker_enabled(
        taxi_driver_profiles, taxi_config, testpoint, mongodb, mock_personal,
):
    mock_personal.set_pd_phones(PHONE_PD_MAP)

    await taxi_driver_profiles.invalidate_caches()
    for _ in range(0, 3):
        await wait_iteration(
            taxi_driver_profiles, JOB_NAME, 'enabled', testpoint,
        )

    assert (
        mongodb.drivers.find({'_state': 'absent'}).count()
        == ABSENT_DRIVERS_COUNT
    )
    assert (
        mongodb.drivers.find().count()
        == IMPORTABLE_DRIVERS_WITH_PD_PHONE_COUNT + ABSENT_DRIVERS_COUNT
    )

    taxi_config.set_values(
        dict(
            DRIVERS_IMPORTER_WORK_MODE=get_drivers_importer_work_mode(
                'disabled',
            ),
        ),
    )
    await taxi_driver_profiles.invalidate_caches()

    await wait_iteration(taxi_driver_profiles, JOB_NAME, 'disabled', testpoint)


@pytest.mark.config(
    DRIVERS_IMPORTER_WORK_MODE=get_drivers_importer_work_mode('enabled'),
)
async def test_worker_enabled_pd_fail_500(
        taxi_driver_profiles, taxi_config, testpoint, mongodb, mock_personal,
):
    mock_personal.set_failing(True)

    initial_count = mongodb.drivers.find().count()

    await taxi_driver_profiles.invalidate_caches()
    await wait_iteration(taxi_driver_profiles, JOB_NAME, 'enabled', testpoint)

    assert mongodb.drivers.find({'_state': 'absent'}).count() == 0
    assert mongodb.drivers.find().count() == initial_count

    taxi_config.set_values(
        dict(
            DRIVERS_IMPORTER_WORK_MODE=get_drivers_importer_work_mode(
                'disabled',
            ),
        ),
    )
    await taxi_driver_profiles.invalidate_caches()

    await wait_iteration(taxi_driver_profiles, JOB_NAME, 'disabled', testpoint)
