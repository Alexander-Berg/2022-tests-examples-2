#include "worker_test_base.h"
#include "host_record.h"

#include <robot/samovar/algo/locator/locator.h>
#include <robot/samovar/protos/schema.pb.h>
#include <robot/samovar/protos/ut.pb.h>

#include <google/protobuf/text_format.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/string.h>
#include <util/stream/file.h>
#include <util/string/type.h>
#include <util/system/env.h>

using namespace NSamovar;

namespace {
    // Verifies that binary key in row matches its string key.
    // If binary key is missing then adds it.
    template <typename TKey, typename TRow>
    void SetKeyIfNeed(TRow& row, TStringBuf stringKey) {
        auto key = TKey::Create(stringKey);
        UNIT_ASSERT(key);
        TKey originalKey;
        originalKey.FromProto(row);
        if (originalKey != TKey()) {
            UNIT_ASSERT_EQUAL(originalKey, *key);
        } else {
            key->ToProto(row);
        }
    }
}

NSamovarTest::TTestData TSamovarWorkerTestBase::ReadTestData(const TString& inputFileName) {
    TIFStream in(inputFileName);

    NSamovarTest::TTestData tables;
    if (!google::protobuf::TextFormat::ParseFromString(in.ReadAll(), &tables)) {
        UNIT_FAIL(Sprintf("Can't load protobuf from: %s", inputFileName.data()));
    }

    for (auto& urlDataRow : *tables.MutableUrlDataTable()) {
        SetKeyIfNeed<TUrlKey>(urlDataRow, urlDataRow.GetData().GetUrl());
    }

    for (auto& hostDataRow : *tables.MutableHostDataTable()) {
        auto rec = TryDeserialize(hostDataRow);
        SetKeyIfNeed<THostKey>(hostDataRow, rec->GetHost());
    }

    for (auto& urlDataPushRow : *tables.MutableUrlDataPushTable()) {
        SetKeyIfNeed<TUrlKey>(urlDataPushRow, urlDataPushRow.GetData().GetKey());
    }

    for (auto& hostDataPushRow : *tables.MutableHostDataPushTable()) {
        SetKeyIfNeed<THostKey>(hostDataPushRow, hostDataPushRow.GetData().GetKey());
    }

    return tables;
}

void TSamovarWorkerTestBase::CheckResult(const TString& canonFileName, const NSamovarTest::TTestData& resultTables) {
    if (ShouldCanonizeResult()) {
        WriteTables(resultTables, canonFileName);
        return;
    }

    auto canonicalTables = ReadTestData(canonFileName);
    UNIT_ASSERT_NO_DIFF(canonicalTables.DebugString(), resultTables.DebugString());
}

bool TSamovarWorkerTestBase::ShouldCanonizeResult() {
    return IsTrue(GetEnv("ENV_SAMOVAR_CANONIZE_TEST"));
}

void TSamovarWorkerTestBase::WriteTables(const NSamovarTest::TTestData& tables, const TString& outputFileName) {
    TString data;
    if (!::google::protobuf::TextFormat::PrintToString(tables, &data)) {
        UNIT_FAIL(Sprintf("Can't save protobuf to: %s", outputFileName.data()));
    }

    TOFStream out(outputFileName);
    out.Write(data.data(), data.size());
}

TMaybe<NSamovarTest::THostDataRow> TSamovarWorkerTestBase::GetHostDataRow(const TString& host, const NSamovarTest::TTestData& tables) {
    for (auto& row : tables.GetHostDataTable()) {
        if (host == row.GetData().GetHost()) {
            return row;
        }
    }

    return Nothing();
}

TMaybe<NSamovarTest::TUrlDataRow> TSamovarWorkerTestBase::GetUrlDataRow(const TString& url, const NSamovarTest::TTestData& tables) {
    for (auto& row : tables.GetUrlDataTable()) {
        if (url == row.GetData().GetUrl()) {
            return row;
        }
    }

    return Nothing();
}
