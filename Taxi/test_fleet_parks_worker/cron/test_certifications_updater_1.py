# pylint: disable=too-many-lines
# pylint: disable=unused-variable
import datetime

import pytest

from fleet_parks_worker.generated.cron import run_cron

CURR_DATE = datetime.datetime.now().replace(microsecond=0)


YT_PARKS_CERTS = [
    {
        'park_id': '000861c5494e43909c7346ec07179f2f',
        'certified_flg': False,
        'sh_per_driver': 4.54,
        'dpsat': 4.38,
        'churn': 25.4,
        'share_of_bad_grades': 4.61,
        'drivers': 123.1,
        'reason': 'reason1',
        'type': 'type1',
        'expiration_date': '2020-02-06',
        'sh_per_driver_threshold': 4.5,
        'churn_threshold': 20,
        'dpsat_threshold': 3,
        'drivers_threshold': 30,
        'share_of_bad_grades_threshold': 4.5,
        'share_drivers_with_kis_art_id': 11,
        'kis_art_id_threshold': 21,
        'show_kis_art_flg': True,
    },
    {
        'park_id': '111861c5494e43909c7346ec07179f2f',
        'certified_flg': True,
        'sh_per_driver': 2.54,
        'dpsat': 3.38,
        'churn': 50.4,
        'share_of_bad_grades': 4.91,
        'drivers': 123.1,
        'reason': 'reason2',
        'type': 'type2',
        'expiration_date': '2020-02-06',
        'sh_per_driver_threshold': 4.5,
        'churn_threshold': 20,
        'dpsat_threshold': 3,
        'drivers_threshold': 30,
        'share_of_bad_grades_threshold': 4.5,
        'share_drivers_with_kis_art_id': 11,
        'kis_art_id_threshold': 21,
        'show_kis_art_flg': True,
    },
]


MONGO_PARKS_CERTS = [
    {
        '_id': '000861c5494e43909c7346ec07179f2f',
        'is_certified': False,
        'sh_per_driver': 4.54,
        'dpsat': 4.38,
        'churn': 25.4,
        'share_of_bad_grades': 4.61,
        'drivers': 123.1,
        'reason': 'reason1',
        'type': 'type1',
        'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
        'sh_per_driver_threshold': 4.5,
        'churn_threshold': 20,
        'dpsat_threshold': 3,
        'drivers_threshold': 30,
        'share_of_bad_grades_threshold': 4.5,
        'share_drivers_with_kis_art_id': 11,
        'kis_art_id_threshold': 21,
        'show_kis_art_flg': True,
    },
    {
        '_id': '111861c5494e43909c7346ec07179f2f',
        'is_certified': True,
        'sh_per_driver': 2.54,
        'dpsat': 3.38,
        'churn': 50.4,
        'share_of_bad_grades': 4.91,
        'drivers': 123.1,
        'reason': 'reason2',
        'type': 'type2',
        'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
        'sh_per_driver_threshold': 4.5,
        'churn_threshold': 20,
        'dpsat_threshold': 3,
        'drivers_threshold': 30,
        'share_of_bad_grades_threshold': 4.5,
        'share_drivers_with_kis_art_id': 11,
        'kis_art_id_threshold': 21,
        'show_kis_art_flg': True,
    },
]


async def test_insert_certs(patch, mongo):
    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.list'
        ),
    )
    async def yt_list(path, *args, **kwargs):
        assert path.endswith(CURR_DATE.strftime('quarterly/%Y/new_widget'))
        return ['q1', 'q2', 'q3']

    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.read_table'
        ),
    )
    async def yt_read_table(full_path, *args, **kwargs):
        assert full_path.endswith('q3')
        return YT_PARKS_CERTS

    await run_cron.main(
        ['fleet_parks_worker.crontasks.certifications_updater', '-t', '0'],
    )

    mongo_certs = await mongo.parks_certifications.find({}).to_list(None)
    for cert in mongo_certs:
        assert cert.get('updated')
        cert.pop('updated')

    assert mongo_certs == MONGO_PARKS_CERTS


@pytest.mark.parametrize(
    ['mongo_certs', 'updated_count'],
    [
        # sh_per_driver changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'drivers': 123.1,
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.44,  # changed
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # is_certified and churn changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': True,  # changed
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.44,
                    'dpsat': 3.38,
                    'churn': 51.4,  # changed
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            2,
        ),
        # dpsat changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.44,
                    'dpsat': 3.40,  # changed
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.44,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.96,  # changed
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # drivers changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.5,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # type changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type_new',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # reason changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason_new',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # expiration_date changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 5, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # one park absent in mongo
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # share_drivers_with_kis_art_id changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'drivers': 123.1,
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 1,  # changed
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # kis_art_id_threshold changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'drivers': 123.1,
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 20,  # changed
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # show_kis_art_flg changed
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'type': 'type1',
                    'reason': 'reason1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'drivers': 123.1,
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 4.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'type': 'type2',
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': False,  # changed
                },
            ],
            1,
        ),
    ],
)
async def test_update_certs(patch, mongo, mongo_certs, updated_count):
    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.list'
        ),
    )
    async def yt_list(path, *args, **kwargs):
        assert path.endswith(CURR_DATE.strftime('quarterly/%Y/new_widget'))
        return ['q1', 'q2', 'q3']

    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.read_table'
        ),
    )
    async def yt_read_table(full_path, *args, **kwargs):
        assert full_path.endswith('q3')
        return YT_PARKS_CERTS

    await mongo.parks_certifications.insert_many(mongo_certs)

    await run_cron.main(
        ['fleet_parks_worker.crontasks.certifications_updater', '-t', '0'],
    )

    mongo_certs = await mongo.parks_certifications.find({}).to_list(None)
    updated_cnt = 0
    for cert in mongo_certs:
        if cert.get('updated'):
            updated_cnt += 1
            cert.pop('updated')

    assert updated_cnt == updated_count
    assert mongo_certs == MONGO_PARKS_CERTS


