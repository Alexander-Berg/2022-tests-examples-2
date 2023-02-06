# -*- coding: utf-8 -*-
import itertools
import json

import sandbox.sdk2 as sdk2
from sandbox.common.errors import TaskFailure
from sandbox.projects.common.differ.json_differ import JsonDiffer
from sandbox.projects.common.differ.printers import PrinterToHtml
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.ydo import ydo_releasers
from sandbox.projects.ydo.testenv import YdoSearchproxyTestWizardResponses, YdoSearchproxyTestPortalResponses


class YdoSearchproxyTestDiff(sdk2.Resource):
    releasers = ydo_releasers


class YdoSearchproxyResponseDiff(sdk2.Task):
    class Context(sdk2.Task.Context):
        has_diff = False

    class Parameters(sdk2.Parameters):
        fail_on_any_error = True
        empty_serp_threshold = sdk2.parameters.Float(
            'threshold of empty serp in [0,1]',
            default_value=0.03
        )
        wizard_resource_1 = sdk2.parameters.Resource(
            'Response wizard 1',
            resource_type=YdoSearchproxyTestWizardResponses
        )
        wizard_resource_2 = sdk2.parameters.Resource(
            'Responses wizard 2',
            resource_type=YdoSearchproxyTestWizardResponses
        )
        portal_resource_1 = sdk2.parameters.Resource(
            'Responses portal 1',
            resource_type=YdoSearchproxyTestPortalResponses
        )
        portal_resource_2 = sdk2.parameters.Resource(
            'Responses portal 2',
            resource_type=YdoSearchproxyTestPortalResponses
        )
        wizard_flag = sdk2.parameters.Bool('count wizard', default_value=True)
        portal_flag = sdk2.parameters.Bool('count portal', default_value=True)
        diff_flag = sdk2.parameters.Bool('count diff', default_value=True)
        with sdk2.parameters.Output:
            has_diff = sdk2.parameters.Bool('has diff', required=True)
            has_wizard_diff = sdk2.parameters.Bool('has wizard diff', required=True)
            has_portal_diff = sdk2.parameters.Bool('has portal diff', required=True)
            hit_empty_serp = sdk2.parameters.Bool('hit empty serp threshold', required=True)
            empty_serp_count = sdk2.parameters.Integer('number empty serps', required=True)

    def on_execute(self):
        has_wizard_diff = False
        if self.Parameters.wizard_flag:
            left, right = self._read_responses(
                self.Parameters.wizard_resource_1,
                self.Parameters.wizard_resource_2
            )
            left_empty, right_empty, left, right = self._split_empty_responses(left, right)
            self.Context.empty_serp_wizard_count = len(left_empty)
            self.Context.wizard_responses_count = len(left) + len(left_empty)
            self._process_wizard_responses(left, right)
            has_empty_wizard_diff, empty_wizard_diff_res_id = self._count_diff(left_empty, right_empty, 'empty_wizard_diff', 'diff empty wizard')
            has_wizard_diff, wizard_diff_res_id = self._count_diff(left, right, 'wizard_diff', 'diff wizard')
        else:
            self.Context.empty_serp_wizard_count = 0
            self.Context.wizard_responses_count = 0

        has_portal_diff = False
        if self.Parameters.portal_flag:
            left, right = self._read_responses(
                self.Parameters.portal_resource_1,
                self.Parameters.portal_resource_2
            )
            left_empty, right_empty, left, right = self._split_empty_responses(left, right)
            self.Context.empty_serp_portal_count = len(left_empty)
            self.Context.portal_responses_count = len(left) + len(left_empty)
            self._process_portal_responses(left, right)
            has_empty_portal_diff, empty_portal_diff_res_id = self._count_diff(left_empty, right_empty, 'empty_portal_diff', 'diff empty portal')
            has_portal_diff, portal_diff_res_id = self._count_diff(left, right, 'portal_diff', 'diff portal')
        else:
            self.Context.empty_serp_portal_count = 0
            self.Context.portal_responses_count = 0

        self.Parameters.has_wizard_diff = has_wizard_diff
        self.Parameters.has_portal_diff = has_portal_diff
        self.Parameters.has_diff = has_wizard_diff or has_portal_diff
        self.Parameters.empty_serp_count = self.Context.empty_serp_wizard_count + self.Context.empty_serp_portal_count
        hit_empty_wizard_serp = self.Context.empty_serp_wizard_count >= int(self.Parameters.empty_serp_threshold * self.Context.wizard_responses_count)
        hit_empty_portal_serp = self.Context.empty_serp_portal_count >= int(self.Parameters.empty_serp_threshold * self.Context.portal_responses_count)
        self.Parameters.hit_empty_serp = hit_empty_wizard_serp or hit_empty_portal_serp

        if self.Parameters.has_diff or self.Parameters.hit_empty_serp:
            error_msg = ''
            resource_link_tmp = 'https://proxy.sandbox.yandex-team.ru/{resource_id}'
            if self.Parameters.has_diff:
                error_tmp = '{type} has diff. See <a href="{resource_link}">{resource_link}</a>.'
                if has_wizard_diff:
                    resource_link = resource_link_tmp.format(resource_id=wizard_diff_res_id)
                    error_msg = '\n'.join((error_msg, error_tmp.format(type='Wizard', resource_link=resource_link)))
                if has_portal_diff:
                    resource_link = resource_link_tmp.format(resource_id=portal_diff_res_id)
                    error_msg = '\n'.join((error_msg, error_tmp.format(type='Portal', resource_link=resource_link)))

            if self.Parameters.hit_empty_serp:
                error_msg = '\n'.join((
                    error_msg,
                    '{empty} from {count} responses under wizard is empty. Should be less than {threshold}.'.format(
                        empty=self.Context.empty_serp_wizard_count,
                        count=self.Context.wizard_responses_count,
                        threshold=int(self.Parameters.empty_serp_threshold * self.Context.wizard_responses_count)
                    ),
                    '{empty} from {count} responses under portal is empty. Should be less than {threshold}.'.format(
                        empty=self.Context.empty_serp_portal_count,
                        count=self.Context.portal_responses_count,
                        threshold=int(self.Parameters.empty_serp_threshold * self.Context.portal_responses_count)
                    )
                ))

                if has_empty_wizard_diff or has_empty_portal_diff:
                    error_msg = '\n'.join((error_msg, 'If you want to see diff in empty serp responses, see'))
                    if has_empty_wizard_diff:
                        resource_link = resource_link_tmp.format(resource_id=empty_wizard_diff_res_id)
                        error_msg = ' '.join((error_msg, '<a href="{resource_link}">wizard</a> or'.format(resource_link=resource_link)))
                    if has_empty_portal_diff:
                        resource_link = resource_link_tmp.format(resource_id=empty_portal_diff_res_id)
                        error_msg = ' '.join((error_msg, '<a href="{resource_link}">portal</a>.'.format(resource_link=resource_link)))

            eh.check_failed(error_msg)

    def _split_empty_responses(self, left, right):
        left_empty = []
        right_empty = []

        left_nonempty = []
        right_nonempty = []

        for query in left.keys():
            if left[query]['arrange'] and right[query]['arrange']:
                left_nonempty.append(left.pop(query))
                right_nonempty.append(right.pop(query))
            else:
                left_empty.append(left.pop(query))
                right_empty.append(right.pop(query))

        return left_empty, right_empty, left_nonempty, right_nonempty

    def _read_responses(self, left, right):
        def load_response(resource):
            with open(str(sdk2.ResourceData(resource).path), 'r') as file:
                return json.load(file)

        def post_processing(responses):
            return {r['query']: r for r in responses}

        def chain(resource):
            return post_processing(load_response(resource))

        return chain(left), chain(right)

    def _process_wizard_responses(self, left, right):
        def post_processing(responses):
            for r in responses:
                r.pop('url')
                serpData = r.get('gta', {}).get('_SerpData', {})
                people = serpData.get('peoples', [])
                serpData['peoples'] = {worker['worker_id']: worker for worker in people}

        post_processing(left)
        post_processing(right)

    def _get_portal_url(self, doc):
        return doc['Document'][0]['ArchiveInfo']['Url']

    def _process_portal_responses(self, left, right):
        def post_processing(responses):
            for r in responses:
                r.pop('url')
                docs = r.get('docs', [])
                r['docs'] = {self._get_portal_url(doc): doc for doc in docs}

        post_processing(left)
        post_processing(right)

    def _count_diff(self, left, right, diff_dir, description):
        diff_dir = sdk2.path.Path(diff_dir)
        if not diff_dir.exists():
            diff_dir.mkdir()

        resource = YdoSearchproxyTestDiff(self, description, str(diff_dir))
        resourceData = sdk2.ResourceData(resource)

        printer = PrinterToHtml(str(diff_dir), write_compact_diff=False)
        differ = JsonDiffer(printer)

        def generate_pairs(left, right):
            for (x, y) in itertools.izip(left, right):
                if x['query'] != y['query']:
                    TaskFailure('Requests not matched: {} and {}'.format(x['query'], y['query']))

                yield (json.dumps(x, ensure_ascii=False), json.dumps(y, ensure_ascii=False), x['query'])

        differ.compare_pairs(generate_pairs(left, right))

        resourceData.ready()

        return bool(differ.get_diff_count()), resource.id
