#pragma once

#include "host_record.h"
#include "test_transaction.h"
#include "worker_test_base.h"
#include "url_record.h"
#include "ut_common.h"

#include <robot/samovar/combustor/hooks/common/hook.h>
#include <robot/samovar/algo/misc/basetime.h>
#include <robot/samovar/algo/yt/transaction.h>
#include <robot/samovar/protos/ut.pb.h>

#include <google/protobuf/text_format.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/ptr.h>
#include <util/stream/file.h>

using namespace NSamovar;

template <typename TUrlHook>
class TUrlHookTestBase: public TSamovarWorkerTestBase {
public:
    // define specialization of this function
    // to create non-trivial url hooks
    template <typename THook>
    static THolder<NSamovar::IUrlHook> Create() {
        return MakeHolder<THook>("dummy");
    }

    static void RunTest(const TString& input, const TString& output) {
        auto hook = Create<TUrlHook>();

        NSamovarTest::TTestData testData = ReadTestData(input);
        UNIT_ASSERT_C(testData.UrlDataTableSize() > 0, "UrlRecordTable should not be empty");

        if (testData.HasTestTime()) {
            SetTestTime(testData.GetTestTime());
        }

        NSamovarTest::TTestData result;
        TTestTransaction tx(result);

        THostRecordPtr hostRecord;
        for (auto& urlDataRow : testData.GetUrlDataTable()) {
            auto urlRecord = TryDeserialize(urlDataRow);
            UNIT_ASSERT(urlRecord);

            TString url, host;
            auto key = TUrlKey::Create(urlRecord->GetUrl(), &url, &host);
            UNIT_ASSERT(key);

            // get url's host
            if (!hostRecord || hostRecord->GetHost() != host) {
                if (hostRecord) {
                    hook->FinishHost(*hostRecord, tx);
                }
                auto hostData = GetHostDataRow(host, testData);
                hostRecord = hostData
                    ? TryDeserialize(*hostData)
                    : THostRecord::TryCreate(host);
                UNIT_ASSERT(hostRecord);
                hook->StartHost(*hostRecord);
            }

            urlRecord->Bind(*hostRecord);

            hook->Hitch(*urlRecord, *hostRecord, tx);
            result.MutableUrlDataTable()->Add()->CopyFrom(AsRowProto(*urlRecord));
        }

        hook->FinishHost(*hostRecord, tx);


        CheckResult(output, result);
    }
};

#define SAMOVAR_URL_HOOK_UNIT_TEST_SUITE(HOOK)                          \
    Y_UNIT_TEST_SUITE_IMPL(HOOK##Test, TUrlHookTestBase<HOOK>)

#define SAMOVAR_URL_HOOK_UNIT_TEST(N)                                                           \
    Y_UNIT_TEST(N) {                                                                       \
        TCurrentTest::RunTest(SAMOVAR_HOOK_UNIT_TEST_IN(N), SAMOVAR_HOOK_UNIT_TEST_OUT(N));     \
    }
