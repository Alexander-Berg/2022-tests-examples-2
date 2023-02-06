import datetime
from ukrop.common.jupiter import get_cluster_name, get_jupiter_production_state, get_sr_factors_path_template
from ukrop.common.blocks import \
    GetMRTable, GetUrlsFromValidationBacketWorld, \
    SRToolSampleFactors, SRConvertToLite, build_fetch_basket, labelsConfig, \
    GetMRDirectory, build_srtool, plotsConfig, get_fml_urls_script, build_geminicl, \
    get_all_as_rnd_strategy, build_add_labels, \
    SRToolGenUnbiasedSet, YtReadTsv, SRToolFilterExtDataRank, MergeMRTablesWithDst, \
    upload_urls, backet_descriptions, backet_descriptions_world

from ukrop.common.locations import FULL_EDR_TABLE, FULL_EDR_STATS_TABLE
from robot.quality.nirvana.common.blocks import GetJupiterPath
from robot.quality.nirvana.common.build import get_binary_make_jupiter_path


def get_unbiased_rnd_set(args):
    sample_params = get_all_as_rnd_strategy.outputs.json

    edr_table = GetMRTable(
        name="FullExtDataRank",
        cluster=get_cluster_name(),
        table=FULL_EDR_TABLE,
        creationMode='CHECK_EXISTS'
    ).outputs.outTable

    edr_stats_table = GetMRTable(
        name="FullExtDataRank stats",
        cluster=get_cluster_name(),
        table=FULL_EDR_STATS_TABLE,
        creationMode='CHECK_EXISTS',
    ).outputs.outTable

    all_labels = SRToolFilterExtDataRank(
        name="Get labels",
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        src_table=edr_table,
        stats_table=edr_stats_table,
        max_ram=2096,
        timestamp=args.timestamp,
        ttl=3600,
        sample_params=sample_params,
        cluster=get_cluster_name(),
    ).outputs.out_table

    unbiased_set = SRToolGenUnbiasedSet(
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        labels_table=all_labels,
        jupiter_state=get_jupiter_production_state(),
        timestamp=args.timestamp,
        cluster=get_cluster_name(),
    ).outputs.result

    result_tsv = YtReadTsv(
        table=unbiased_set,
        columns='[Url;Label;Fraction]'
    ).outputs.output_tsv

    return result_tsv


def create_test_set(args):
    start_date = str(datetime.date.today())

    to_jupiter_test_set = []
    test_set = []

    for backet in backet_descriptions:
        get_urls_from_validation_backet = GetUrlsFromValidationBacketWorld(
            fetch_basket=build_fetch_basket.outputs.ARCADIA_PROJECT,
            geminicl=build_geminicl.outputs.ARCADIA_PROJECT,
            add_labels=build_add_labels.outputs.ARCADIA_PROJECT,
            max_ram=8192,
            start_date=start_date,
            canonization_type="weak",
            metrics_secret=args.metrics_secret,
            **backet
        )
        to_jupiter_test_set.append(get_urls_from_validation_backet.outputs.original_urls)
        test_set.append(get_urls_from_validation_backet.outputs.prob_of_canonized_urls)

    for backet in backet_descriptions_world:
        get_urls_from_validation_backet = GetUrlsFromValidationBacketWorld(
            fetch_basket=build_fetch_basket.outputs.ARCADIA_PROJECT,
            geminicl=build_geminicl.outputs.ARCADIA_PROJECT,
            add_labels=build_add_labels.outputs.ARCADIA_PROJECT,
            labels=labelsConfig.outputs.json,
            max_ram=8192,
            start_date=start_date,
            metrics_secret=args.metrics_secret,
            canonization_type="weak",
            **backet
        )
        to_jupiter_test_set.append(get_urls_from_validation_backet.outputs.original_urls)
        test_set.append(get_urls_from_validation_backet.outputs.prob_of_canonized_urls)

    test_set.append(get_unbiased_rnd_set(args))

    cluster_name = get_cluster_name()

    factors_dir_name = GetJupiterPath(
        binary=get_binary_make_jupiter_path(),
        path_template=get_sr_factors_path_template(),
    ).outputs.path

    factors_dir = GetMRDirectory(
        path=factors_dir_name,
        cluster=cluster_name,
        creationMode='CHECK_EXISTS'
    ).outputs.mr_directory

    current_test_table = GetMRTable(
        cluster=cluster_name,
        table=args.test_table,
        creationMode='NO_CHECK'
    )

    sampled_factors = SRToolSampleFactors(
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        labels_table=upload_urls(test_set, plotsConfig.outputs.json, args.tmp_dir, get_cluster_name()).outputs.result,
        src_dir=factors_dir,
        random_urls_count=args.random_urls_count,
        max_ram=4048,
        timestamp='0',
        data_size_per_job=str(4 * 1024 ** 3),
        generate_labels_str=True,
        ttl=3600,
        table_name='sr_learning_pool',
        cluster=get_cluster_name()
    ).outputs.dst_table

    current_test = MergeMRTablesWithDst(
        srcs=[sampled_factors],
        dst=current_test_table.outputs.outTable,
    )

    convert_to_lite = SRConvertToLite(
        name="Generate current_to_jupiter",
        srtool=build_srtool.outputs.ARCADIA_PROJECT,
        src_table=upload_urls(to_jupiter_test_set, plotsConfig.outputs.json, args.tmp_dir, get_cluster_name()).outputs.result,
        dst_table=args.jupiter_test_table,
        cluster=get_cluster_name()
    )

    return [current_test, convert_to_lite]
