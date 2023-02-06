# -*- coding: utf-8 -*-
import os
import logging
from collections import defaultdict

import jinja2
import sys
import json

import sandbox.sandboxsdk.svn
from sandbox import sdk2
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.channel import channel

from sandbox.projects.common import utils


def parse_emails(emails_str):
    return [i.strip() for i in emails_str.split(',')]


def format_staff(user):
    return '<a href="https://staff.yandex-team.ru/%s">%s@</a>' % (user, user)


def parse_arcadia_url(url):
    a = url.split('://')
    b = a[1].split('@')
    revision = b[1]
    return revision


def stringify_value(value):
    primitives = (int, str, bool, type(None), unicode)

    if isinstance(value, primitives):
        logging.info("Primitive: {}".format(value))
        return str(value)
    logging.info("Complex: {}: {}".format(value, type(value)))
    return json.dumps(value)


def difference_changes(list_prev_changes, list_cur_changes, name_file, diffs, strict=False):
    def get_hist_id(hist):
        return hist['key'] + '|' + hist['calc_type'] + '|' + hist['time']

    id_to_prev_changes = {get_hist_id(ele): ele for ele in list_prev_changes}
    id_to_cur_changes = {get_hist_id(ele): ele for ele in list_cur_changes}

    prev_ids = set(id_to_prev_changes)
    cur_ids = set(id_to_cur_changes)

    if not prev_ids.intersection(cur_ids):
        msg = 'Changes of {} maybe lost'.format(name_file)
        logging.warning(msg)
        if strict:
            raise RuntimeError(msg)

    dict_changes = defaultdict(lambda: defaultdict(list))
    new_id = cur_ids.difference(prev_ids)
    for id_change in new_id:
        ele = id_to_cur_changes[id_change]
        name = ele['author']

        if ele['action'] == 'POST':
            if ele['key'] in diffs.added or ele['key'] in diffs.added_feature:
                action = 'Added'
            else:
                # if metric wasn't changed during update
                continue
        else:
            if ele['key'] in diffs.removed or ele['key'] in diffs.removed_feature:
                action = 'Removed'
            else:
                action = 'Transformed'

        changes = None
        if ele['changes']:
            if not ele['key'] in diffs.diff and not ele['key'] in diffs.diff_feature:
                logging.info('Ignoring {} in diff'.format(ele['key']))
            else:
                logging.info("Adding {} with diff in changes".format(ele['key']))
                changes = ele['changes']

                for key in changes.keys():
                    changes[key] = [(r'<font color="red">' + stringify_value(changes[key][0]) + r"</font>",
                                     r'<font color="green">' + stringify_value(changes[key][1]) + r"</font>")]

                changes['timestamp'] = ele['time']
                changes['key'] = '<b>'+ele['key']+r'</b>'

        if changes:
            logging.info("Name: {}, Action: {}, changes: {}".format(name, action, changes))
            dict_changes[name][action].append(changes)
        elif action == 'Added' or action == 'Removed':
            dict_changes[name][action].append('<b>'+ele['key']+r'</b>')

    for name, name_to_action in dict_changes.items():
        for action, action_to_changes in name_to_action.items():
            if isinstance(action_to_changes[0], str):
                dict_changes[name][action].sort()

    return dict_changes


