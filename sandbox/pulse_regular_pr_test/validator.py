import logging


class Validator(object):
    def __init__(self, master_task, config):
        """
        :type master_task: sandbox.projects.sandbox_ci.pulse.pulse_regular_pr_test.PulseRegularPrTest
        :type config: sandbox.projects.sandbox_ci.pulse.pulse_regular_pr_test.config.Config
        """
        self._master_task = master_task
        self._config = config

    def check_shooting_task(self, task):
        """
        :type task: sandbox.projects.sandbox_ci.pulse.pulse_shooter.PulseShooter
        """
        platform = task.Parameters.platform
        shooting_diff = task.Parameters.results
        errors = []

        if not shooting_diff:
            return ['Unable to read diff from task context']

        for stage_data in shooting_diff:
            rows = stage_data.get('rows')
            stage_name = stage_data.get('subtitle')
            if not rows:
                continue

            for row_data in rows:
                metric_name = row_data.get('raw_name')
                if metric_name is None:
                    logging.warn('Empty name for {}'.format(row_data))
                    continue

                for aggr_data in row_data['values']:
                    aggr_name = aggr_data.get('aggr_name')
                    diff = aggr_data.get('delta')

                    if aggr_name is None or diff is None:
                        logging.warn('There is no data for {}:{}'.format(metric_name, aggr_name))
                        continue

                    limits = self._config.shooting_limit_for(platform, stage_name, metric_name, aggr_name)

                    if not limits:
                        logging.warn('Limits for {} {} {} {} was not specified'.format(
                            platform,
                            stage_name,
                            metric_name,
                            aggr_name
                        ))
                        continue

                    min_limit, max_limit = limits

                    if diff < min_limit or diff > max_limit:
                        errors.append('[{} | {} | {} | {}] - min={}, max={}, actual={}'.format(
                            platform,
                            stage_name,
                            metric_name,
                            aggr_name,
                            min_limit,
                            max_limit,
                            diff
                        ))

        return errors

    def check_static_task(self, task):
        """
        :type task: sandbox.projects.sandbox_ci.pulse.pulse_static.PulseStatic
        """
        static_diff = task.Parameters.results
        errors = []

        if not static_diff:
            return ['Unable to read diff from task context']

        for stage_data in static_diff:
            platform = stage_data.get('title')
            rows = stage_data.get('rows')
            aggregations = stage_data.get('aggregations')
            if not rows:
                continue

            for row_data in rows:
                metric_name = row_data.get('raw_name')
                if metric_name is None:
                    logging.warn('Empty name for {}'.format(row_data))
                    continue

                values = row_data['values']
                i = 0
                sizeofValues = len(values)

                while i < sizeofValues:
                    aggr_data = values[i]
                    aggr_name = aggregations[i]
                    diff = aggr_data.get('delta')

                    if aggr_name is None or diff is None:
                        print('There is no data for {}:{}'.format(metric_name, aggr_name))
                        i += 1
                        continue

                    limits = self._config.static_limit_for(platform, aggr_name)

                    if not limits:
                        print('Limits for {} {} {} was not specified'.format(
                            platform,
                            metric_name,
                            aggr_name
                        ))
                        i += 1
                        continue

                    min_limit, max_limit = limits

                    if diff < min_limit or diff > max_limit:
                        errors.append('[{} | {} | {}] - min={}, max={}, actual={}'.format(
                            platform,
                            metric_name,
                            aggr_name,
                            min_limit,
                            max_limit,
                            diff
                        ))

                    i += 1

        return errors
