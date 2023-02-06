# pylint: disable=unused-variable
import datetime


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


INITIAL_MONGO_PARK_CERT = {
    '_id': '999961c5494e43909c7346ec07179f9D',
    'is_certified': False,
    'dpsat': 0.0,
    'churn_threshold': 20,
    'dpsat_threshold': 3,
    'drivers_threshold': 30,
    'share_drivers_with_kis_art_id': 11,
    'kis_art_id_threshold': 21,
    'show_kis_art_flg': True,
}


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


async def test_excess_mongo_parks(patch, mongo):
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

    await mongo.parks_certifications.insert_one(INITIAL_MONGO_PARK_CERT)

    await run_cron.main(
        ['fleet_parks_worker.crontasks.certifications_updater', '-t', '0'],
    )

    mongo_certs = await mongo.parks_certifications.find({}).to_list(None)
    for cert in mongo_certs:
        assert cert.get('updated')
        cert.pop('updated')

    # initial mongo cert was deleted
    assert mongo_certs == MONGO_PARKS_CERTS
