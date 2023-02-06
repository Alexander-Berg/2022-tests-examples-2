#include "test_transaction.h"

#include <robot/samovar/algo/locator/locator.h>
#include <robot/samovar/algo/record/host_record.h>
#include <robot/samovar/algo/record/url_record.h>
#include <robot/samovar/algo/misc/basetime.h>
#include <robot/samovar/algo/misc/guid.h>
#include <robot/samovar/algo/misc/random.h>
#include <robot/samovar/algo/yt/transaction.h>
#include <robot/samovar/protos/ut.pb.h>

#include <util/datetime/base.h>

TTestTransaction::TTestTransaction(NSamovarTest::TTestData& result)
    : Result(result)
{}

void TTestTransaction::WritePush(NSamovarData::TPushData&& pushData) {
    auto pushAgent = NSamovarData::EPushType_descriptor()->FindValueByNumber(pushData.GetPushType())->options().GetExtension(NSamovarData::PushAgent);
    switch (pushAgent) {
        case NSamovarData::PA_HOST:
            return WriteHostPushData(std::move(pushData));
        case NSamovarData::PA_URL:
            return WriteUrlPushData(std::move(pushData));
        default:
            UNIT_FAIL("Unknown push agent");
    }
}

void TTestTransaction::WriteDelayedPush(TDuration delay, NSamovarData::TPushData&& pushData) {
    WriteDelayedPush(NSamovar::GetNow() + delay, std::move(pushData));
}

void TTestTransaction::WriteDelayedPush(TInstant readyTime, NSamovarData::TPushData&& pushData) {
    NSamovarSchema::TDelayedPushRow pushRow;

    // set key
    const auto pushAgent = NSamovarData::EPushType_descriptor()->FindValueByNumber(pushData.GetPushType())->options().GetExtension(NSamovarData::PushAgent);
    if (pushAgent == NSamovarData::PA_HOST) {
        auto key = NSamovar::THostKey::Create(pushData.GetKey());
        Y_VERIFY(key, "TPushWriter::WriteDelayedPush can't parse key Type %u Host %s", (ui32)pushData.GetPushType(), pushData.GetKey().data());

        key->ToProto(pushRow);
    } else if (pushAgent == NSamovarData::PA_URL) {
        auto key = NSamovar::TUrlKey::Create(pushData.GetKey());
        Y_VERIFY(key, "TPushWriter::WriteDelayedPush can't parse key Type %u Url %s", (ui32)pushData.GetPushType(), pushData.GetKey().data());

        key->ToProto(pushRow);
    } else {
        ythrow yexception() << "Unknown push agent: " << static_cast<int>(pushAgent);
    }

    pushRow.MutableData()->Swap(&pushData);
    pushRow.SetShard(0);
    pushRow.SetTimestamp(0);
    pushRow.SetUniqId(NSamovar::GetGuidAsUi64());
    pushRow.SetReadyTime(readyTime.Seconds());

    Result.MutableDelayedPushTable()->Add()->CopyFrom(pushRow);
}

void TTestTransaction::WriteCrawlQueueCandidate(const NCrawl::TEjectorCandidate& candidate, const NCrawl::TCrawlSettings& settings) {
    auto row = Result.MutableCrawlQueueTable()->Add();
    row->MutableCandidate()->CopyFrom(candidate);
    row->MutableSettings()->CopyFrom(settings);
}

void TTestTransaction::WriteCrawlForwardingPush(const NSamovarData::TPushData&) {
    Y_FAIL();
}

void TTestTransaction::WriteUrlPushData(NSamovarData::TPushData&& pushData) {
    auto key = NSamovar::TUrlKey::Create(pushData.GetKey());
    if (!key) {
        return;
    }

    // set push row
    NSamovarSchema::TUrlDataPushRow pushRow;
    pushRow.MutableData()->Swap(&pushData);
    key->ToProto(pushRow);
    pushRow.SetTimestamp(0);

    Result.MutableUrlDataPushTable()->Add()->CopyFrom(pushRow);
}

void TTestTransaction::WriteHostPushData(NSamovarData::TPushData&& pushData) {
    auto key = NSamovar::THostKey::Create(pushData.GetKey());
    if (!key) {
        return;
    }

    NSamovarSchema::THostDataPushRow hostDataPushRow;
    hostDataPushRow.MutableData()->Swap(&pushData);
    key->ToProto(hostDataPushRow);
    hostDataPushRow.SetTimestamp(0);

    Result.MutableHostDataPushTable()->Add()->CopyFrom(hostDataPushRow);
}

void TTestTransaction::RemoveCurrentUrlRecord() {
    CurrentUrlRecordRemoved = true;
}

void TTestTransaction::WriteExportRaw(const TString&, const TString&, const TString&) {
    Y_FAIL();
}

void TTestTransaction::WriteLbExportPush(const TString&, TString&&) {
    Y_FAIL();
}

void TTestTransaction::WriteLbExportPush(NSamovarSchema::TLbPushRow&&) {
    Y_FAIL();
}
