#include "util/system/env.h"
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/tools/taxi-trackstory-archive/internal/options_parser.hpp>

Y_UNIT_TEST_SUITE(archive_options_test) {
    Y_UNIT_TEST(base_test) {
        const char* argv[] = {
            "./executable",
            "--yt-proxy",
            "hahn",
            "--source-table=//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00",
            "--destination-table=//home/taxi/home/vaninvv/removeme_aaa",
            "--mds-bucket=taxi-camera-testing",
            "--mds-host=s3.mdst.yandex.net",
            "--mds-prefix=splittest",
            "--uuid-field=contractor_uuid",
            "--dbid-field=contractor_dbid",
            "--timestamp-field=unix_timestamp",
            "--split-column=pipeline",
            "--jobs-count=1",
            "--ttl-days=123",
            "--timestamp-divisor=1000000",
            "--replace-empty-dbid-with=$",
            "--enable-filter=true",
        };
        const int argc = sizeof(argv) / sizeof(*argv);
        SetEnv("AWS_ACCESS_KEY_ID", "access_key");
        SetEnv("AWS_SECRET_ACCESS_KEY", "secret_key");

        NTrackArchiver::TParams params;
        params.Process(argc, argv);

        UNIT_ASSERT_EQUAL(params.YtProxy, "hahn");
        UNIT_ASSERT_EQUAL(params.InputTables, TVector<TString>{"//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00"});
        UNIT_ASSERT_EQUAL(params.OutputTable, "//home/taxi/home/vaninvv/removeme_aaa");
        UNIT_ASSERT_EQUAL(params.MdsBucket, "taxi-camera-testing");
        UNIT_ASSERT_EQUAL(params.MdsHost, "s3.mdst.yandex.net");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.UuidField, "contractor_uuid");
        UNIT_ASSERT_EQUAL(params.DbidField, "contractor_dbid");
        UNIT_ASSERT_EQUAL(params.TimestampField, "unix_timestamp");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.ColumnSpliterPrefix, "pipeline");
        UNIT_ASSERT_EQUAL(params.JobsCount, 1);
        UNIT_ASSERT_EQUAL(params.TtlDays, 123);
        UNIT_ASSERT_EQUAL(params.TimestampDivisor, 1000000);
        UNIT_ASSERT_EQUAL(params.MdsAccessKey, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsSecretKey, "secret_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames.size(), 1);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].access_key, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].secret_key, "secret_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].host, params.MdsHost);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].bucket, params.MdsBucket);
        UNIT_ASSERT_EQUAL(params.enable_filter, true);
        UNIT_ASSERT_EQUAL(params.EmptyDbidPlaceholder, "$");
    }

    Y_UNIT_TEST(no_split_test) {
        const char* argv[] = {
            "./executable",
            "--yt-proxy",
            "hahn",
            "--source-table=//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00",
            "--destination-table=//home/taxi/home/vaninvv/removeme_aaa",
            "--mds-bucket=taxi-camera-testing",
            "--mds-host=s3.mdst.yandex.net",
            "--mds-prefix=splittest",
            "--uuid-field=contractor_uuid",
            "--dbid-field=contractor_dbid",
            "--timestamp-field=unix_timestamp",
            "--jobs-count=1",
            "--timestamp-divisor=1000000",
        };
        const int argc = sizeof(argv) / sizeof(*argv);
        SetEnv("AWS_ACCESS_KEY_ID", "access_key");
        SetEnv("AWS_SECRET_ACCESS_KEY", "secret_key");

        NTrackArchiver::TParams params;
        params.Process(argc, argv);

        UNIT_ASSERT_EQUAL(params.YtProxy, "hahn");
        UNIT_ASSERT_EQUAL(params.InputTables, TVector<TString>{"//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00"});
        UNIT_ASSERT_EQUAL(params.OutputTable, "//home/taxi/home/vaninvv/removeme_aaa");
        UNIT_ASSERT_EQUAL(params.MdsBucket, "taxi-camera-testing");
        UNIT_ASSERT_EQUAL(params.MdsHost, "s3.mdst.yandex.net");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.UuidField, "contractor_uuid");
        UNIT_ASSERT_EQUAL(params.DbidField, "contractor_dbid");
        UNIT_ASSERT_EQUAL(params.TimestampField, "unix_timestamp");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.ColumnSpliterPrefix, "");
        UNIT_ASSERT_EQUAL(params.JobsCount, 1);
        UNIT_ASSERT_EQUAL(params.TimestampDivisor, 1000000);
        UNIT_ASSERT_EQUAL(params.MdsAccessKey, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsSecretKey, "secret_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames.size(), 1);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].access_key, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].secret_key, "secret_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].host, params.MdsHost);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].bucket, params.MdsBucket);
    }

    Y_UNIT_TEST(override_config) {
        const char* argv[] = {
            "./executable",
            "--yt-proxy", "hahn",
            "--source-table=//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00",
            "--destination-table=//home/taxi/home/vaninvv/removeme_aaa",
            "--mds-bucket=taxi-camera-testing",
            "--mds-host=s3.mdst.yandex.net",
            "--mds-prefix=splittest",
            "--uuid-field=contractor_uuid",
            "--dbid-field=contractor_dbid",
            "--timestamp-field=unix_timestamp",
            "--split-column=pipeline",
            "--jobs-count=1",
            "--timestamp-divisor=1000000",
            R"(--mds-override-config=
            {
                "mds_clients": {
                    "someclient": {
                        "host": "s333.mdst.yandex.net",
                        "bucket": "taxi-camera-testing2",
                        "access_key": "ACCESS_KEY",
                        "secret_key": "SECRET_KEY"
                    }
                },
                "pipelines": {
                    "taxi": {
                        "client": "someclient",
                        "prefix": "splittesttaxi"
                     },
                    "go-users": {
                        "client": "someclient",
                        "prefix": "splittestaa/gousers"
                    }
                }
            }
            )"};
        const int argc = sizeof(argv) / sizeof(*argv);
        SetEnv("AWS_ACCESS_KEY_ID", "access_key");
        SetEnv("AWS_SECRET_ACCESS_KEY", "secret_key");
        SetEnv("ACCESS_KEY", "access_key2");
        SetEnv("SECRET_KEY", "secret_key2");

        NTrackArchiver::TParams params;
        params.Process(argc, argv);

        UNIT_ASSERT_EQUAL(params.YtProxy, "hahn");
        UNIT_ASSERT_EQUAL(params.InputTables, TVector<TString>{"//home/logfeller/logs/positions-log/1h/2022-01-11T14:00:00"});
        UNIT_ASSERT_EQUAL(params.OutputTable, "//home/taxi/home/vaninvv/removeme_aaa");
        UNIT_ASSERT_EQUAL(params.MdsBucket, "taxi-camera-testing");
        UNIT_ASSERT_EQUAL(params.MdsHost, "s3.mdst.yandex.net");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.UuidField, "contractor_uuid");
        UNIT_ASSERT_EQUAL(params.DbidField, "contractor_dbid");
        UNIT_ASSERT_EQUAL(params.TimestampField, "unix_timestamp");
        UNIT_ASSERT_EQUAL(params.MdsPrefix, "splittest");
        UNIT_ASSERT_EQUAL(params.ColumnSpliterPrefix, "pipeline");
        UNIT_ASSERT_EQUAL(params.JobsCount, 1);
        UNIT_ASSERT_EQUAL(params.TimestampDivisor, 1000000);
        UNIT_ASSERT_EQUAL(params.MdsAccessKey, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsSecretKey, "secret_key");

        UNIT_ASSERT_EQUAL(params.MdsClientsByNames.size(), 2);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].access_key, "access_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].secret_key, "secret_key");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].host, params.MdsHost);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["__default__"].bucket, params.MdsBucket);
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["someclient"].access_key, "access_key2");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["someclient"].secret_key, "secret_key2");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["someclient"].host, "s333.mdst.yandex.net");
        UNIT_ASSERT_EQUAL(params.MdsClientsByNames["someclient"].bucket, "taxi-camera-testing2");
    }
}
