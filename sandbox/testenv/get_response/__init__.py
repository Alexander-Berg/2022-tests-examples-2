from sandbox.projects.ydo.testenv import (
    YdoSearchproxyTestPortalResponses,
    YdoSearchproxyTestWizardResponses,
    save_json_data,
)

import sandbox.sdk2 as sdk2
from sandbox.common.errors import TaskFailure
from sandbox.sandboxsdk.environments import PipEnvironment

from datetime import datetime

import copy
import hashlib
import json
import logging
import requests
import time
import urllib
import urlparse


SOY_API_URL = 'http://soyproxy.yandex.net/hahn/soy_api'


def send_request(func, url, headers, data=None):
    flag = False
    for t in range(10, 50, 10):
        try:
            if data:
                response = func(url, headers=headers, data=data)
            else:
                response = func(url, headers=headers)
            flag = True
        except requests.exceptions.ConnectionError as err:
            error = err
            logging.info('Error: {}! We will sleep {} second'.format(err, t))
            time.sleep(t)
            continue
    if flag:
        return response
    raise error


def xpath_get(val, path, default=None):
    current_subtree = val
    try:
        for x in path.strip("/").split("/"):
            if isinstance(current_subtree, dict):
                current_subtree = current_subtree.get(x)
            elif isinstance(current_subtree, list):
                current_subtree = current_subtree[int(x)]
            else:
                return default
    except:
        return default

    return current_subtree


def delete_webreqid(struct):
    if isinstance(struct, dict):
        for key, value in struct.items():
            if isinstance(value, str) or isinstance(value, unicode):
                if 'webreqid' in value:
                    struct.pop(key)
            else:
                delete_webreqid(value)
    elif isinstance(struct, list):
        for value in struct:
            delete_webreqid(value)


def from_kv_struct_to_dict(struct, json_set={}, black_set={}):
    if not isinstance(struct, list):
        return struct
    ans = dict()
    for attr in struct:
        key = attr['Key']
        value = attr['Value']
        if key in black_set:
            continue
        if key in json_set:
            value = json.loads(value)
        if key not in ans:
            ans[key] = value
        else:
            if not isinstance(ans[key], list):
                ans[key] = [ans[key]]
            ans[key].append(value)
            ans[key].sort()
    return ans


def convert(struct, kv, black_set, path=''):
    if isinstance(struct, dict):
        for key, value in struct.items():
            item_path = '/'.join((path, key)).lstrip('/')
            if item_path in black_set:
                struct.pop(key)
                continue
            if item_path in kv.keys():
                struct[key] = from_kv_struct_to_dict(
                    value,
                    frozenset(kv[item_path].get("json_list", [])),
                    frozenset(kv[item_path].get("black_list", []))
                )
            convert(value, kv, black_set, item_path)
    if isinstance(struct, list):
        for idx, value in enumerate(struct):
            item_path = '/'.join((path, str(idx))).lstrip('/')
            convert(value, kv, black_set, item_path)


