#!/usr/bin/env python
import sys
import argparse
import logging
import re
import robot.selectionrank.sr_proto_lib.schema_pb2 as srtool_schema
import robot.jupiter.protos.filter_status_pb2 as filter_status
import yt.wrapper as yt
from google.protobuf import text_format as pbtxt


def merge_three_dicts(x, y, z):
    u = x.copy()
    u.update(y)
    u.update(z)
    return u


def MapSRTestUrls(shard_filter):
    def func2(row):
        # Parse "Shard" field
        shard = row['Shard']
        match = re.match(r"(\w+)(\d+)/([\d-]+)", shard)
        if not match:
            return
        tierName, tierIdx, shardId = match.group(1, 2, 3)
        if shard_filter != tierName:
            return

        res = {}
        poolEntryLiteList = srtool_schema.TPoolEntryLiteList()
        poolEntryLiteList.ParseFromString(row['SelectionRankValidationData'])

        for p in poolEntryLiteList.PoolEntryLite:
            res['LabelsStr'] = p.LabelsStr
            res['DuplicatesCount'] = len(poolEntryLiteList.PoolEntryLite)
            res['CumulativeDocSize'] = row['CumulativeDocSize']
            res['JupiterUrl'] = row['Host'] + row['Path']
            res['Url'] = p.Url
            res['TierName'] = tierName
            res['TierIdx'] = int(tierIdx)
            res['MainSelectingRule'] = row['MainSelectingRule']
            res['UploadRankValues'] = poolEntryLiteList.UploadRankValues
            yield res

    return func2


def MapSRTestUrlsRejected():
    def func(row):
        Resolution = row['Resolution']
        UrlStatus = ''
        HttpCode = 0
        FakeDocDebugInfoString = filter_status.TFakeDocDebugInfo()
        if row['FakeDocDebugInfoString']:
            pbtxt.Parse(row['FakeDocDebugInfoString'], FakeDocDebugInfoString)
        for param in FakeDocDebugInfoString.Params:
            if param.Name == "httpCode":
                HttpCode = int(param.Value)
            if param.Name == "isRedirHttpCode" and bool(int(param.Value)):
                UrlStatus = "REDIRECT"
            if param.Name == "isGoodMime" and not bool(int(param.Value)):
                UrlStatus = "BAD_MIME_TYPE"
        if Resolution <= 2:
            UrlStatus = 'INDEXED'
        if row['HostBannedByRobotTxt']:
            UrlStatus = 'ROBOTS_HOST_ERROR'
        if row['UrlBannedByRobotTxt']:
            UrlStatus = 'ROBOTS_URL_ERROR'
        if HttpCode >= 400 and HttpCode < 512:
            UrlStatus = 'HTTP_ERROR'
        if HttpCode == 2005:
            UrlStatus = 'NO_INDEX'
        if HttpCode > 2000 and HttpCode < 3000 and HttpCode != 2004:
            UrlStatus = 'PARSER_ERROR'
        if HttpCode >= 1002 and HttpCode <= 1005:
            UrlStatus = 'PARSER_ERROR'
        if HttpCode >= 1008 and HttpCode <= 1021:
            UrlStatus = 'PARSER_ERROR'
        if row['HasRecrawledNonMainMirrorPenalty']:
            UrlStatus = 'NOT_MAIN_MIRROR'
        if row['NonCanonicCleanParams'] and row['NotMainUrl']:
            UrlStatus = 'CLEAN_PARAMS'
        if row['BannedByAntispam']:
            UrlStatus = 'SPAM'
        if UrlStatus == '':
            UrlStatus = 'OTHER'

        res = {}
        res['UrlStatus'] = UrlStatus
        res['Url'] = row['Host'] + row['Path']
        yield res

    return func


