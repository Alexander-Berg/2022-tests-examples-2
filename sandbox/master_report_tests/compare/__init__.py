from __future__ import print_function

import cPickle as pickle
import json
import os

from sandbox.sdk2 import (
    Resource,
    ResourceData,
    parameters,
)
from sandbox.projects.yabs.master_report_tests.resources import (
    YabsMasterReportCompareResults,
    YabsMasterReportRequests,
    YabsMasterReportSpec,
    YabsMasterReportShootResults
)
from sandbox.projects.yabs.base_bin_task import BaseBinTask


INDEX_TEMPLATE = '''
Requests: total {reqs}, diverged {div} ({div_rate:.2%}), errors {err} ({err_rate:.2%})
Coulmns statistics: <a href="{resource_url}/columns.txt">link</a>
Detailed report: <a href="{resource_url}/report.html">link</a>
'''.replace('\n', '<br>')

DIR_NAME = 'report'


def to_unicode(obj):
    if isinstance(obj, basestring) and not isinstance(obj, unicode):
        return unicode(obj, 'utf8')
    if isinstance(obj, list):
        return map(to_unicode, obj)
    if isinstance(obj, dict):
        return {k: to_unicode(v) for k, v in obj.iteritems()}
    return obj


class YabsMasterReportCompare(BaseBinTask):
    '''Compares master report shoot results'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Compare shoot results'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Compare') as compare_params:
            stable_resource = parameters.Resource(
                'Stable (canonical) shoot results',
                resource_type=YabsMasterReportShootResults,
                required=True,
            )
            test_resource = parameters.Resource(
                'Test shoot results',
                resource_type=YabsMasterReportShootResults,
                required=True,
            )
            requests_resource = parameters.Resource(
                'Resource with requests',
                resource_type=YabsMasterReportRequests,
                required=False,
            )
            spec_resource = parameters.Resource(
                'Resource with backup spec',
                resource_type=YabsMasterReportSpec,
                required=False,
            )
            excluded_columns = parameters.List(
                'Excluded columns',
                default=[],
            )
            accuracy = parameters.Float(
                'Permissible relative error',
                default=0.01,
                required=True,
            )
            errors_rate = parameters.Float(
                'Error log scale value',
                default=0.0000000001,
                required=True,
            )
            max_err_rate = parameters.Float(
                'Max err rate',
                default=0.9,
                required=True,
            )

    def cmp_generator(self):
        if self.Parameters.spec_resource:
            spec_file = ResourceData(self.Parameters.spec_resource)
            with open(str(spec_file.path), 'r') as f:
                res_id = json.load(f)['requests']
                requests_resource = Resource.find(id=res_id).first()
        else:
            requests_resource = self.Parameters.requests_resource

        requests_file = ResourceData(requests_resource)
        with open(str(requests_file.path), 'r') as f:
            requests = json.load(f)['requests']

        stable_file = ResourceData(self.Parameters.stable_resource)
        test_file = ResourceData(self.Parameters.test_resource)
        with open(str(stable_file.path), 'r') as stable:
            with open(str(test_file.path), 'r') as test:
                for i, req in enumerate(requests):
                    try:
                        yield req, pickle.load(stable), pickle.load(test)
                    except EOFError:
                        raise Exception('Different number of requests and responses: failed to load response {}'.format(i))

    def compare(self):
        from yabs.interface.yabs_export_scripts_fast.comparing_request import ComparisonResult, IncorrectRequestInfo

        result = ComparisonResult(correct=0, num_rows=0)
        for req, stable, test in self.cmp_generator():
            result_row = test.compare_responses(stable, self.Parameters.accuracy, self.Parameters.excluded_columns)
            if result_row.err:
                result_row.incorrect_requests.append(IncorrectRequestInfo(req, {}, error=True,
                                                                          pre_text=test.text, prod_text=stable.text))
            result.add_row(result_row)

        return result

    def create_detailed_report(self, result):
        import jinja2
        from library.python import resource
        from yabs.interface.yabs_export_scripts_fast.comparing_request import gen_detailed_report

        details = to_unicode(gen_detailed_report(result))

        res = resource.find('master_report_template.jinja2')
        template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(res)
        text = template.render(
            start_time='-',
            finish_time='-',
            pre='test',
            prod='stable',
            num_rows=result.num_rows,
            correct=result.correct,
            requests_with_discrepancies=details['discrepancies'],
            requests_with_errors=details['errors'],
            columns=details['columns'],
            different_set_of_keys=details["different_set_of_keys"],
            pre_err=result.pre_err,
            prod_err=result.prod_err,
            new_err=result.new_err,
            fixed_err=result.fixed_err
        )

        with open(os.path.join(DIR_NAME, 'report.html'), 'w') as f:
            for line in text.split('\n'):
                line = line.encode('utf-8').strip()
                if line != '':
                    f.write(line)

    def create_columns_report(self, result):
        from yabs.interface.yabs_export_scripts_fast.comparing_request import get_stat

        with open(os.path.join(DIR_NAME, 'columns.txt'), 'w') as f:
            for col, col_res in result.columns.iteritems():
                f.write('{}: {} discrepancies, inaccuracy = {}\n'.format(col, col_res['discrepancies'], len(col_res['inaccuracy'])))
                if len(col_res['inaccuracy']) > 0:
                    f.write('Inaccuracy stat {}\n'.format(get_stat(col_res['inaccuracy'], self.Parameters.errors_rate, self.Parameters.max_err_rate)))

    def create_index(self, result, url):
        diverged = result.num_rows - result.correct - result.err
        summary = INDEX_TEMPLATE.format(
            reqs=result.num_rows,
            div=diverged,
            div_rate=float(diverged) / result.num_rows,
            err=result.err,
            err_rate=float(result.err) / result.num_rows,
            resource_url=url,
        )
        with open(os.path.join(DIR_NAME, 'index.html'), 'w') as f:
            f.write(summary)
        self.set_info(summary, do_escape=False)
        if diverged > 0 or result.fixed_err > 0 or result.new_err > 0:
            self.Context.has_diff = True

    def on_execute(self):
        self.Context.has_diff = False
        os.makedirs(DIR_NAME)

        result = self.compare()
        self.create_detailed_report(result)
        self.create_columns_report(result)

        res = YabsMasterReportCompareResults(
            self,
            'Report resource',
            DIR_NAME
        )
        self.create_index(result, res.http_proxy)
