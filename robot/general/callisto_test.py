from ukrop.common.jupiter import get_cluster_name, get_jupiter_production_state, get_srpool_node
from ukrop.common.blocks import \
    GetMRTable, SRToolSampleFactors, \
    GetMRDirectory, build_srtool, get_callisto_rnd_strategy, \
    SRToolFilterExtDataRank, CallistoFilterUserdata, SRToolCalculateUserDataStat, MergeMRTablesWithDst

from ukrop.common.locations import FULL_EDR_TABLE


def create_test_set(args):
    cluster_name = get_cluster_name()
    edr_table = GetMRTable(
        name="FullExtDataRank",
        cluster=cluster_name,
        table=FULL_EDR_TABLE,
        creationMode='CHECK_EXISTS',
    ).outputs.outTable

    edr_callisto_table = CallistoFilterUserdata(
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        src_table=edr_table,
        jupiter_state=get_jupiter_production_state(),
        test=True,
    ).outputs.out_table

    edr_stats_table = SRToolCalculateUserDataStat(
        name='Calculate distribution for postponed documents',
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        src_table=edr_callisto_table,
        max_ram=2048,
        aggr_window=30,
    ).outputs.out_table

    current_test_table = GetMRTable(
        cluster=cluster_name,
        table=args.test_table,
        creationMode='NO_CHECK'
    )

    random_shows_labels = SRToolFilterExtDataRank(
        name="Get labels",
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        src_table=edr_callisto_table,
        stats_table=edr_stats_table,
        max_ram=2096,
        timestamp=args.timestamp,
        ttl=3600,
        sample_params=get_callisto_rnd_strategy.outputs.file
    ).outputs.out_table

    src_dir = GetMRDirectory(
        cluster=cluster_name,
        path=get_srpool_node(),
        creationMode='CHECK_EXISTS'
    ).outputs.mr_directory

    jupiter_test_table = GetMRTable(
        cluster=cluster_name,
        table='//home/ukropdata/selection_rank/test/current',
        creationMode='NO_CHECK'
    ).outputs.outTable

    sampled_factors = SRToolSampleFactors(
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        labels_table=random_shows_labels,
        src_dir=src_dir,
        random_urls_count=args.random_urls_count,
        max_ram=4048,
        timestamp='0',
        data_size_per_job=str(4 * 1024 ** 3),
        generate_labels_str=True,
        ttl=3600,
        table_name='sr_learning_pool_merged_tracked_rule_random_crawl',
    ).outputs.dst_table

    current_test = MergeMRTablesWithDst(
        srcs=[sampled_factors, jupiter_test_table],
        dst=current_test_table.outputs.outTable,
    )

    return [current_test]