class DiffABTMetrics(SandboxTask):
    """
    Compares two metric result outputs from RunABTMetrics and sends angry email
    """
    type = 'DIFF_ABT_METRICS'

    class EmailTo(SandboxStringParameter):
        name = 'email_to'
        description = 'Send emails with any diff report to'

    class DiffEmailTo(SandboxStringParameter):
        name = 'diff_email_to'
        description = 'Send emails with diverse diff report to'

    class Date(SandboxStringParameter):
        """
        Date for calculations
        """
        name = 'date'
        description = 'DATE for calculations YYYYMMDD'
        default_value = '20150120'

    class SamplePath(SandboxStringParameter):
        """
        User sessions sample path
        """
        name = 'sample_path'
        description = 'Sample path'

    class Metrics1(SandboxStringParameter):
        """
        Metrics file output from one revision of stat tools
        """
        name = 'metrics1_id'
        description = 'metrics_id #1'

    class Metrics2(SandboxStringParameter):
        """
        Metrics file output from second revision of stat tools
        """
        name = 'metrics2_id'
        description = 'metrics_id #2'

    class RevisionUrls(SandboxStringParameter):
        """
        Semicolon-separated revisions with branch prefix.
        Examples: "arcadia:/arc/trunk/arcadia@1599640;arcadia:/arc/trunk/arcadia@1611111"
        """
        name = 'revision_urls'
        description = 'Semicolon-separated revision urls'

    class CommitAuthor(SandboxStringParameter):
        name = 'commit_author'
        description = 'Commit author (Optional)'
        default_value = ''

    class CommitMessage(SandboxStringParameter):
        name = 'commit_message'
        description = 'Commit messsage (Optional)'
        default_value = ''

    class CommitPaths(SandboxStringParameter):
        name = 'commit_paths'
        description = 'Commit path (Optional)'
        default_value = ''

    input_parameters = [EmailTo, DiffEmailTo, Date, SamplePath, Metrics1, Metrics2, RevisionUrls, CommitAuthor, CommitMessage, CommitPaths]

    def __init__(self, *args, **kwargs):
        SandboxTask.__init__(self, *args, **kwargs)

    def on_execute(self):
        id_metric1 = int(utils.get_or_default(self.ctx, self.Metrics1))
        id_metric2 = int(utils.get_or_default(self.ctx, self.Metrics2))
        m1_file = self.sync_resource(id_metric1)
        m2_file = self.sync_resource(id_metric2)

        shellabt_path = sandbox.sandboxsdk.svn.Arcadia.get_arcadia_src_dir(
            "arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/"
        )
        sys.path.append(shellabt_path)

        import shellabt

        diff_report = shellabt.diff_suite_files(m1_file, m2_file)

        has_diff = diff_report.has_diff()
        self.ctx['has_diff'] = has_diff

        diff_html = diff_report.format_html()

        arcadia_urls = utils.get_or_default(self.ctx, self.RevisionUrls).split(';')
        prev_commit_revision = parse_arcadia_url(arcadia_urls[0])
        commit_revision = parse_arcadia_url(arcadia_urls[1])

        prev_resource = sdk2.Resource.find(id=id_metric1).first()
        cur_resource = sdk2.Resource.find(id=id_metric2).first()
        name_files = ['metrics.json', 'feature_custom.json']
        name_ids = ['metrics_id', 'features_id']

        def get_changes_by_id(resource_id):
            with open(str(sdk2.ResourceData(sdk2.Resource.find(id=resource_id).first()).path), 'r') as f:
                return json.load(f)['changes_info']['changes']

        dict_changes = {}
        for name_file, name_id in zip(name_files, name_ids):
            value_id1 = getattr(prev_resource, name_id, None)
            value_id2 = getattr(cur_resource, name_id, None)

            if not value_id1 or not value_id2 or value_id1 == value_id2:
                logging.info("Skipping... value_id1:{}, value_id2:{}".format(value_id1, value_id2))
                continue

            list_prev_changes = get_changes_by_id(value_id1)
            list_cur_changes = get_changes_by_id(value_id2)

            changes = difference_changes(list_prev_changes, list_cur_changes, name_file, diffs=diff_report)
            logging.info('Changes for name_file: {}: \n{}'.format(name_file, changes))
            dict_changes.update(changes)

        commit_author = utils.get_or_default(self.ctx, self.CommitAuthor)
        logging.info("Json changes: {}".format(json.dumps(dict_changes, indent=4)))
        context = {
            'diff_formatted': diff_html,
            'commit_revision': commit_revision,
            'commit_author': commit_author,
            'commit_author_formatted': format_staff(commit_author),
            'commit_message': utils.get_or_default(self.ctx, self.CommitMessage),
            'updates_resources': dict_changes,
        }

        template_path = os.path.dirname(os.path.abspath(__file__))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

        def to_pretty_json(js_object):
            res = json.dumps(js_object, indent=2, sort_keys=True)
            res = res.replace(r'"<font', '<font').replace(r'</font>"', r'</font>').replace(r'\"red\"', "red").replace(r'\"green\"', "green")
            return '\n'+res

        env.filters['to_pretty_json'] = to_pretty_json

        template = env.get_template('email-template.html')
        full_html = template.render(context)

        report_file = 'report.html'
        report_file = os.path.abspath(report_file)
        with open(report_file, 'wt') as report:
            report.write(full_html.encode('utf-8'))
        resource = self.create_resource('ABT report', report_file, 'TEST_ABT_METRICS_DIFF_REPORT', attributes={'ttl': 200})

        preview_link = 'https://proxy.sandbox.yandex-team.ru/%d' % resource.id
        preview_html = diff_report.format_html(preview_link)
        report_file = 'report_preview.html'
        report_file = os.path.abspath(report_file)
        with open(report_file, 'wt') as report:
            report.write(preview_html.encode('utf-8'))
        self.create_resource('ABT report', report_file, 'TEST_ABT_METRICS_DIFF_REPORT_PREVIEW', attributes={'ttl': 200})

        email_title = 'Report on Adminka metrics/features changes:'
        email_title += ' %s-%s by %s@' % (prev_commit_revision, commit_revision, commit_author)

        send_email = True

        email_to = set(parse_emails(utils.get_or_default(self.ctx, self.EmailTo)))

        for ele in list(email_to):
            if ele.startswith('robot-'):
                email_to.remove(ele)

        if dict_changes or has_diff:
            all_email_receivers = list(set(email_to).union(set(dict_changes.keys())))

            if send_email:
                logging.info('Sending mail to: ' + ', '.join(all_email_receivers))
                headers = ['Reply-to: ' + ', '.join((email + '@yandex-team.ru' for email in all_email_receivers))]
                channel.sandbox.send_email(all_email_receivers, None, email_title, full_html, 'text/html', 'utf-8', extra_headers=headers)


__Task__ = DiffABTMetrics
