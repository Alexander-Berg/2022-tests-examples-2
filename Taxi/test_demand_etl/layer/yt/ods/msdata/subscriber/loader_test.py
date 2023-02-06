from nile.api.v1.clusters import MockCluster

from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat

from demand_etl.layer.yt.ods.msdata.subscriber.loader import calculate_subscriber


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_calculate_subscriber(self):
        job = MockCluster().job()

        user_profiles = job.table('dummy').label('user_profiles')
        opk_profiles = job.table('dummy').label('opk_profiles')

        calculate_subscriber(user_profiles, opk_profiles).label('subscriber')

        self.assertCorrectLocalRun(
            job,
            sources={
                'user_profiles': 'user_profiles.json',
                'opk_profiles': 'opk_profiles.json'
            },
            expected_sinks={
                'subscriber': 'subscriber.json'
            }
        )
