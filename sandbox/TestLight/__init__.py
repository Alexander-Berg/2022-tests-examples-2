import logging

import sandbox.common.types.client as ctc

from sandbox.projects import resource_types
import sandbox.projects.yane.common as yane
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.parameters import LastReleasedResource, SandboxStringParameter, SandboxBoolParameter
from sandbox.sandboxsdk.paths import make_folder, remove_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.svn import Arcadia


TOP_DIFF_OBJECT_COUNT = 5
TESTING_SUFFIX = '_testing'

FULL_DIFF_FILE_NAME = 'hypos_diff.txt'
LOST_HYPOS_FILE_NAME = 'lost_hypos.txt'
ADDED_HYPOS_FILE_NAME = 'added_hypos.txt'

FULL_DIFF_CHARSET = 'utf-8'
HTML_REPORT_CHARSET = 'utf-8'  # 'ISO-8859-5'

DEFAULT_LANGS = ('rus', 'eng')
DEFAULT_SVN_DATA_PATH = 'data/dict/ner'


def resize(list_pointer, size, default_value):
    assert isinstance(list_pointer, list)

    if len(list_pointer) < size:
        list_pointer += [default_value] * (size - len(list_pointer))


def compute_sorted_list_diff(old_list, new_list):
    items_loss = []
    items_added = []

    old_index = 0
    new_index = 0
    while old_index < len(old_list) and new_index < len(new_list):
        if old_list[old_index] == new_list[new_index]:
            old_index += 1
            new_index += 1
        elif old_list[old_index] < new_list[new_index]:
            items_loss.append(old_list[old_index])
            old_index += 1
        else:
            items_added.append(new_list[new_index])
            new_index += 1

    items_loss += old_list[old_index:]
    items_added += new_list[new_index:]

    return items_loss, items_added


def count_rows_by_col(table, col_num, col_name='id', count_name='count'):
    counts = dict()
    for row in table:
        if row[col_num] not in counts:
            counts[row[col_num]] = 0
        counts[row[col_num]] += 1

    ordered_counts = sorted(counts.items(), key=lambda k: k[1], reverse=True)
    named_counts = [{col_name: id, count_name: count} for id, count in ordered_counts]

    return named_counts


def agregate_rows_by_col(table, col_num):
    sub_tables = dict()
    for row in table:
        if row[col_num] not in sub_tables:
            sub_tables[row[col_num]] = list()
        sub_tables[row[col_num]].append(row)

    return sub_tables


def write_hypos_to_file(records, hypos_texts, file_name):
    with open(file_name, "w") as output_file:
        for record in records:
            output_file.write('\t'.join((record['id'], hypos_texts[record['id']].encode('utf-8'), str(record['count']))) + '\n')


def read_markup(markup_file_path):
    markup = {}
    with open(markup_file_path, "r") as markup_file:
        for line in markup_file:
            parts = line.strip().split('\t')
            documentId, objectId, beginPosition, size = parts[:4]
            markup_key = (documentId, objectId, beginPosition, size)
            markup[markup_key] = (parts[-1] == 't')

    return markup


class HyposDistribution:
    def __init__(self):
        self.winner_hypos = []
        self.loser_hypos = []
        self.uncovered_hypos = []

    def get_hypos_count(self):
        return (
            len(self.winner_hypos) +
            len(self.loser_hypos) +
            len(self.uncovered_hypos)
        )


class HyposDistributionDiff:
    def __init__(self):
        self.winner_hypos_loss = []
        self.winner_hypos_added = []
        self.loser_hypos_loss = []
        self.loser_hypos_added = []
        self.uncovered_hypos_loss = []
        self.uncovered_hypos_added = []

        self.loss_hypos_counters = []
        self.added_hypos_counters = []
        self.loss_docs_counters = []
        self.added_docs_counters = []

    def get_loss(self):
        return (
            self.winner_hypos_loss +
            self.loser_hypos_loss +
            self.uncovered_hypos_loss
        )

    def get_added(self):
        return (
            self.winner_hypos_added +
            self.loser_hypos_added +
            self.uncovered_hypos_added
        )

    def get_total_loss(self):
        return (
            len(self.winner_hypos_loss) +
            len(self.loser_hypos_loss) +
            len(self.uncovered_hypos_loss)
        )

    def get_total_added(self):
        return (
            len(self.winner_hypos_added) +
            len(self.loser_hypos_added) +
            len(self.uncovered_hypos_added)
        )

    def has_diff(self):
        return not (self.get_total_loss() + self.get_total_added() == 0)


