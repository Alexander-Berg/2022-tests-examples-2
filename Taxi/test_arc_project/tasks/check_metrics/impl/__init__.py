import logging

from tasklet.services.yav.proto import yav_pb2 as yav
from taxi.eda.test_arc_project.tasks.check_metrics.proto import check_metrics_tasklet
from yql.api.v1.client import YqlClient


class CheckMetricsImpl(check_metrics_tasklet.CheckMetricsBase):

    def run(self):
        revision: str = self.input.context.target_revision.hash
        current_ratio: float = self.input.config.current_ratio

        secret_uid = self.input.context.secret_uid
        yav_key_name = 'YT_PERSONAL_OAUTH'
        spec = yav.YavSecretSpec(uuid=secret_uid, key=yav_key_name)
        token_value = self.ctx.yav.get_secret(spec).secret

        service_name = 'eats-launch'

        query = f"""
        select metric_name, value from autocheck.metrics
        where subtest_name = 'test_api_coverage'
        and path like 'taxi/uservices/services/%'
        and metric_name = 'api_coverage.{service_name}.coverage_ratio'
        order by revision desc;
        """
        logging.info('Running on revision "%s"', revision)

        logging.info('Running YT query "%s"', query)
        client = YqlClient(db='ci_public', token=token_value)
        request = client.query(query=query, syntax_version=1, clickhouse_syntax=True)
        request.run()
        results = request.get_results()

        if not request.is_success:
            if request.errors:
                errors = str([str(error)+'\n' for error in request.errors])
                raise Exception('Returned errors: \n' + errors)

        logging.info('Fetched %d records', len(results.table.rows))
        reference_coverage_ratio = results.table.rows[0][1]
        logging.info(f'api_coverage.{service_name}.coverage_ratio = {reference_coverage_ratio}')
        if reference_coverage_ratio > current_ratio:
            raise Exception(f'reference value is less than current: {reference_coverage_ratio} < {current_ratio}')
        self.output.result.message = 'Success'
