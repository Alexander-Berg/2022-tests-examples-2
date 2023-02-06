#pragma once

#include "host_record.h"
#include "test_transaction.h"
#include "worker_test_base.h"
#include "ut_common.h"

#include <robot/samovar/combustor/pushers/common/pusher.h>
#include <robot/samovar/algo/locator/locator.h>
#include <robot/samovar/algo/misc/basetime.h>
#include <robot/samovar/algo/yt/transaction.h>
#include <robot/samovar/protos/ut.pb.h>

#include <google/protobuf/text_format.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/ptr.h>
#include <util/stream/file.h>

using namespace NSamovar;

template <typename THostPusher>
class THostPusherTestBase: public TSamovarWorkerTestBase {
public:
    // define specialization of this function
    // to create non-trivial host pushers
    template <typename TPusher>
    static THolder<NSamovar::IHostPusher> Create() {
        return MakeHolder<TPusher>("dummy");
    }

    static void RunTest(const TString& input, const TString& output) {
        auto pusher = Create<THostPusher>();

        NSamovarTest::TTestData testData = ReadTestData(input);
        UNIT_ASSERT_C(testData.HostDataPushTableSize() > 0, "HostDataPushTable should not be empty");

        if (testData.HasTestTime()) {
            SetTestTime(testData.GetTestTime());
        }

        NSamovarTest::TTestData result;
        TTestTransaction tx(result);

        THostRecordPtr hostRecord;
        for (auto& hostRecordPush : *testData.MutableHostDataPushTable()) {
            TString host;
            auto key = THostKey::Create(hostRecordPush.GetData().GetKey(), &host);
            UNIT_ASSERT(key);

            // get push's host
            TMaybe<NSamovarTest::THostDataRow> newHostData = GetHostDataRow(host, testData);
            UNIT_ASSERT_C(newHostData, Sprintf("No host data found for host: %s", host.data()));
            auto newHostRecord = TryDeserialize(*newHostData);
            UNIT_ASSERT(newHostRecord);

            if (hostRecord && hostRecord->GetHost() != newHostRecord->GetHost()) {
                // save previous host data
                result.MutableHostDataTable()->Add()->CopyFrom(AsRowProto(*hostRecord));
            }

            hostRecord = std::move(newHostRecord);

            pusher->Push(std::move(*hostRecordPush.MutableData()), *hostRecord, tx);
        }

        // save host data
        result.MutableHostDataTable()->Add()->CopyFrom(AsRowProto(*hostRecord));

        CheckResult(output, result);
    }
};

#define SAMOVAR_HOST_PUSHER_UNIT_TEST_SUITE(PUSHER)  \
    Y_UNIT_TEST_SUITE_IMPL(PUSHER##Test, THostPusherTestBase<PUSHER>)

#define SAMOVAR_HOST_PUSHER_UNIT_TEST(N)                                                            \
    Y_UNIT_TEST(N) {                                                                           \
        TCurrentTest::RunTest(SAMOVAR_PUSHER_UNIT_TEST_IN(N), SAMOVAR_PUSHER_UNIT_TEST_OUT(N));     \
    }