def compute_hypos_diff(first_distr, second_distr):
    diff_stats = HyposDistributionDiff()

    diff_stats.winner_hypos_loss, diff_stats.winner_hypos_added = compute_sorted_list_diff(first_distr.winner_hypos, second_distr.winner_hypos)
    diff_stats.loser_hypos_loss, diff_stats.loser_hypos_added = compute_sorted_list_diff(first_distr.loser_hypos, second_distr.loser_hypos)
    diff_stats.uncovered_hypos_loss, diff_stats.uncovered_hypos_added = compute_sorted_list_diff(first_distr.uncovered_hypos, second_distr.uncovered_hypos)

    diff_stats.loss_winner_hypos_counters = count_rows_by_col(diff_stats.winner_hypos_loss, 1)
    diff_stats.added_winner_hypos_counters = count_rows_by_col(diff_stats.winner_hypos_added, 1)

    diff_stats.freq_total_lost = float(diff_stats.get_total_loss()) / first_distr.get_hypos_count()
    diff_stats.freq_total_added = float(diff_stats.get_total_added()) / first_distr.get_hypos_count()

    diff_stats.freq_winner_lost = float(len(diff_stats.winner_hypos_loss)) / len(first_distr.winner_hypos)
    diff_stats.freq_winner_added = float(len(diff_stats.winner_hypos_added)) / len(first_distr.winner_hypos)

    return diff_stats


def get_hypo_text(hypo, document_text):
    hypo_start = int(hypo[2])
    hypo_end = hypo_start + int(hypo[3])
    hypo_text = document_text[hypo_start: hypo_end]

    return hypo_text


def extract_most_freq_texts(hypos, texts_pool_path):
    hypos_by_doc = agregate_rows_by_col(hypos, 0)
    hypos_texts = dict()

    with open(texts_pool_path, "r") as texts_pool:
        for line in texts_pool:
            parts = line.strip().split('\t')
            document_id, document_text = parts[0], ' '.join(parts[1:]).decode('utf-8')

            if document_id in hypos_by_doc:
                for hypo in hypos_by_doc[document_id]:
                    hypo_id = hypo[1]
                    hypo_text = get_hypo_text(hypo, document_text)

                    if hypo_id not in hypos_texts:
                        hypos_texts[hypo_id] = dict()
                    if hypo_text not in hypos_texts[hypo_id]:
                        hypos_texts[hypo_id][hypo_text] = 0
                    hypos_texts[hypo_id][hypo_text] += 1

    most_freq_texts = dict()
    for id, texts in hypos_texts.items():
        text = sorted(texts.items(), key=lambda k: k[1], reverse=True)[0][0]
        most_freq_texts[id] = text

    return most_freq_texts


def create_full_diff_file(markup_diff, texts_pool_path, file_name):

    def fill_document_diff_list(hypos, document_id, document_text, flag, diff_by_object_id):
        for hypo in hypos:
            object_id = hypo[1]
            hypo_begin = hypo[2]
            hypo_text = get_hypo_text(hypo, document_text)

            if object_id not in diff_by_object_id:
                diff_by_object_id[object_id] = []
            diff_by_object_id[object_id].append((object_id, hypo_text.encode(FULL_DIFF_CHARSET), document_id, hypo_begin, flag))

    lost_hypos_by_doc = agregate_rows_by_col(markup_diff.get_loss(), 0)
    added_hypos_by_doc = agregate_rows_by_col(markup_diff.get_added(), 0)

    diff_by_object_id = dict()
    with open(texts_pool_path, "r") as texts_pool:
        for line in texts_pool:
            parts = line.strip().split('\t')
            document_id, document_text = parts[0], ' '.join(parts[1:]).decode('utf-8')

            if document_id in lost_hypos_by_doc:
                fill_document_diff_list(lost_hypos_by_doc[document_id], document_id, document_text, 'LOST', diff_by_object_id)

            if document_id in added_hypos_by_doc:
                fill_document_diff_list(added_hypos_by_doc[document_id], document_id, document_text, 'ADDED', diff_by_object_id)

    diff_list = [item for sublist in sorted(diff_by_object_id.values(), key=lambda k: len(k), reverse=True) for item in sublist]

    with open(file_name, 'w') as output_file:
        for record in diff_list:
            output_file.write('\t'.join(record) + '\n')