@pytest.mark.parametrize(
    ['mongo_certs', 'updated_count'],
    [
        # without is_certified
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without sh_per_driver
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without dpsat
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without churn
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without share_of_bad_grades
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without sh_per_driver and share_of_bad_grades
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            2,
        ),
        #  without drivers
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        #  without type
        (
            [
                {
                    '_id': '000861c5494e43909c7346ec07179f2f',
                    'is_certified': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    '_id': '111861c5494e43909c7346ec07179f2f',
                    'is_certified': True,
                    'sh_per_driver': 2.54,
                    'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'expiration_date': datetime.datetime(2020, 2, 6, 0, 0),
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
    ],
)
async def test_broken_mongo_cert(patch, mongo, mongo_certs, updated_count):
    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.list'
        ),
    )
    async def yt_list(path, *args, **kwargs):
        assert path.endswith(CURR_DATE.strftime('quarterly/%Y/new_widget'))
        return ['q1', 'q2', 'q3']

    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.read_table'
        ),
    )
    async def yt_read_table(full_path, *args, **kwargs):
        assert full_path.endswith('q3')
        return YT_PARKS_CERTS

    await mongo.parks_certifications.insert_many(mongo_certs)

    await run_cron.main(
        ['fleet_parks_worker.crontasks.certifications_updater', '-t', '0'],
    )

    mongo_certs = await mongo.parks_certifications.find({}).to_list(None)
    updated_cnt = 0
    for cert in mongo_certs:
        if cert.get('updated'):
            updated_cnt += 1
            cert.pop('updated')

    assert updated_cnt == updated_count
    assert mongo_certs == MONGO_PARKS_CERTS


@pytest.mark.parametrize(
    ['yt_certs', 'expected_updated'],
    [
        # one park without required field
        (
            [
                {
                    'park_id': '000861c5494e43909c7346ec07179f2f',
                    'certified_flg': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': '2020-02-06',
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
                {
                    'park_id': '111861c5494e43909c7346ec07179f2f',
                    'certified_flg': True,
                    'sh_per_driver': 2.54,
                    # 'dpsat': 3.38,
                    'churn': 50.4,
                    'share_of_bad_grades': 4.91,
                    'drivers': 123.1,
                    'reason': 'reason2',
                    'type': 'type2',
                    'expiration_date': '2020-02-06',
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
        # one park absent in yt
        (
            [
                {
                    'park_id': '000861c5494e43909c7346ec07179f2f',
                    'certified_flg': False,
                    'sh_per_driver': 4.54,
                    'dpsat': 4.38,
                    'churn': 25.4,
                    'share_of_bad_grades': 4.61,
                    'drivers': 123.1,
                    'reason': 'reason1',
                    'type': 'type1',
                    'expiration_date': '2020-02-06',
                    'sh_per_driver_threshold': 4.5,
                    'churn_threshold': 20,
                    'dpsat_threshold': 3,
                    'drivers_threshold': 30,
                    'share_of_bad_grades_threshold': 4.5,
                    'share_drivers_with_kis_art_id': 11,
                    'kis_art_id_threshold': 21,
                    'show_kis_art_flg': True,
                },
            ],
            1,
        ),
    ],
)
async def test_broken_yt_cert(patch, mongo, yt_certs, expected_updated):
    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.list'
        ),
    )
    async def yt_list(path, *args, **kwargs):
        assert path.endswith(CURR_DATE.strftime('quarterly/%Y/new_widget'))
        return ['q1', 'q2', 'q3']

    @patch(
        (
            'fleet_parks_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.read_table'
        ),
    )
    async def yt_read_table(full_path, *args, **kwargs):
        assert full_path.endswith('q3')
        return yt_certs

    await mongo.parks_certifications.insert_many(MONGO_PARKS_CERTS)

    await run_cron.main(
        ['fleet_parks_worker.crontasks.certifications_updater', '-t', '0'],
    )

    mongo_certs = await mongo.parks_certifications.find({}).to_list(None)
    updated_cnt = 0
    for cert in mongo_certs:
        if cert.get('updated'):
            updated_cnt += 1
            cert.pop('updated')
    # nothing was updated
    assert updated_cnt == 0

    # broken yt park deleted from mongo
    assert mongo_certs == [MONGO_PARKS_CERTS[0]]
