import argparse
import os
import json
import datetime
import yt.wrapper as ytw

from nirvana_api import NirvanaApi, GlobalParameter, ParameterValue, ParameterType
from nirvana_api.highlevel_api import create_workflow
from ukrop.common.jupiter import get_jupiter_production_state
from robot.quality.robotrank.nirvana.common.blocks import (GetMrTable, GetMRDirectory, SetRRTestLabels, SetFormulaName,
                   JoinUserdata, JoinSpam, JoinFactors, MakeUnbiased, ApplyFormula, ApplyFormulaRemap,
                   ParseCrawlAttempt, SvnCheckoutOneFile, CalcBorders, AddSearchBaseInfo, FetchProdHostBorders,
                   MergeData, MRCopy, GetLossesFromMetrics, CreateEntryWithLabel, CalcRRFactors, get_rr_tool,
                   get_metrics_losses_tool, get_set_fml_name_tool)
from robot.quality.nirvana.common.upload import upload_json
from google.protobuf.text_format import Parse

import yweb.robot.ukrop.protos.zoneconfig_pb2 as zoneconfig_pb2
import robot.lemur.algo.userdata.protos.userdata_pb2 as userdata_pb2
import __res


CONFIGS_REVISION = 3846526


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', help='oauth token for nirvana', required=True)
    parser.add_argument('--yt-secret', required=True)
    parser.add_argument('--mr-account', required=True)
    parser.add_argument('--metrics-secret', default='robot_metrics_musca_metrics_token')
    parser.add_argument('--yt-pool', required=True)
    parser.add_argument('--proxy', default='banach')
    parser.add_argument('--dst-path', default='//home/robot-metrics/rr_test_pool')
    parser.add_argument('--blocks-ttl', default=1000, type=int)
    parser.add_argument('--timestamp', default=datetime.datetime.now().isoformat())
    parser.add_argument('--userdata-label-config', default=None)
    parser.add_argument('--nirvana-quota', default='robot-coverage-metric-fresh')
    return parser.parse_args()


def create_graph(args, title, block):
    nirvana = NirvanaApi(args.token)

    workflow = create_workflow(nirvana, title, block, quota_project_id=args.nirvana_quota)
    nirvana.edit_workflow(workflow.id, execution_params={'resultsTtlDays': 14})
    workflow.add_global_parameters(
        [
            GlobalParameter('mr-account', ParameterType.string),
            GlobalParameter('yt-token', ParameterType.secret),
            GlobalParameter('yt-pool', ParameterType.string),
            GlobalParameter('timestamp', ParameterType.string),
            GlobalParameter('ttl', ParameterType.integer),
        ]
    )
    parameterValues = [
        ParameterValue('mr-account', args.mr_account),
        ParameterValue('yt-token', args.yt_secret),
        ParameterValue('yt-pool', args.yt_pool),
        ParameterValue('timestamp', args.timestamp),
        ParameterValue('ttl', args.blocks_ttl),
    ]
    workflow.set_global_parameters(parameterValues)
    workflow.link_block_parameters(param_refs=[
        {
            'parameter': param.parameter,
            'derivedFrom': param.parameter
        } for param in parameterValues]
    )

    print workflow.id


def get_losses(args, status):
    return GetLossesFromMetrics(
        binary=get_metrics_losses_tool(),
        status=status,
        cron_id='9234',
        regional_type='WORLD',
        metrics_token=args.metrics_secret,
    ).outputs.urls


def load_zones():
    zoneConfig = __res.find("zoneconfig.pb.txt")
    zones = []
    record = zoneconfig_pb2.TZoneConfig()
    Parse(zoneConfig, record)
    for rec in record.Zones:
        zones.append(rec.ZoneStr)
    return zones


def check_label_config(label_config):
    if label_config is None:
        return
    conf = json.load(open(label_config))
    assert set(conf.keys()) == {"labels"}
    labelKeys = {"name", "zones", "log"}
    zonesSet = set(load_zones())
    logsSet = set(userdata_pb2.ELogCounterType.keys())

    for lb in conf["labels"]:
        for k in lb.keys():
            assert k in labelKeys
        assert "name" in lb.keys()
        if "zones" in lb.keys():
            for z in lb["zones"]:
                assert z in zonesSet
        assert lb["log"] in logsSet


