#pragma once

#include "host_record.h"
#include "test_transaction.h"
#include "worker_test_base.h"
#include "url_record.h"
#include "ut_common.h"

#include <robot/samovar/combustor/pushers/common/pusher.h>
#include <robot/samovar/algo/crawl/crawlconfig.h>
#include <robot/samovar/algo/locator/locator.h>
#include <robot/samovar/algo/misc/basetime.h>
#include <robot/samovar/algo/yt/transaction.h>
#include <robot/samovar/algo/record/complex_attrs/url_sitemap_basis_state/url_sitemap_basis_state.h>
#include <robot/samovar/protos/ut.pb.h>

#include <google/protobuf/text_format.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/ptr.h>
#include <util/stream/file.h>

using namespace NSamovar;

template <typename TUrlPusher>
class TUrlPusherTestBase: public TSamovarWorkerTestBase {
public:
    // define specialization of this function
    // to create non-trivial url pushers
    template <typename TPusher>
    static THolder<NSamovar::IUrlPusher> Create() {
        return MakeHolder<TPusher>("dummy");
    }

    static void RunTest(const TString& input, const TString& output) {
        auto pusher = Create<TUrlPusher>();

        NSamovarTest::TTestData testData = ReadTestData(input);
        UNIT_ASSERT_C(testData.UrlDataPushTableSize() > 0, "UrlDataPushTable should not be empty");

        if (!TCrawlConfig::IsInitialized()) {
            TCrawlConfig::InitStatic("data/crawl/crawl_config.pb.txt");
        }

        if (testData.HasTestTime()) {
            SetTestTime(testData.GetTestTime());
        }

        NSamovarTest::TTestData result;
        TTestTransaction tx(result);

        TUrlRecordPtr urlRecord;
        THostRecordPtr hostRecord;

        for (auto& urlDataPush : *testData.MutableUrlDataPushTable()) {
            TString url, host;
            auto key = TUrlKey::Create(urlDataPush.GetData().GetKey(), &url, &host);
            UNIT_ASSERT_C(key, "Failed to parse key from input row");

            // get push's url
            if (!urlRecord || urlRecord->GetUrl() != url) {
                if (urlRecord) {
                    // XXX(trofimenkov) Temporary hack
                    if (urlRecord->HasSitemapBasisState()) {
                        urlRecord->MutableSitemapBasisState()->Finalize();
                    }
                    result.MutableUrlDataTable()->Add()->CopyFrom(AsRowProto(*urlRecord));
                }
                auto urlData = GetUrlDataRow(url, testData);
                urlRecord = urlData
                    ? TryDeserialize(*urlData)
                    : TUrlRecord::TryCreate(url);
                UNIT_ASSERT(urlRecord);
            }

            // get push's host
            if (!hostRecord || hostRecord->GetHost() != host) {
                if (hostRecord) {
                    pusher->FinishHost(*hostRecord, tx);
                }
                auto hostData = GetHostDataRow(host, testData);
                hostRecord = hostData
                    ? TryDeserialize(*hostData)
                    : THostRecord::TryCreate(host);
                UNIT_ASSERT(hostRecord);
                pusher->StartHost(*hostRecord);
            }

            urlRecord->Bind(*hostRecord);

            pusher->Push(std::move(*urlDataPush.MutableData()), *urlRecord, *hostRecord, tx);
        }

        // finish host
        pusher->FinishHost(*hostRecord, tx);

        // XXX(trofimenkov) Temporary hack
        if (urlRecord->HasSitemapBasisState()) {
            urlRecord->MutableSitemapBasisState()->Finalize();
        }

        // save url data
        result.MutableUrlDataTable()->Add()->CopyFrom(AsRowProto(*urlRecord));

        CheckResult(output, result);
    }
};

#define SAMOVAR_URL_PUSHER_UNIT_TEST_SUITE(PUSHER)  \
    Y_UNIT_TEST_SUITE_IMPL(PUSHER##Test, TUrlPusherTestBase<PUSHER>)

#define SAMOVAR_URL_PUSHER_UNIT_TEST(N)                                                             \
    Y_UNIT_TEST(N) {                                                                           \
        TCurrentTest::RunTest(SAMOVAR_PUSHER_UNIT_TEST_IN(N), SAMOVAR_PUSHER_UNIT_TEST_OUT(N));     \
    }
