# -*- oding: utf-8 -*-

import copy
import logging
import os
import yt.wrapper as yt
import subprocess as sub
import shutil

from os.path import join as pj


WEBMASTER_HOSTS_PATH = '//home/webmaster/prod/export/webmaster-hosts'
PREPARAT_SHARDS_COUNT = 18
SAMOVAR_PREPARAT_SHARDS_COUNT = 128

MB = 1024 * 1024
MAX_ROW_WEIGHT = 64 * MB
YT_LIST_RESPONSE_LIMIT = 15000


def get_client(proxy):
    return yt.client.YtClient(proxy=proxy, token=yt.http_helpers.get_token())


class TestPreparer:

    def __init__(self, default_proxy=None):
        self.default_proxy = default_proxy

    @staticmethod
    def no_sample():
        pass

    def recursive_set(self, path, value):
        node_path, attr_path = path.split('@', 1)
        node_path = node_path.rstrip('/')
        client = get_client(self.default_proxy)
        client.create(
            'map_node',
            node_path,
            recursive=True,
            ignore_existing=True,
        )
        current_attribute_path_parts = []
        for path_element in attr_path.split('/')[:-1]:
            current_attribute_path_parts.append(path_element)
            meta_sub_path = '/'.join(current_attribute_path_parts)
            full_path = pj(node_path, '@' + meta_sub_path)
            if not client.exists(full_path):
                client.set(full_path, {})

        client.set(path, value)

    def lemur_preparat_sample(self, delivery, server, directory, yt_output_dir):
        if delivery not in ['JupiterLemurPreparat']:
            raise Exception('Unknown lemur preparat delivery: %s', delivery)

        # this sampling function is used for JupiterLemurPreparat
        client = get_client(server)
        last_state = max(client.list(directory))
        for shard_number in range(0, PREPARAT_SHARDS_COUNT):
            shard = 'inlinks_{:0>4}'.format(shard_number)
            path = pj(directory, last_state, last_state, shard)
            # Here we want intersection with WebMasterHosts table (otherwise delivery fail).
            # Also we need large enough sample for fakes to be present there
            self.create_sample(delivery, server, path, yt_output_dir, end_index=10000)

    def samovar_preparat_sample(self, delivery, server, directory, yt_output_dir):
        if delivery != 'JupiterSamovarPreparatRaw':
            raise Exception('Unknown samovar preparat delivery: %s', delivery)

        def add_possible_fakes(table_data):
            result = []
            host = None
            for row in table_data:
                if host != row["Host"]:
                    host = row["Host"]
                    if row["Path"] != "/":
                        new_row = copy.deepcopy(row)
                        new_row["Path"] = "/"
                        result.append(new_row)
                result.append(row)

            return result

        def find_preparat(table_data):
            count = 0
            for row in table_data:
                if len(row["LemurPreparat"]) > 0:
                    count += 1
                if count >= 8:
                    return True
            return False

        shards = ['{:0>3}'.format(shard_number) for shard_number in range(0, SAMOVAR_PREPARAT_SHARDS_COUNT)]

        client = get_client(server)
        output_client = get_client(self.default_proxy)
        for shard in shards:
            path = pj(directory, shard, 'preparat')

            sampled = False
            sample_size = 5000
            start_index = 0
            while not sampled:
                logging.info("Sampling samovar preparat {} with offset {}".format(shard, start_index))
                sampled = self.create_sample(
                    delivery,
                    server,
                    path,
                    yt_output_dir,
                    start_index=start_index,
                    end_index=start_index + sample_size,
                    table_data_patcher=add_possible_fakes,
                    table_data_checker=find_preparat
                )
                start_index += sample_size

            state_path = pj(directory, shard, 'start_time')
            state_ts = client.get(state_path)  # get from original tables
            output_client.set(pj(yt_output_dir, state_path[2:]), state_ts)  # set to sample

    def video_index_ann_sample(self, delivery, server, directory, yt_output_dir):
        self.create_sample(delivery, server, directory, yt_output_dir, start_index=0, end_index=10000)

    def middle_table_sample(self, delivery, server, directory, yt_output_dir, sample_size=10, start_index_fraction=2):
        client = get_client(server)
        table_path = directory

        start_index = client.row_count(table_path)/start_index_fraction
        logging.info('Sample start row index is %s', start_index)
        end_index = start_index + sample_size

        self.create_sample(delivery, server, table_path, yt_output_dir, start_index=start_index, end_index=end_index)

    def lemur_dir_factors_sample(self, delivery, server, directory, yt_output_dir):
        self.middle_table_sample(delivery, server, directory, yt_output_dir, sample_size=100)

    def antispam_export_sample(self, delivery, server, directory, yt_output_dir):
        self.middle_table_sample(delivery, server, directory, yt_output_dir, sample_size=200)

    def host_mirror_sample(self, delivery, server, directory, yt_output_dir):  # noqa
        min_groups = 2
        client = get_client(server)
        state = client.get(pj(directory, '@for_production'))
        table_path = pj(directory, state, 'prod.res.index')

        groups_left = min_groups
        sample_size = 0
        cur_main = ''
        data = []
        output_client = get_client(self.default_proxy)
        while True:
            row = output_client.TablePath(table_path, start_index=sample_size, end_index=sample_size + 1)
            cur = list(client.read_table(row, format=yt.format.YsonFormat()))[0]
            if cur_main == '':
                cur_main = cur['Main']
            elif cur_main != cur['Main']:
                if groups_left > 0:
                    groups_left -= 1
                if groups_left == 0 and sample_size >= 10:
                    break
                cur_main = cur['Main']

            data.append(cur)
            sample_size += 1

        output_directory = pj(yt_output_dir, directory[2:])
        output_client.set(pj(output_directory, '@for_production'), state)
        output_path = pj(output_directory, state, 'prod.res')
        if not output_client.exists(output_path):
            output_client.create('table', output_path, recursive=True)
        output_client.write_table(output_path, data, format=yt.format.YsonFormat())
        output_client.run_sort(output_path, sort_by=['Host'])
        logging.info('%s sample created. Output path=%s', delivery, output_path)
        logging.info('%s OK', delivery)

    def enrich_webmaster_hosts_by_lemur_preparat(self, yt_output_dir, lemur_suffix):
        client = get_client(self.default_proxy)
        lemur_path = pj(yt_output_dir, lemur_suffix[2:])
        extra_hosts = set()
        last_state = sorted(client.list(lemur_path))[-1]
        for table_path in client.list(pj(lemur_path, last_state, last_state)):
            for row in client.read_table(pj(lemur_path, last_state, last_state, table_path)):
                extra_hosts.add(row.get('Host'))
        if not client.exists(WEBMASTER_HOSTS_PATH):
            raise Exception('Could not find ' + WEBMASTER_HOSTS_PATH)
        extra_hosts = [{'key': host} for host in extra_hosts]
        logging.info('Enriching WebMasterHosts delivery with %d hosts', len(extra_hosts))
        client.write_table(client.TablePath(pj(yt_output_dir, WEBMASTER_HOSTS_PATH[2:]), append=True), extra_hosts)

    def enrich_webmaster_hosts_by_samovar_preparat(self, yt_output_dir, samovar_suffix):
        client = get_client(self.default_proxy)
        shards = ['{:0>3}'.format(shard_number) for shard_number in range(0, SAMOVAR_PREPARAT_SHARDS_COUNT)]
        extra_hosts = set()

        for shard in shards:
            path = pj(yt_output_dir, samovar_suffix[2:], shard, 'preparat')
            for row in client.read_table(path):
                extra_hosts.add(row.get('Host'))
        if not client.exists(WEBMASTER_HOSTS_PATH):
            raise Exception('Could not find ' + WEBMASTER_HOSTS_PATH)
        extra_hosts = [{'key': host} for host in extra_hosts]
        logging.info('Enriching WebMasterHosts delivery with %d hosts', len(extra_hosts))
        client.write_table(client.TablePath(pj(yt_output_dir, WEBMASTER_HOSTS_PATH[2:]), append=True), extra_hosts)

    def create_sample(
            self,
            delivery,
            server,
            input_table_path,
            yt_output_dir,
            start_index=0,
            end_index=10,
            output_table_path_suffix=None,
            table_data_patcher=None,
            table_data_checker=None,
    ):
        client = get_client(server)
        output_client = get_client(self.default_proxy)
        rich_input_path = output_client.TablePath(input_table_path, start_index=start_index, end_index=end_index)
        table_data = client.read_table(rich_input_path)

        if table_data_patcher is not None:
            table_data = table_data_patcher(table_data)

        if table_data_checker is not None:
            if not table_data_checker(table_data):
                return False

        output_path = pj(yt_output_dir, output_table_path_suffix[2:] if output_table_path_suffix else input_table_path[2:])
        # We get rid of '//' in yt path once it cannot be handled by path.join
        if client.get_attribute(input_table_path, 'sorted'):
            rich_output_path = output_client.TablePath(
                output_path,
                sorted_by=list(client.get_attribute(input_table_path, 'sorted_by')))
        else:
            rich_output_path = output_path

        output_client.create('table', rich_output_path, recursive=True, ignore_existing=True)
        output_client.write_table(rich_output_path, table_data)

        logging.info('%s sample created. Output path=%s', delivery, rich_output_path)
        logging.info('%s OK', delivery)
        return True

    def hand_written_sampling(self, failed_deliveries, delivery_config, yt_output_dir, deliveries, delivery_prefix):  # noqa
        hand_made = {
            'AddTimeJupiterSamovarPreparat': {
                'custom_sample_func': TestPreparer.no_sample,
            },
            'AntispamAttRules': {
                'from_raw_delivery_table': True,
            },
            'AntispamErfs': {
                'remote_server': 'arnold',
                'path': '//home/antispam/export/erf/AntispamErfs/{}/AntispamErfs',
                'meta': '//home/antispam/export/erf/AntispamErfs/@for_production',
                'from_raw_delivery_table': True,
            },
            'AntispamOwnerAggregates': {
                'path': '//home/antispam/jupiter-deduce/{}/AntispamOwnerAggregates',
                'meta': '//home/antispam/jupiter-deduce/@for_production',
                'from_raw_delivery_table': True,
            },
            'AntispamOwnerAggregatesMeta': {
                'path': '//home/antispam/jupiter-deduce/{}/AntispamOwnerAggregatesMeta',
                'meta': '//home/antispam/jupiter-deduce/@for_production',
                'from_raw_delivery_table': True,
            },
            'AntispamOwner': {
                'path': '//home/antispam/export/AntispamOwner/{}/AntispamOwner',
                'meta': '//home/antispam/export/AntispamOwner/@for_production',
                'from_raw_delivery_table': True,
            },
            'AntispamSamovarPreparat': {
                'custom_sample_func': TestPreparer.no_sample,
            },
            'TurboUrls': {
                'path': '//home/antispam/export/erf/TurboUrls/{}/TurboUrls',
                'meta': '//home/antispam/export/erf/TurboUrls/@for_production',
                'from_raw_delivery_table': True,
            },
            'AntispamExtraRules': {
                'from_raw_delivery_table': True,
            },
            'AntispamMemorandum': {
                'custom_sample_func': self.antispam_export_sample,
            },
            'AntispamMemorandumVideo': {
                'custom_sample_func': self.antispam_export_sample,
            },
            'AntispamRulesPatch': {
                'custom_sample_func': self.antispam_export_sample,
            },
            'AntispamHost': {
                'path': '//home/antispam/export/herf/AntispamHost/{}/AntispamHost',
                'meta': '//home/antispam/export/herf/AntispamHost/@for_production',
                'from_raw_delivery_table': True,
            },
            'ClicksHostErf': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//userfeat/export/long_user_search/{}/host/clicks_shows_erf'
            },
            'ClicksOwnErf': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//userfeat/export/long_user_search/{}/owner/clicks_shows_erf'
            },
            'DocAura': {
                'from_raw_delivery_table': True,
            },
            'ExternalSnippets': {
                'path': '//home/snippets/production/{0}/{1}/{0}',
                'sources': [
                    'catalog',
                    'encyc',
                ],
                'meta': '//home/snippets/production/{0}/@last_release',
            },
            'FakeJupiterSamovarPreparat': {
                'custom_sample_func': TestPreparer.no_sample,
            },
            'HasVideo': {
                'custom_sample_func': self.middle_table_sample,
            },
            'HostMirror': {
                'path': '//home/mirrors/dump',
                'custom_sample_func': self.host_mirror_sample,
            },
            'UserSearchSlowLongIndexAnn': {
                'meta': '//home/userfeat/@userfeat_meta/slow_long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/slow_long_user_search/{0}/indexann/indexann'
            },
            'UserSearchSlowLongQueryUrlUserData': {
                'meta': '//home/userfeat/@userfeat_meta/slow_long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/slow_long_user_search/{0}/query_url/query_clicks_userdata'
            },
            'UserSearchHostReturnFeatures': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/host/host_return_features',
            },
            'UserSearchRandomLogHost': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/host/random_log_host',
                'remote_server': 'hahn.yt.yandex.net',
            },
            'UserSearchRandomLogOwner': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/owner/random_log_owner',
            },
            'UserSearchIndexAnn': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/indexann/indexann',
            },
            'UserSearchStaticUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/url/erf_mr_static_features',
            },
            'ClickMachineWeeklyShowsClicks': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/url/click_machine_weekly_shows_clicks',
            },
            'UserSearchQueryUrlUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{0}/query_url/query_clicks_userdata',
            },
            'UserBrowseIndexAnn': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_browse_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_browse/{0}/indexann/indexann',
            },
            'UserBrowseStaticUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_browse_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_browse/{0}/url/erf_mr_static_features',
            },
            'UserBrowseQueryUrlUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_browse_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_browse/{0}/query_url/query_clicks_userdata',
            },
            'MiscDataIndexAnn': {
                'meta': '//home/userfeat/@userfeat_meta/long_miscdata_meta/state_for_production',
                'path': '//home/userfeat/export/long_miscdata/{0}/indexann/indexann'
            },
            'MiscDataStaticUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_miscdata_meta/state_for_production',
                'path': '//home/userfeat/export/long_miscdata/{0}/url/erf_mr_static_features',
            },
            'MiscDataQueryUrlUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_miscdata_meta/state_for_production',
                'path': '//home/userfeat/export/long_miscdata/{0}/query_url/query_clicks_userdata',
            },
            'UserCountersStaticUserData': {
                'meta': '//home/userfeat/@userfeat_meta/long_user_counters_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_counters/{0}/url/erf_mr_static_features',
            },
            'IndexAnnFast': {
                'meta': '//userfeat/@userfeat_meta/fast_userdata_meta/state_for_production',
                'path': '//userfeat/userdata/fast/production/{0}/one/jupiter/IndexAnnSourceDataFast',
            },
            'IndexUserOwnM': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/middle_meta/state_for_production',
                'path': '//userfeat/export/middle/{0}/query_owner/indexuserown',
            },
            'IndexUserOwnQM': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/middle_meta/state_for_production',
                'path': '//userfeat/export/middle/{0}/query_owner/indexuserownq',
            },
            'IsClickunder': {
                'from_raw_delivery_table': True,
            },
            'IsPornoAdvert': {
                'from_raw_delivery_table': True,
            },
            'JupiterSamovarPreparatRaw': {
                'custom_sample_func': self.samovar_preparat_sample,
            },
            'LemurUserData': {
                'last_in_dir': True,
                'path': '//home/lemur-data/jupiter_factors/{}'
            },
            'MobileBeautyUrls': {
                'path': '//home/watto/mobile/exports/{}/MobileBeautyUrls',
                'meta': '//home/watto/mobile/exports/@for_production'
            },
            'MobileFactors': {
                'path': '//home/watto/mobile/exports/{}/MobileFactors',
                'meta': '//home/watto/mobile/exports/@for_production'
            },
            'MobileTrashAdv': {
                'from_raw_delivery_table': True,
            },
            'NastyVideo': {
                'custom_sample_func': self.middle_table_sample,
            },
            'OfflineLongVisits': {
                'path': '//home/antispam/export/herf/OfflineLongVisits/{}/OfflineLongVisits',
                'meta': '//home/antispam/export/herf/OfflineLongVisits/@for_production',
                'from_raw_delivery_table': True,
            },
            'RegClicksOwn': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//userfeat/export/long_user_search/{}/owner/clicks_shows_regional_erf'
            },
            'RegCommercialOwnerRank': {
                'from_raw_delivery_table': True,
            },
            'RegSiteBrowser': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/long_user_browse_meta/state_for_production',
                'path': '//userfeat/export/long_user_browse/{}/url/reg'
            },
            'SrcClicksM': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/middle_meta/state_for_production',
                'path': '//userfeat/export/middle/{0}/reg_map/reg_map',
            },
            'StaticUserDataFast': {
                'meta': '//userfeat/@userfeat_meta/fast_userdata_meta/state_for_production',
                'path': '//userfeat/userdata/fast/production/{0}/one/jupiter/ErfMRStaticFeaturesFast',
            },
            'TrashAdvUrl': {
                'from_raw_delivery_table': True,
            },
            'QueryUrlUserDataFast': {
                'meta': '//userfeat/@userfeat_meta/fast_userdata_meta/state_for_production',
                'path': '//userfeat/userdata/fast/production/{0}/one/jupiter/QueryClicksUserDataProtoFast',
            },
            'VideoIndexAnn': {
                'custom_sample_func': self.video_index_ann_sample,
            },
            'YaBarHostErf': {
                'remote_server': 'hahn',
                'meta': '//userfeat/@userfeat_meta/long_user_browse_meta/state_for_production',
                'path': '//userfeat/export/long_user_browse/{}/host/erf'
            },
            'YellowAdv': {
                'from_raw_delivery_table': True,
            },
            'Yellowness': {
                'from_raw_delivery_table': True,
                'meta': '//home/antispam/export/herf/Yellowness/@for_production',
                'path': '//home/antispam/export/herf/Yellowness/{}/Yellowness',
                'remote_server': 'arnold',
            },
            'ItdItpStaticFeatures': {
                'from_raw_delivery_table': True,
                'meta': '//home/izolenta/export/jupiter/itditp_static_features/@for_production',
                'path': '//home/izolenta/export/jupiter/itditp_static_features/{}/ItdItpStaticFeatures',
                'remote_server': 'arnold',
            },
            'MirrorFactorsTransferBan': {
                'from_raw_delivery_table': True,
                'path': '//home/antispam/export/pirates/auto/pirate_hosts/reject_mirror/{}/hosts',
                'meta': '//home/antispam/export/pirates/auto/pirate_hosts/reject_mirror/@for_production',
            },
            'UserdataMirrorFactorsManualTransfer': {
                'path': '//home/robot-dev/niknik/userdata-mirror-factors-transfer/{}/factors',
                'meta': '//home/robot-dev/niknik/userdata-mirror-factors-transfer/@for_production',
            },
            'USLPStatic': {
                'remote_server': 'hahn',
                'meta': '//home/userfeat/@userfeat_meta/long_user_search_meta/state_for_production',
                'path': '//home/userfeat/export/long_user_search/{}/url/uslp_static'
            }
        }

        there_will_be_no_sample_for = set(failed_deliveries) - set(hand_made.keys())
        if there_will_be_no_sample_for:
            raise Exception('There will be no sample for {}.\nWe believe it is bad.'.format(there_will_be_no_sample_for))
        failed_deliveries = set(failed_deliveries) | set(hand_made.keys())
        deliveries_to_sample = failed_deliveries & set(deliveries) if deliveries else failed_deliveries
        for delivery in sorted(deliveries_to_sample):
            if delivery not in delivery_config:
                raise Exception('Not from config {}'.format(delivery))
            if delivery in hand_made:
                server = (
                    hand_made[delivery].get('remote_server') or
                    delivery_config[delivery].get('remote_server') or
                    self.default_proxy or
                    os.environ.get('YT_PROXY')
                )
                if 'custom_sample_func' in hand_made[delivery]:
                    custom_sample_func = hand_made[delivery]['custom_sample_func']
                    if custom_sample_func == TestPreparer.no_sample:
                        continue
                    if 'path' in hand_made[delivery]:
                        remote_path = hand_made[delivery]['path']
                    else:
                        remote_path = delivery_config[delivery]['remote_path']

                    custom_sample_func(
                        delivery,
                        server,
                        remote_path,
                        yt_output_dir
                    )
                    continue
                client = get_client(server)
                if 'sources' in hand_made[delivery]:
                    for source in hand_made[delivery]['sources']:
                        logging.info('Sample %s snippet source', source)
                        state = client.get(hand_made[delivery]['meta'].format(source))
                        self.recursive_set(
                            pj(yt_output_dir, hand_made[delivery]['meta'][2:].format(source)),
                            state)
                        table_path = hand_made[delivery]['path'].format(source, state)
                        self.create_sample(delivery, server, table_path, yt_output_dir)
                    continue

                output_table_path = None
                if hand_made[delivery].get('last_in_dir'):
                    input_table_path = hand_made[delivery]['path']
                    state = [sorted(client.list(input_table_path[:input_table_path.find('{}')-1]))[-1]]
                elif hand_made[delivery].get('from_raw_delivery_table'):
                    source_name = delivery_config[delivery].get('part_of') or delivery
                    state = [client.get(
                        pj(delivery_prefix, 'delivery', source_name, '@delivery', delivery, 'ready_for_production_state'))]
                    input_table_path = pj(delivery_prefix, 'delivery', source_name, state[0], '{}.raw'.format(delivery))
                    output_table_path = hand_made[delivery].get('path') or delivery_config[delivery]['remote_path']
                    if hand_made[delivery].get('meta'):
                        self.recursive_set(pj(yt_output_dir, hand_made[delivery]['meta'][2:]), state[0])
                else:
                    state = [client.get(hand_made[delivery]['meta'])]
                    input_table_path = hand_made[delivery]['path']
                    self.recursive_set(pj(yt_output_dir, hand_made[delivery]['meta'][2:]), state[0])
                    if 'additional_meta' in hand_made[delivery]:
                        additional_meta_path = hand_made[delivery]['additional_meta'].format(*state)
                        state.append(client.get(additional_meta_path))
                        self.recursive_set(pj(yt_output_dir, additional_meta_path[2:]), state[1])

                if output_table_path:
                    output_table_path = output_table_path.format(*state)
                self.create_sample(
                    delivery,
                    server,
                    input_table_path.format(*state),
                    yt_output_dir,
                    output_table_path_suffix=output_table_path)
            else:
                raise Exception('Failed to create sample for {}. Look for logged exception above.'.format(delivery))

        if deliveries is None or 'WebMasterHosts' in deliveries:
            self.enrich_webmaster_hosts_by_samovar_preparat(yt_output_dir, delivery_config['JupiterSamovarPreparatRaw']['remote_path'])

    def try_to_prepare_test_data(self, delivery_config, yt_output_dir, deliveries):
        # use this list to filter deliveries that can pass naive but should be handmade
        filtered_naive_sampling_deliveries = ['NastyVideo', 'VideoIndexAnn']

        failed_deliveries = []

        deliveries = deliveries or delivery_config.iterkeys()
        for delivery in sorted(deliveries):
            config = delivery_config[delivery]
            if 'remote_server' not in config:
                logging.info('%s is not a table delivery', delivery)
                continue

            if delivery in filtered_naive_sampling_deliveries:
                logging.info('Delivery %s was skipped by user in naive approach', delivery)
                failed_deliveries.append(delivery)
                continue

            client = get_client(config['remote_server'])

            try:
                if not client.exists(config['remote_path']):
                    logging.warning(
                        '%s raw table wasn\'t found using naive approach. You need to create sample with bare hands.',
                        delivery
                    )
                    failed_deliveries.append(delivery)
                    continue

                output_client = get_client(self.default_proxy)

                if client.get(pj(config['remote_path'], '@type')) == 'table':
                    table_path = config['remote_path']
                else:
                    attr_value = client.get_attribute(config['remote_path'], 'for_production', None)
                    if attr_value:
                        output_client.create(
                            'map_node',
                            pj(yt_output_dir, config['remote_path'][2:]),
                            recursive=True,
                            ignore_existing=True)
                        output_client.set(pj(yt_output_dir, config['remote_path'][2:], '@for_production'), attr_value)
                        table_path = pj(config['remote_path'], attr_value, delivery)
                        if not client.exists(table_path) or client.get(pj(table_path, '@type')) != 'table':
                            table_path = None
                    else:
                        table_path = None

                if table_path is None:
                    logging.warning(
                        '%s raw table wasn\'t found using naive approach. You need to create sample with bare hands.',
                        delivery
                    )
                    failed_deliveries.append(delivery)
                    continue

                self.create_sample(delivery, config['remote_server'], table_path, yt_output_dir)
            except BaseException:
                logging.warning('Will use hand-written sampling for %s instead of regular way', delivery)
                failed_deliveries.append(delivery)

        return failed_deliveries

    @staticmethod
    def sample_file_maybe_archived(path):
        gzipped = path.endswith('.gz')
        if gzipped:
            sub.check_call(['gzip', '-d', path])
            path = path[:-len('.gz')]

        with open(path + '.tmp', 'w') as head_output:
            sub.check_call(['head', '-n', '50', path], stdout=head_output)
        shutil.move(path + '.tmp', path)

        if gzipped:
            sub.check_call(['gzip', path])

    @staticmethod
    def prepare_test_files(delivery_config, output_dir, deliveries, extfiles_path, sbclient_path):
        extfiles_path = os.path.abspath(extfiles_path)
        sbclient_path = os.path.abspath(sbclient_path)
        shutil.copyfile(sbclient_path, pj(os.path.dirname(extfiles_path), os.path.basename(sbclient_path)))
        deliveries = deliveries or list(delivery_config.iterkeys())
        bundles = []
        for delivery in sorted(deliveries):
            config = delivery_config[delivery]
            if 'sandbox_resource_type' not in config:
                continue

            if not os.path.exists(pj(output_dir, config['sandbox_resource_type'])):
                bundles.append(config['sandbox_resource_type'])

        os.chdir(output_dir)
        sub.check_call(extfiles_path + " --force-rebuild -b '' + ';'.join(bundles) + ''", shell=True)
        os.remove(pj(os.path.dirname(extfiles_path), os.path.basename(sbclient_path)))

        logging.info('All bundels downloaded')
        for delivery in sorted(deliveries):
            config = delivery_config[delivery]
            if 'sandbox_resource_type' not in config:
                continue

            logging.info('Sampling %s', delivery)
            bundle_dir = pj(output_dir, config['sandbox_resource_type'])
            for directory, _, files in os.walk(bundle_dir):
                if os.path.basename(directory) == config['sandbox_resource_type'] and 'meta.json' in files:
                    os.remove(pj(directory, 'meta.json'))
                    files.remove('meta.json')
                if 'file_to_table' in config:
                    files = os.listdir(bundle_dir)
                    for filename in files:
                        TestPreparer.sample_file_maybe_archived(pj(bundle_dir, filename))
                else:
                    for filename in files:
                        os.remove(pj(directory, filename))
                        open(pj(directory, filename), 'w').close()