def main(args):
    ytw.config.set_proxy(args.proxy)

    if args.userdata_label_config is not None:
        check_label_config(args.userdata_label_config)

    rr_tool = get_rr_tool()

    crawl_attempt_dir = GetMRDirectory(
        cluster='banach',
        path='//home/ukropdata/crawlattempt_log'
    ).outputs.mr_directory

    parsed_crawl_attempt = ParseCrawlAttempt(
        rr_tool=rr_tool,
        logs_dir=crawl_attempt_dir,
    ).outputs.result

    unbiased_pool = MakeUnbiased(
        rr_tool=rr_tool,
        input=parsed_crawl_attempt,
        policy='random_crawl',
    ).outputs.result

    userdata_table = GetMrTable(
        table='//home/lemur-userdata/merged',
        cluster='banach'
    ).outputs.outTable

    zone_config = SvnCheckoutOneFile(
        path='yweb/robot/ukrop/conf/conf-production/zones/zoneconfig.pb.txt',
        revision=CONFIGS_REVISION
    ).outputs.file

    triggers_config = SvnCheckoutOneFile(
        path='yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt',
        revision=CONFIGS_REVISION
    ).outputs.file

    jupiter_state = get_jupiter_production_state()

    urlinfo_table = GetMrTable(
        table='//home/jupiter/acceptance/{}/urls_for_webmaster_simple'.format(jupiter_state),
        cluster='banach'
    ).outputs.outTable

    dups_table = GetMrTable(
        table='//home/jupiter/constellations/{}/duplicates'.format(jupiter_state),
        cluster='banach'
    ).outputs.outTable

    spam_owners_table = GetMrTable(
        table='//home/antispam/export/ukrop/banned_pessimized'.format(jupiter_state),
        cluster='banach'
    ).outputs.outTable

    with_jupiter_labels = AddSearchBaseInfo(
        rr_tool=rr_tool,
        pool=unbiased_pool,
        urlinfo=urlinfo_table,
        dups_info=dups_table,
    ).outputs.result

    with_userdata = JoinUserdata(
        rr_tool=rr_tool,
        pool=unbiased_pool,
        userdata=userdata_table,
        triggers_conf=triggers_config,
    ).outputs.result

    with_spam = JoinSpam(
        rr_tool=rr_tool,
        pool=unbiased_pool,
        spam_owners=spam_owners_table,
    ).outputs.result

    crawled_urls = get_losses(args, 'CRAWLED')
    not_crawled_urls = get_losses(args, 'NOT_CRAWLED')

    crawled_entries = CreateEntryWithLabel(
        rr_tool=rr_tool,
        urls=crawled_urls,
        label='ValidateCrawled',
        entry_weight=0.0,
    ).outputs.result

    not_crawled_entries = CreateEntryWithLabel(
        rr_tool=rr_tool,
        urls=not_crawled_urls,
        label='ValidateNotCrawled',
        entry_weight=0.0,
    ).outputs.result

    crawled_factors = CalcRRFactors(
        rr_tool=rr_tool,
        urls=crawled_urls,
    ).outputs.result

    not_crawled_factors = CalcRRFactors(
        rr_tool=rr_tool,
        urls=not_crawled_urls,
    ).outputs.result

    factors_table = GetMrTable(
        table="//home/ukropdata/PostponedFactors/result",
        cluster='banach'
    ).outputs.outTable

    with_factors = JoinFactors(
        rr_tool=rr_tool,
        pool=unbiased_pool,
        factors=[factors_table],
    ).outputs.result

    merged_pool = MergeData(
        rr_tool=rr_tool,
        userdata_info=with_userdata,
        search_base_info=with_jupiter_labels,
        factors=with_factors,
        custom_labels=[crawled_entries, not_crawled_entries],
        custom_factors=[crawled_factors, not_crawled_factors],
        spam_info=with_spam,
    ).outputs.result

    prod_fml = SvnCheckoutOneFile(
        path='robot/lemur/mnformulas/RobotRankZonal.info',
    ).outputs.binary

    annotated_fml = SetFormulaName(
        binary=get_set_fml_name_tool(),
        formula=prod_fml,
        formula_name='production',
    ).outputs.result

    prod_fml_predictions = ApplyFormula(
        rr_tool=rr_tool,
        pool=with_factors,
        formula=[annotated_fml],
    ).outputs.result

    prod_fml_remap = SvnCheckoutOneFile(
        path='robot/lemur/mnformulas/RobotRankRemap.tsv',
    ).outputs.file

    apply_prod_fml_remap = ApplyFormulaRemap(
        rr_tool=rr_tool,
        predictions=prod_fml_predictions,
        remap=prod_fml_remap,
        formula_name='production',
    ).outputs.result

    prod_host_borders = FetchProdHostBorders(
        rr_tool=rr_tool,
        policy='robotrank',
    ).outputs.result

    pool_with_borders = CalcBorders(
        rr_tool=rr_tool,
        input=merged_pool,
        prod_predictions=apply_prod_fml_remap,
        prod_host_borders=prod_host_borders,
        policy='robotrank',
        prod_formula_name='production',
        zone_config=zone_config,
    ).outputs.result

    if (args.userdata_label_config is not None):
        label_config = upload_json(
            token=args.token,
            path=args.userdata_label_config,
            name=os.path.basename(args.userdata_label_config),
            quota=args.nirvana_quota,
        )
    else:
        label_config = None

    pool_with_labels = SetRRTestLabels(
        rr_tool=rr_tool,
        pool=pool_with_borders,
        config=label_config,
    ).outputs.result

    result = MRCopy(
        src=pool_with_labels,
        dst_path=args.dst_path,
        force=True,
    )

    create_graph(args, 'create robotrank test', result)


if __name__ == '__main__':
    main(parse_args())