class Reduce:
    THUMB_CURRENT_TO_JUPITER = 0
    THUMB_SR_TEST_URLS = 1
    THUMB_SR_TEST_URLS_FILTER_STATUS = 2

    def __init__(self, lostTier=None, lostTierIdx=2):
        if lostTier is None:
            lostTier = 'LostTier'
        self.lostTier = lostTier
        self.lostTierIdx = lostTierIdx

    def __call__(self, key, rows):
        left_tables = []
        right_tables = []
        right_filtered_tables = []

        for row in rows:
            table_index = row['@table_index']
            if table_index == Reduce.THUMB_CURRENT_TO_JUPITER:
                left_tables.append(row)
            elif table_index == Reduce.THUMB_SR_TEST_URLS:
                right_tables.append(row)
            elif table_index == Reduce.THUMB_SR_TEST_URLS_FILTER_STATUS:
                right_filtered_tables.append(row)

        for l in left_tables:
            if len(right_filtered_tables) == 0:
                fake_filtered = {}
                fake_filtered['UrlStatus'] = 'UNKNOWN'
                fake_filtered['Url'] = l['Url']
                right_filtered_tables.append(fake_filtered)
            if len(right_tables) == 0:
                fake = {}
                poolEntryLiteList = srtool_schema.TPoolEntryLiteList()
                poolEntryLiteList.ParseFromString(l['PoolEntryLiteList'])
                poolEntryLites = [pel for pel in poolEntryLiteList.PoolEntryLite]

                for p in poolEntryLites:
                    fake['LabelsStr'] = p.LabelsStr
                    fake['DuplicatesCount'] = 0
                    fake['CumulativeDocSize'] = 0
                    fake['Url'] = p.Url
                    fake['JupiterUrl'] = p.Url
                    fake['TierName'] = self.lostTier
                    fake['TierIdx'] = self.lostTierIdx
                    fake['MainSelectingRule'] = 'unk'
                    right_tables.append(fake)

            for r in right_tables:
                for rf in right_filtered_tables:
                    if r['MainSelectingRule'] == 'unk' and rf['UrlStatus'] == 'INDEXED':
                        rf['UrlStatus'] = 'SR'
                    yield merge_three_dicts(r, rf, l)


def main():
    yt.initialize_python_job_processing()
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-to-jupiter", required=True, help="Table #0", dest="current_to_jupiter")
    parser.add_argument("--sr-test-urls", required=True, help="Table #1", dest="sr_test_urls")
    parser.add_argument("--sr-test-urls-filtered", required=True, help="Table #1", dest="sr_test_urls_filtered")
    parser.add_argument('--dst', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--dataset-alias', required=True)
    parser.add_argument('--proxy')
    parser.add_argument('--token')
    parser.add_argument('--yt-pool', default='ukrop_research')
    parser.add_argument('--shard-filter', default='WebTier', dest='shard_filter')
    args = parser.parse_args()

    if args.proxy:
        yt.config.set_proxy(args.proxy)
    if args.token:
        yt.config.config['token_path'] = args.token
    logging.getLogger("Yt").setLevel(logging.INFO)
    yt.config["tabular_data_format"] = yt.YsonFormat(control_attributes_mode='row_fields')

    spec = {
        'pool': args.yt_pool,
        'data_size_per_job': 2 ** 28,
        'fair_share_preemption_timeout': 600000,
        'mapper': {
            "tmpfs_path": ".", "copy_files": True
        },
        'enable_input_table_index': True,
        'partitions_count': 100
    }

    yt.run_map(
        MapSRTestUrls(args.shard_filter),
        source_table=args.sr_test_urls,
        destination_table=args.dst,
        spec=spec
    )

    yt.run_sort(
        args.dst,
        sort_by=['Url']
    )

    yt.run_map(
        MapSRTestUrlsRejected(),
        source_table=args.sr_test_urls_filtered,
        destination_table=args.dst+"_filtered",
        spec=spec
    )

    yt.run_sort(
        args.dst+"_filtered",
        sort_by=['Url']
    )

    yt.run_reduce(
        binary=Reduce(),
        source_table=[args.current_to_jupiter, args.dst, args.dst+"_filtered"],
        destination_table=args.dst,
        reduce_by=['Url'],
        format=yt.YsonFormat(control_attributes_mode='row_fields'),  # needed to obtain @row_index
        spec=spec
    )

    yt.run_sort(
        args.dst,
        sort_by=['TierIdx', 'CumulativeDocSize', 'UrlStatus']
    )

    with open(args.output, 'w') as file:
        file.write(args.dataset_alias)
        file.write("\n")
        prevCumulativeDocSize = 0
        prevTierCumulativeDocSize = 0
        prevTier = "-1"
        for line in yt.read_table(args.dst, format='<columns=[TierIdx;CumulativeDocSize;LabelsStr;MainSelectingRule;UrlStatus]>schemaful_dsv'):
            if prevTier != line['TierIdx']:
                prevTier = line['TierIdx']
                prevTierCumulativeDocSize = prevCumulativeDocSize
            prevCumulativeDocSize = int(line['CumulativeDocSize'])

            file.write('\t'.join([line['TierIdx'], str(prevCumulativeDocSize + prevTierCumulativeDocSize), line['LabelsStr'], line['MainSelectingRule'], line['UrlStatus']]))
            file.write("\n")


if __name__ == '__main__':
    sys.exit(main())