class YdoSearchproxyGetResponses(sdk2.Task):
    class Requirements(sdk2.Task.Requirements):
        environments = [
            PipEnvironment('yandex-yt')
        ]

    class Parameters(sdk2.Parameters):
        fail_on_any_error = True
        revision = sdk2.parameters.Integer('revision', default_value=0)
        url_prefix = sdk2.parameters.String('beta hostname', default_value='hamster')
        checkout_arcadia_from_url = sdk2.parameters.String(
            'Svn url for arcadia:',
            default_value='arcadia:/arc/trunk/arcadia/'
        )
        config_dir = sdk2.parameters.String(
            'config dir',
            default_value='ydo/tools/searchproxy/get_responses'
        )
        config_name = sdk2.parameters.String(
            'config name',
            default_value='config.json'
        )
        wizard_pool_filename = sdk2.parameters.String(
            'wizard pool filename',
            default_value='wizard_pool.txt'
        )
        portal_pool_filename = sdk2.parameters.String(
            'portal pool filename',
            default_value='portal_pool.txt'
        )
        temp_dir = sdk2.parameters.String(
            'directory for temporary tables (use for interactions with SOY)',
            default_value='//home/ydo/tmp'
        )
        wizard_flag = sdk2.parameters.Bool('count wizard', default_value=True)
        portal_flag = sdk2.parameters.Bool('count portal', default_value=True)
        wizard_cgi = sdk2.parameters.String('add cgi wizard')
        portal_cgi = sdk2.parameters.String('add cgi portal')
        pool = sdk2.parameters.String(
            'pool',
            default_value='ydo'
        )
        with sdk2.parameters.Output:
            batch_id = sdk2.parameters.String('soy id', default_value='')

    def on_break(self, prev_status, status):
        self._finish('on_break')

    def on_failure(self, prev_status):
        self._finish('on_failure')

    def on_timeout(self, prev_status):
        self._finish('on_timeout')
        raise TaskFailure("timeout")

    def _finish(self, stage):
        logging.info('{stage} abort soy'.format(stage=stage))
        logging.info('batch_id = {}'.format(self.Context.batch_id))
        headers = {
            "Authorization": "OAuth {}".format(sdk2.Vault.data('YDO', 'soy-token'))
        }
        if self.Context.batch_id:
            response = send_request(
                requests.delete,
                "{url}/abort?id={id}".format(url=SOY_API_URL, id=self.Context.batch_id),
                headers
            ).json()
            logging.info('{stage} abort soy response = {response}'.format(stage=stage, response=response))

    def on_execute(self):
        config, wizard_queries, portal_queries = self._read_configs()
        batch = self._create_batch(wizard_queries, portal_queries, config)
        if not len(batch):
            return
        responses = self._scrap_batch(batch)
        wizard, portal = self._process_responses(responses, config)

        if self.Parameters.wizard_flag:
            save_json_data(self, YdoSearchproxyTestWizardResponses, wizard, 'wizard', 'wizard.json')

        if self.Parameters.portal_flag:
            save_json_data(self, YdoSearchproxyTestPortalResponses, portal, 'portal', 'portal.json')

        self.Parameters.batch_id = self.Context.batch_id

    def _read_configs(self):
        url = '/'.join((self.Parameters.checkout_arcadia_from_url, self.Parameters.config_dir))
        config_path = sdk2.svn.Arcadia.checkout(url, 'config', depth='files', revision=self.Parameters.revision)
        logging.info('checkout configs from revision = {}'.format(self.Parameters.revision))

        with open('/'.join((config_path, self.Parameters.config_name)), 'r') as file:
            config = json.load(file)
        logging.info('config:\n{}'.format(config))

        wizard_queries = []
        portal_queries = []

        if self.Parameters.wizard_flag:
            with open('/'.join((config_path, self.Parameters.wizard_pool_filename)), 'r') as file:
                wizard_queries = [urlparse.parse_qsl(query.rstrip('\n')) for query in file]
            logging.debug('wizard_queries:\n{}'.format(json.dumps(wizard_queries, ensure_ascii=False)))

        if self.Parameters.portal_flag:
            with open('/'.join((config_path, self.Parameters.portal_pool_filename)), 'r') as file:
                portal_queries = [urlparse.urlsplit(query.rstrip('\n')) for query in file]
            logging.debug('portal_queries:\n{}'.format(json.dumps(portal_queries, ensure_ascii=False)))

        return config, wizard_queries, portal_queries

    def _create_batch(self, wizard_queries, portal_queries, config):
        batch = list()
        row_template = {
            'method': 'GET',
            'cookies': [],
            'headers': []
        }

        if self.Parameters.wizard_flag:
            flags_cgi = urlparse.parse_qsl(config['wizard_serp'].get('cgi', '')) \
                            + urlparse.parse_qsl(config.get('cgi', '')) \
                            + urlparse.parse_qsl(self.Parameters.wizard_cgi)
            logging.info('flags_wizard_cgi = {}'.format(flags_cgi))
            for query in wizard_queries:
                row = copy.copy(row_template)

                url_parts = urlparse.ParseResult(scheme='https',
                                                 netloc='{}.yandex.ru'.format(self.Parameters.url_prefix),
                                                 path='yandsearch',
                                                 params='',
                                                 query=urllib.urlencode(query + flags_cgi),
                                                 fragment='')

                url = urlparse.urlunparse(url_parts)
                row['uri'] = url

                md5 = hashlib.md5()
                md5.update(url)
                qid = 'wizard_' + md5.hexdigest()
                row['id'] = qid

                batch.append(row)

        if self.Parameters.portal_flag:
            flags_cgi = urlparse.parse_qsl(config['portal_serp'].get('cgi', '')) \
                            + urlparse.parse_qsl(config.get('cgi', '')) \
                            + urlparse.parse_qsl(self.Parameters.portal_cgi)
            logging.info('flags_portal_cgi = {}'.format(flags_cgi))
            for query_parts in portal_queries:
                row = copy.copy(row_template)

                url_parts = urlparse.ParseResult(scheme='https',
                                                 netloc='{}.yandex.ru'.format(self.Parameters.url_prefix),
                                                 path='{}/{}'.format('uslugi', query_parts.path),
                                                 params='',
                                                 query=urllib.urlencode(urlparse.parse_qsl(query_parts.query) + flags_cgi),
                                                 fragment='')

                url = urlparse.urlunparse(url_parts)
                row['uri'] = url

                md5 = hashlib.md5()
                md5.update(url)
                qid = 'portal_' + md5.hexdigest()
                row['id'] = qid

                batch.append(row)

        logging.info('batch_size = {}'.format(len(batch)))
        logging.debug('batch = {}'.format(batch))
        return batch

    def _scrap_batch(self, batch):
        import yt.wrapper as yt
        yt.config["proxy"]["url"] = "hahn"
        yt.config["token"] = sdk2.Vault.data('YDO', 'yt-token')
        with yt.TempTable(self.Parameters.temp_dir, "searchproxy_scrapper_") as table:
            # write table
            yt.write_table(table, batch, format='<encode_utf8=false>json')
            logging.info("save {} to request table {}".format(len(batch), table))
            self.Context.batch_id = datetime.now().isoformat().replace(':', '-')
            headers = {
                "Authorization": "OAuth {}".format(sdk2.Vault.data('YDO', 'soy-token'))
            }
            self.Context.save()
            # request to SOY
            data = {
                "input_table": str(table),
                "pool": self.Parameters.pool,
                "id": self.Context.batch_id,
                "max_retries_per_row": 5,
                "fetch_timeout": 10000,
                "execution_timeout": "1h",
                "queue_timeout": "2h",
                "map_operation_type": "http"
            }
            logging.info('request data = {}'.format(data))
            response = send_request(
                requests.post,
                '{}/create'.format(SOY_API_URL),
                headers,
                json.dumps(data),
            )
            logging.info("response = {}".format(response))
            response = response.json()
            logging.info("status = {}".format(response['status']))
            if response['status'] != 'ok':
                raise TaskFailure(str(response))

            # wait SOY
            tm = - time.time()
            while True:
                response = send_request(
                    requests.get,
                    "{url}/status?id={id}".format(url=SOY_API_URL, id=self.Context.batch_id),
                    headers
                )
                if response:
                    response = response.json()
                    status = response.get("operation_status")
                    logging.info("status = {}".format(status))
                    if status in {'completed', 'failed', 'aborted', 'timeout', 'rejected'}:
                        break
                time.sleep(10)

            logging.info("response = {}".format(response))
            if response["operation_status"] != 'completed':
                raise TaskFailure('SOY operation failed')
            tm += time.time()
            logging.info('waiting time {}'.format(tm))
        # read responses
        output_table = response['output_path']
        table = yt.read_table(yt.TablePath(output_table, columns=[
            "Url",
            "id",
            "FetchedResult"
        ]), format='<encode_utf8=true>json')
        try:
            def get_query(url):
                url_parts = urlparse.urlsplit(url)
                return '{}?{}'.format(url_parts.path, url_parts.query)

            beta_responses = {row['id']: {'url': row['Url'], 'query': get_query(row['Url']), 'content': json.loads(row["FetchedResult"])} for row in table}
            logging.debug('random_beta_responses = {}'.format(beta_responses.itervalues().next()))
        except:
            raise TaskFailure("we can't read beta response as a json file")
        return beta_responses

    def _process_responses(self, responses, config):
        wizard_ans = []
        if self.Parameters.wizard_flag:
            wizard_responses = filter(lambda (key, _): key.startswith('wizard'), responses.iteritems())
            for id, response in wizard_responses:
                extracted_content = xpath_get(response['content'], config['wizard_serp']['path'], '')

                arrange, gta = self._process_gta(extracted_content, config['wizard_serp']['gta'])

                wizard_ans.append(
                    {
                        'arrange': arrange,
                        'gta': gta,
                        'query': response['query'],
                        'search_props': self._process_search_props(
                            extracted_content,
                            config['wizard_serp']['search_props']
                        ),
                        'url': response['url']
                    }
                )

        portal_ans = []
        if self.Parameters.portal_flag:
            portal_responses = filter(lambda (key, _): key.startswith('portal'), responses.iteritems())
            for id, response in portal_responses:
                extracted_content = xpath_get(response['content'], config['portal_serp']['path'], {})

                arrange, docs = self._process_docs(
                    extracted_content,
                    config['portal_serp']['docs']
                )

                portal_ans.append(
                    {
                        'arrange': arrange,
                        'docs': docs,
                        'query': response['query'],
                        'search_props': self._process_search_props(
                            extracted_content,
                            config['portal_serp']['search_props']
                        ),
                        'url': response['url']
                    }
                )

        return wizard_ans, portal_ans

    def _process_search_props(self, response, config):
        response = xpath_get(response, config['path'])
        if response is None:
            return dict()
        response = from_kv_struct_to_dict(response, frozenset(config.get('json_list', [])), frozenset(config.get('black_list', [])))
        convert(response, dict(), frozenset(config.get('black_list', [])))
        delete_webreqid(response)
        return response

    def _process_gta(self, response, config):
        gta = xpath_get(response, config['path'])
        if gta is None:
            return [], dict()
        gta_ans = from_kv_struct_to_dict(gta, frozenset(config.get('json_list', [])))
        convert(gta_ans, dict(), frozenset(config.get('black_list', [])))
        delete_webreqid(gta_ans)
        serpData = gta_ans['_SerpData']
        arrange = []
        if serpData['peoples'] is None:
            serpData['peoples'] = []
        for idx, worker in enumerate(serpData['peoples']):
            arrange.append(worker['worker_id'])
            worker['pos'] = idx
        return arrange, gta_ans

    def _process_docs(self, response, config):
        black_set = frozenset(config.get('black_list', []))
        kv = config['kv']
        docs = xpath_get(response, config['path'])
        if docs is None:
            return [], []
        arrange = []
        for idx, doc in enumerate(docs):
            arrange.append(xpath_get(doc, 'Document/0/ArchiveInfo/Url', ''))
            convert(doc, kv, black_set)
            doc['pos'] = idx
        return arrange, docs