GROUP_BASE = 'Base data'
GROUP_TEST = 'Test data'
GROUP_MR_CORPUS = 'MapReduce corpus'


class YaneTestLight(yane.YaneTaskBase):
    """
        Calculate hypos diff of entity extraction
    """
    type = 'YANE_EXTRACTION_DIFF'

    execution_space = 30 * 1024
    client_tags = ctc.Tag.LINUX_PRECISE

    class Config(LastReleasedResource):
        name = 'config'
        description = 'Config'
        resource_type = resource_types.YANE_CONFIG
        group = yane.GROUP_IN

    class ObjectExtractorData(LastReleasedResource):
        name = 'data'
        description = 'Yane data (leave blank to get from SVN)'
        group = GROUP_BASE
        resource_type = resource_types.YANE_DATA
        required = False
        do_not_copy = True

    class YaneToolsTested(LastReleasedResource):
        name = 'tools' + TESTING_SUFFIX
        description = 'Yane tools for testing (leave blank to use from base)'
        group = GROUP_TEST
        resource_type = resource_types.YANE_TOOLS
        required = False
        do_not_copy = True

    class ObjectExtractorDataTested(LastReleasedResource):
        name = 'data' + TESTING_SUFFIX
        description = 'Yane data for testing'
        group = GROUP_TEST
        resource_type = resource_types.YANE_DATA
        do_not_copy = True

    class UseMRCorpus(SandboxBoolParameter):
        name = 'use_mr_corpus'
        description = 'Test with MapReduce corpus'
        group = GROUP_MR_CORPUS
        default_value = False
        sub_fields = {'true': ['mr_runtime', 'mr_server', 'mr_user',
                               'mr_corpus_table', 'mr_object_diff_table', 'mr_doc_diff_table']}

    class MRCorpusTable(SandboxStringParameter):
        name = 'mr_corpus_table'
        group = GROUP_MR_CORPUS
        description = 'MR corpus table for testing'
        default_value = 'home/dict/yane/external.data/corpus/short'
        required = True

    class MRObjectDiffTable(SandboxStringParameter):
        name = 'mr_object_diff_table'
        group = GROUP_MR_CORPUS
        description = 'MR table for output object diff (optional)'
        required = False

    class MRDocDiffTable(SandboxStringParameter):
        name = 'mr_doc_diff_table'
        group = GROUP_MR_CORPUS
        description = 'MR table for output document diff (optional)'
        required = False

    input_parameters = yane.get_base_params(GROUP_BASE).params + \
        [ObjectExtractorData, YaneToolsTested, ObjectExtractorDataTested, Config] + \
        yane.get_text_params('Markup').params + \
        [UseMRCorpus] + \
        yane.get_mr_params(GROUP_MR_CORPUS).params + \
        [MRCorpusTable, MRObjectDiffTable, MRDocDiffTable]

    def __init__(self, task_id=0):
        yane.YaneTaskBase.__init__(self, task_id)
        self.ctx['kill_timeout'] = 5 * 60 * 60
        self.local_ctx = {}

    def check_resources(self):
        if not self.is_resource_selected('tools') or not self.is_resource_selected('tools' + TESTING_SUFFIX):
            return

        tools_resource_stable = channel.sandbox.get_resource(self.ctx['tools'])
        tools_resource_tested = channel.sandbox.get_resource(self.ctx['tools' + TESTING_SUFFIX])

        if tools_resource_stable.arch != tools_resource_tested.arch:
            raise SandboxTaskFailureError('Difference in architectures of stable and tested tools')

        if 'arch' in self.client_info and tools_resource_stable.arch != self.client_info['arch']:
            raise SandboxTaskFailureError('Difference in current and tools architectures')

    @property
    def footer(self):
        if self.is_finished():
            return self.ctx['result_html']
        else:
            return {}

    def get_data_path(self, param_suffix):
        param = 'data' + param_suffix
        if param not in self.local_ctx:
            if self.is_resource_selected(param):
                self.local_ctx[param] = self.sync_resource(self.ctx[param])
            else:
                yane_config = self.get_config('config')
                svn_path = DEFAULT_SVN_DATA_PATH if 'svn_data_path' not in yane_config else yane_config['svn_data_path']
                data_dir = make_folder(self.abs_path(param))
                Arcadia.checkout(self.get_svn_path(svn_path), path=data_dir, depth='files')
                self.local_ctx[param] = data_dir
        return self.local_ctx[param]

    def create_hypos_file(self, texts_pool_path, param_suffix, langs):
        data_path = self.get_data_path(param_suffix)
        hypos_filename = 'hypos_list' + param_suffix
        extractor_cmd = [self.get_tool('objectsextractor', 'tools' + param_suffix),
                         '-d', data_path,
                         '-l', ','.join(langs)]
        logging.debug("extractor_cmd: %s" % extractor_cmd)

        with open(hypos_filename, 'w') as output_file:
            with open(texts_pool_path, 'r') as texts:
                run_process(
                    extractor_cmd,
                    log_prefix='objectsextractor',
                    wait=True,
                    stdin=texts,
                    stdout=output_file,
                    outputs_to_one_file=False
                )

        return hypos_filename

    def create_hypos_stat_mr_table(self, output_mr_table, param_suffix, langs):
        self.run_tool(
            'mrobjectsextractor',
            [
                '-s', self.ctx['mr_server'],
                '-i', self.ctx['mr_corpus_table'],
                '-o', output_mr_table,
                '-d', self.get_data_path(param_suffix),
                '-l', ','.join(langs),
                '-G',  # hypos only
                '--temp-dir', self.abs_path('tmp'),
            ],
            env=self.get_mr_env(), wait=True, tools_param='tools' + param_suffix
        )

    def compute_mr_hypos_stats_diff(self, first_stats_table, second_stats_table):
        TOP_DIFF_FILE_PATH = 'hypos_diff.txt'

        cmd = [
            self.get_tool('mrhyposdiff', 'tools' + TESTING_SUFFIX),
            '-s', self.ctx['mr_server'],
            '-t', repr(TOP_DIFF_OBJECT_COUNT),
            first_stats_table,
            second_stats_table
        ]
        if 'mr_object_diff_table' in self.ctx and self.ctx['mr_object_diff_table'] != '':
            cmd += ['-h', self.ctx['mr_object_diff_table']]
        if 'mr_doc_diff_table' in self.ctx and self.ctx['mr_doc_diff_table'] != '':
            cmd += ['-d', self.ctx['mr_doc_diff_table']]

        with open(TOP_DIFF_FILE_PATH, 'w') as diff_file:
            run_process(cmd, log_prefix='mrhyposdiff', stdout=diff_file, outputs_to_one_file=False, wait=True, environment=self.get_mr_env())

        hypos_diff_top = []
        docs_diff_top = []

        cur_diff_list_pointer = hypos_diff_top
        with open(TOP_DIFF_FILE_PATH, 'r') as diff_file:
            for line in diff_file:
                if line.strip() == '':
                    cur_diff_list_pointer = docs_diff_top
                    continue

                obj_id, loss_count, added_count = line.strip().split('\t')
                cur_diff_list_pointer.append({'id': obj_id, 'loss': loss_count, 'added': added_count})

        return hypos_diff_top, docs_diff_top

    def compute_stats(self, texts_pool_path, markup, param_suffix, langs):
        hypos_filename = self.create_hypos_file(texts_pool_path, param_suffix, langs)

        stats = HyposDistribution()

        with open(hypos_filename, "r") as hypos_file:
            for line in hypos_file:
                try:
                    documentId, objectId, beginPosition, size = line.strip().split('\t')
                except:
                    self._create_resource("Extraction result",
                                          hypos_filename,
                                          resource_types.OTHER_RESOURCE,
                                          arch='any')

                    raise SandboxTaskFailureError('Bad extraction result: %s' % line.strip())

                markup_key = (documentId, objectId, beginPosition, size)
                if markup_key not in markup:
                    stats.uncovered_hypos.append(markup_key)
                else:
                    if markup[markup_key]:
                        stats.winner_hypos.append(markup_key)
                    else:
                        stats.loser_hypos.append(markup_key)

            remove_path(hypos_filename)

        stats.winner_hypos.sort()
        stats.loser_hypos.sort()
        stats.uncovered_hypos.sort()

        return stats

    def do_execute(self):
        # Use base version of tools if it is not specified explicitly for testing
        if not self.is_resource_selected('tools' + TESTING_SUFFIX):
            self.ctx['tools' + TESTING_SUFFIX] = self.ctx.get('tools')

        texts_pool_path = self.sync_resource(self.ctx['texts'])
        markup_path = self.sync_resource(self.ctx['markup'])
        markup = read_markup(markup_path)

        yane_config = self.get_config('config')
        langs = DEFAULT_LANGS if 'extraction_langs' not in yane_config else yane_config['extraction_langs']

        stable_stats = self.compute_stats(texts_pool_path, markup, '', langs)
        tested_stats = self.compute_stats(texts_pool_path, markup, TESTING_SUFFIX, langs)

        markup_diff = compute_hypos_diff(stable_stats, tested_stats)

        logging.debug("Freq total loss: %f" % markup_diff.freq_total_lost)
        logging.debug("Freq total addded: %f" % markup_diff.freq_total_added)

        logging.debug("Freq winner loss: %f" % markup_diff.freq_winner_lost)
        logging.debug("Freq winner addded: %f" % markup_diff.freq_winner_added)

        loss_hypos_texts = extract_most_freq_texts(markup_diff.winner_hypos_loss, texts_pool_path)
        added_hypos_texts = extract_most_freq_texts(markup_diff.winner_hypos_added, texts_pool_path)

        mr_hypos_diff_top = []
        mr_docs_diff_top = []

        if self.ctx.get('use_mr_corpus', False):
            stable_stats_table = 'tmp/yane_stable_stats_' + repr(self.id)
            tested_stats_table = 'tmp/yane_tested_stats_' + repr(self.id)
            self.create_hypos_stat_mr_table(stable_stats_table, '', langs)
            self.create_hypos_stat_mr_table(tested_stats_table, TESTING_SUFFIX, langs)

            mr_hypos_diff_top, mr_docs_diff_top = self.compute_mr_hypos_stats_diff(stable_stats_table, tested_stats_table)
            self.run_tool('mr_rm',
                          ['-s', self.ctx['mr_server'], '-v', stable_stats_table, tested_stats_table],
                          self.get_mr_env())

        if markup_diff.has_diff():
            full_diff_resource = self.create_full_diff_resource('Full hypos extraction diff',
                                                                markup_diff,
                                                                texts_pool_path,
                                                                FULL_DIFF_FILE_NAME)
            self.ctx['full_diff_resource_id'] = full_diff_resource.id

        if len(markup_diff.winner_hypos_loss) > 0:
            lost_hypos_resource = self.create_hypos_list_resource('Lost winner hypos', markup_diff.loss_winner_hypos_counters, LOST_HYPOS_FILE_NAME, loss_hypos_texts)
            self.ctx['lost_diff_resource_id'] = lost_hypos_resource.id

        if len(markup_diff.winner_hypos_added) > 0:
            added_hypos_resource = self.create_hypos_list_resource('Added winner hypos', markup_diff.added_winner_hypos_counters, ADDED_HYPOS_FILE_NAME, added_hypos_texts)
            self.ctx['added_diff_resource_id'] = added_hypos_resource.id

        self.ctx['result_html'] = self.make_result_html(markup_diff, mr_hypos_diff_top, mr_docs_diff_top, loss_hypos_texts, added_hypos_texts)

    def create_hypos_list_resource(self, description, records, file_name, hypos_texts):
        write_hypos_to_file(records, hypos_texts, file_name)

        return self._create_resource(description,
                                     file_name,
                                     resource_types.OTHER_RESOURCE,
                                     arch='any')

    def create_full_diff_resource(self, description, markup_diff, texts_pool_path, file_name):
        if not markup_diff.has_diff():
            raise SandboxTaskFailureError('Attempt to create resource with empty diff. Description: %s' % description)

        create_full_diff_file(markup_diff, texts_pool_path, file_name)

        return self._create_resource(description,
                                     file_name,
                                     resource_types.OTHER_RESOURCE,
                                     arch='any')

    def make_result_html(self, markup_diff, mr_hypos_diff_top, mr_docs_diff_top, loss_hypos_texts, added_hypos_texts):
        LOSS_COLOR = "#FFC5CE"
        ADDED_COLOR = "#C5FFC4"

        def make_hypos_row(freq, sign):
            freq_text = "%.2f" % (freq * 100)

            return """<div><b>{}{}%</b> of winner hypos.
                   </div>""".format(sign, freq_text)

        def make_mr_diff_html(top, title):
            chunk = "<h4>" + title + "</h4><ul>"
            for item in top:
                chunk += "<li> {} (<b>-{}</b> hypos, <b>+{}</b> hypos)</li>".format(*item)
            chunk += "</ul>"
            return chunk

        def make_top_diff(top, sign, full_diff_resource_id, hypos_texts):
            if len(top) == 0:
                return "<div>No diff in winner hypos</div>"

            html = "<div>Top:</div>"
            for item in top:
                html += """<div style="margin-left:15px; margin-top:3px;">
                         <b>{}{}</b> <i>{} ({})</i>
                         </div>""".format(sign, item['count'], item['id'], hypos_texts[item['id']].encode(HTML_REPORT_CHARSET))

            html += make_resource_url(full_diff_resource_id, 'All winner hypos')
            return html

        def make_table(body):
            return (
                "<h4>Diff in markup corpus </h4><table border='0'><tbody>" +
                body +
                "</tbody></table>"
            )

        def make_resource_url(resource_id, text):
            return """<div style="margin-left:15px; margin-top:3px; margin-bottom:5px;">
                       <a href="https://proxy.sandbox.yandex-team.ru/{}">{}</a>
                       </div>""".format(resource_id, text)

        def make_diff(freq, hypos_top, full_diff_resource_id, hypos_texts, is_loss):
            color = LOSS_COLOR if is_loss else ADDED_COLOR
            sign = '-' if is_loss else '+'

            html = """<tr><td style="width:100%; background-color:{};
                   padding:10px;">""".format(color)
            html += make_hypos_row(freq, sign)
            html += make_top_diff(hypos_top, sign, full_diff_resource_id, hypos_texts)

            return html

        if not markup_diff.has_diff():
            return make_table("<div><b>No diff</b></div>")

        html = ""
        if len(markup_diff.winner_hypos_loss) > 0:
            html += make_diff(markup_diff.freq_winner_lost,
                              markup_diff.loss_winner_hypos_counters[:TOP_DIFF_OBJECT_COUNT],
                              self.ctx['lost_diff_resource_id'],
                              loss_hypos_texts,
                              True)
        if len(markup_diff.winner_hypos_added) > 0:
            html += make_diff(markup_diff.freq_winner_added,
                              markup_diff.added_winner_hypos_counters[:TOP_DIFF_OBJECT_COUNT],
                              self.ctx['added_diff_resource_id'],
                              added_hypos_texts,
                              False)

        full_diff_record = 'Full diff (<b>-%.2f%%</b>, <b>+%.2f%%</b> of all hypos) ' % (markup_diff.freq_total_lost * 100, markup_diff.freq_total_added * 100)
        html += """<tr><td>""" + \
                make_resource_url(self.ctx['full_diff_resource_id'], full_diff_record) + \
                """</td></tr>"""

        if len(mr_hypos_diff_top):
            html += make_mr_diff_html(mr_hypos_diff_top, "Top extration objects diff in MR-corpus:")
            html += make_mr_diff_html(mr_docs_diff_top, "Top documents diff in MR-corpus:")

        return make_table(html)

    def on_enqueue(self):
        yane.YaneTaskBase.on_enqueue(self)
        yane.validate_resource(self.ctx.get('tools' + TESTING_SUFFIX), 'Yane tools for testing', False,
                                       resource_types.YANE_TOOLS, self.arch)
        yane.validate_resource(self.ctx.get('data'), 'Yane data', False,
                                       resource_types.YANE_DATA)
        yane.validate_resource(self.ctx.get('data' + TESTING_SUFFIX), 'Yane data for testing', True,
                                       resource_types.YANE_DATA)

    # override YaneTaskBase._on_first_run
    # will be called from YaneTaskBase.on_execute()
    def _on_first_run(self):
        yane.YaneTaskBase._on_first_run(self)
        self.check_resources()


__Task__ = YaneTestLight
