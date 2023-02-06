import argparse
import os
import datetime
import yt.wrapper as ytw

from nirvana_api import NirvanaApi, GlobalParameter, ParameterValue, ParameterType
from nirvana_api.highlevel_api import create_workflow, create_workflow_parameters, run_workflow
from ukrop.common.jupiter import get_jupiter_production_state
from robot.quality.robotrank.nirvana.common.blocks import (GetMrTable, GetMRDirectory,
                   JoinUserdata, JoinFactors, MakeUnbiased, ReferrerEdr, ApplyFormula, ApplyFormulaRemap,
                   ParseCrawlAttempt, SvnCheckoutOneFile, CalcBorders, RRTestAddJupiterLabels, RRFetchProdHostBorders,
                   RRTestJoinLabels, MRCopy, GetLossesFromMetrics, RRTestCreateEntryWithLabel, RRTestCalcFactors, get_rr_tool,
                   get_metrics_losses_tool)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', help='oauth token for nirvana', required=True)
    parser.add_argument('--yt-secret', required=True)
    parser.add_argument('--mr-account', required=True)
    parser.add_argument('--yt-pool', required=True)
    parser.add_argument('--proxy', default='banach')
    parser.add_argument('--dst-path', default='//home/robot-metrics/refferrank_test_pool')
    parser.add_argument('--blocks-ttl', default=1000, type=int)
    parser.add_argument('--timestamp', default=datetime.datetime.now().isoformat())
    return parser.parse_args()


def create_graph(args, title, block):
    nirvana = NirvanaApi(args.token)

    workflow = create_workflow(nirvana, title, block, quota_project_id='robot-quality')
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


def main(args):
    ytw.config.set_proxy(args.proxy)

    rr_tool = get_rr_tool()

    crawl_attempt_dir = GetMRDirectory(
        cluster='banach',
        path='//home/ukropdata/crawlattempt_log'
    ).outputs.mr_directory

    parsed_crawl_attempt = RRTestParseCrawlAttempt(
        rr_tool=rr_tool,
        logs_dir=crawl_attempt_dir,
    ).outputs.result

    unbiased_pool = RRTestMakeUnbiased(
        rr_tool=rr_tool,
        input=parsed_crawl_attempt,
        policy='random_recrawl',
    ).outputs.result

    edr_table = GetMrTable(
        table='//home/ukropdata/FullExtDataRankExtended/actual_protobin',
        cluster='banach'
    ).outputs.outTable

    zone_config = SvnCheckoutOneFile(
        path='yweb/robot/ukrop/conf/conf-production/zones/zoneconfig.pb.txt',
    ).outputs.file

    prod_fml = SvnCheckoutOneFile(
        path='yweb/robot/lemur/mnformulas/RefererRankZonal.info',
    ).outputs.file

    prod_fml_remap = SvnCheckoutOneFile(
        path='yweb/robot/lemur/mnformulas/RefererRankZonalRemap.tsv',
    ).outputs.file

    triggers_config = SvnCheckoutOneFile(
        path='yweb/robot/ukrop/conf/conf-production/kiwi/triggers.pb.txt',
    ).outputs.file

    factros_table = GetMrTable(
        table="//home/ukropdata/PostponedFactors/result",
        cluster='banach'
    ).outputs.outTable

    with_factors = RRTestJoinFactors(
        rr_tool=rr_tool,
        pool=unbiased_pool,
        factors=[factros_table],
    ).outputs.result

    with_refferer_edr = ReferrerEdr(
        rr_tool=rr_tool,
        pool=with_factors,
        edr=edr_table,
        zone_config=zone_config,
    ).outputs.result

    apply_prod_fml = RRApplyFormula(
        rr_tool=rr_tool,
        pool=with_factors,
        formula=[prod_fml],
        formula_alias=['production']
    ).outputs.result

    apply_prod_fml_remap = RRApplyFormulaRemap(
        rr_tool=rr_tool,
        predictions=apply_prod_fml,
        remap=prod_fml_remap,
        formula_name='production',
    ).outputs.result

    prod_host_borders = RRFetchProdHostBorders(
        rr_tool=rr_tool,
        policy='refererrank',
    ).outputs.result

    pool_with_borders = RRTestCalcBorders(
        rr_tool=rr_tool,
        input=with_refferer_edr,
        prod_predictions=apply_prod_fml_remap,
        prod_host_borders=prod_host_borders,
        policy='refererrank',
        prod_formula_name='production',
        zone_config=zone_config,
    )

    create_graph(args, 'create refererrank test', pool_with_borders)


if __name__ == '__main__':
    main(parse_args())
