from ukrop.common.blocks import \
    GetMRTable, SRRetrieveTestPool, ApplyUtil, build_sr_retrieve_test_pool, plotBuilderOnPositives, \
    build_sr_compare_jupiter_validates, SingleOptionToTextOutput, SRCompareJupiterValidates, plotsConfig, \
    BuildDelayedFileMessage, Email, buildYtPieReport, BuildPieReport
from ukrop.common.jupiter import get_jupiter_valid_states, get_cluster_name
from collections import namedtuple

VALIDATION_SET_TEMPLATE = '//home/jupiter/selectionrank/{}/validation_set_urls'
VALIDATION_SET_FILTERED_TEMPLATE = '//home/jupiter/selectionrank/{}/validation_set_urls_filter_status'
RAW_TEST_TO_JUPITER_TEMPLATE = '//home/jupiter/delivery_snapshot/{}/SelectionRankValidationData/SelectionRankValidationData.raw'

ValidationTuple = namedtuple('ValidationTuple', ['validation_set', 'validation_set_filtered', 'raw_test', 'state', 'name'])


def test_jupiters_url_pool(args):
    if args.custom_jupiter_states is not None and len(args.custom_jupiter_states) > 0:
        jupiter_states = args.custom_jupiter_states
    else:
        jupiter_states = get_jupiter_valid_states()
    mr_validation_tables = []
    print "Following states were found:"
    for state in jupiter_states:
        pair = ValidationTuple(
            validation_set=VALIDATION_SET_TEMPLATE.format(state),
            validation_set_filtered=VALIDATION_SET_FILTERED_TEMPLATE.format(state),
            raw_test=RAW_TEST_TO_JUPITER_TEMPLATE.format(state),
            state=state,
            name=state
            )
        mr_validation_tables.append(pair)
        print "-", state

    if args.custom_validation_set is not None:
        for custom_set in args.custom_validation_set:
            path, name, state = custom_set.split(':')
            pair = ValidationTuple(
                validation_set=path,
                validation_set_filtered=path+'_filter_status',
                raw_test=RAW_TEST_TO_JUPITER_TEMPLATE.format(state),
                state=state,
                name=name
            )
            mr_validation_tables.append(pair)
            print "*", state, name

    dumpedFiles = []
    waiting_for_files = []

    cluster_name = get_cluster_name()
    for validation_tuple in mr_validation_tables:
        sr_test_urls = GetMRTable(
            cluster=cluster_name,
            table=validation_tuple.validation_set,
            creationMode='CHECK_EXISTS',
            name="validation_set " + validation_tuple.state
        )

        sr_test_urls_filtered = GetMRTable(
            cluster=cluster_name,
            table=validation_tuple.validation_set_filtered,
            creationMode='CHECK_EXISTS',
            name="validation_set_filtered " + validation_tuple.state
        )

        raw_test_table = GetMRTable(
            cluster=cluster_name,
            table=validation_tuple.raw_test,
            creationMode='CHECK_EXISTS',
            name="raw_test " + validation_tuple.state
        )

        retrieveTestPool = SRRetrieveTestPool(
            sr_retrieve_test_pool=build_sr_retrieve_test_pool.outputs.ARCADIA_PROJECT,
            current_to_jupiter=raw_test_table.outputs.outTable,
            sr_test_urls=sr_test_urls.outputs.outTable,
            sr_test_urls_filtered=sr_test_urls_filtered.outputs.outTable,
            alias=validation_tuple.state,
            name=validation_tuple.state,
            max_ram=2048
        )

        dumpedFiles.append(retrieveTestPool.outputs.dumped_file)

        buildPieReport = BuildPieReport(
            util=buildYtPieReport.outputs.ARCADIA_PROJECT,
            input=retrieveTestPool.outputs.dst,
            plots=plotsConfig.outputs.json,
            kit_name=validation_tuple.state,
            name=validation_tuple.state
        )

        waiting_for_files.append(buildPieReport.outputs.pie_pdf)

    applyUtil = ApplyUtil(
        util=plotBuilderOnPositives.outputs.ARCADIA_PROJECT,
        res_files=dumpedFiles,
        plots=plotsConfig.outputs.json,
        max_ram=32784,
        columns='TierIdx,DocSize,Labels,SelectionRankRule,UrlStatus'
    )

    args_str = ' '.join(['-v {validation_table} -s {state} -n {name}'.format(
        validation_table=validation_tuple.validation_set,
        state=validation_tuple.state,
        name=validation_tuple.name
    ) for validation_tuple in sorted(mr_validation_tables, key=lambda l: l.state)])

    jupiterBranchesHelper = SingleOptionToTextOutput(
        input=args_str,
        addTrailingNewLine=False,
    )

    waiting_for_files.append(
        SRCompareJupiterValidates(
            util=build_sr_compare_jupiter_validates.outputs.ARCADIA_PROJECT,
            args_str=jupiterBranchesHelper.outputs.output,
            max_ram=4096,
            mr_default_cluster=cluster_name,
        ).outputs.report_html
    )
    waiting_for_files.append(applyUtil.outputs.report_pdf)

    # Send an email if blocks in results finished
    buildDelayedFileMessage = BuildDelayedFileMessage(
        wait_for_inputs=waiting_for_files,
        input='Successfully completed the comparison on ',
        addTrailingNewLine=False
    )

    email = Email(
        body=buildDelayedFileMessage.outputs.text_output,
        attach=[applyUtil.outputs.report_pdf],
        subject='SUCCESS on %s' % ', '.join(jupiter_states),
        sender='selectionrank-alerts@yandex-team.ru',
        recipients=['selectionrank-alerts@yandex-team.ru']
    )

    return email
