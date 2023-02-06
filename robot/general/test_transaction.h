#pragma once

#include "ut_common.h"

#include <robot/samovar/algo/record/host_record.h>
#include <robot/samovar/algo/record/url_record.h>
#include <robot/samovar/algo/yt/transaction.h>

#include <robot/samovar/protos/schema.pb.h>
#include <robot/samovar/protos/ut.pb.h>
#include <robot/protos/crawl/candidate.pb.h>

#include <util/datetime/base.h>

class TTestTransaction: public NSamovar::ITransaction {
public:
    TTestTransaction() = delete;

    explicit TTestTransaction(NSamovarTest::TTestData& result);

    virtual void WritePush(NSamovarData::TPushData&& pushData) override;
    virtual void WriteDelayedPush(TDuration delay, NSamovarData::TPushData&& data) override;
    virtual void WriteDelayedPush(TInstant readyTime, NSamovarData::TPushData&& data) override;

    virtual void WriteCrawlQueueCandidate(const NCrawl::TEjectorCandidate& candidate,const NCrawl::TCrawlSettings& settings) override;
    virtual void WriteCrawlForwardingPush(const NSamovarData::TPushData& data) override;
    virtual void RemoveCurrentUrlRecord() override;
    virtual void WriteExportRaw(const TString& target, const TString& format, const TString& data) override;
    virtual void WriteLbExportPush(const TString& exportName, TString&& data) override;
    virtual void WriteLbExportPush(NSamovarSchema::TLbPushRow&& row) override;

private:
    void WriteUrlPushData(NSamovarData::TPushData&& pushData);
    void WriteHostPushData(NSamovarData::TPushData&& pushData);

public:
    bool CurrentUrlRecordRemoved = false;

private:
    NSamovarTest::TTestData& Result;
};
