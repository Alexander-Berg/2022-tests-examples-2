#pragma once

#include "ut_common.h"

#include <robot/samovar/protos/schema.pb.h>
#include <robot/samovar/protos/ut.pb.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/string.h>

class TSamovarWorkerTestBase: public TSamovarTestBase {
protected:
    static NSamovarTest::TTestData ReadTestData(const TString& inputFileName);

    static void CheckResult(const TString& canonFileName, const NSamovarTest::TTestData& resultTables);

    static TMaybe<NSamovarTest::THostDataRow> GetHostDataRow(const TString& host, const NSamovarTest::TTestData& tables);
    static TMaybe<NSamovarTest::TUrlDataRow> GetUrlDataRow(const TString& url, const NSamovarTest::TTestData& tables);

private:
    static bool ShouldCanonizeResult();
    static void WriteTables(const NSamovarTest::TTestData& tables, const TString& outputFileName);
};


#define SAMOVAR_UNIT_TEST_IN(N) \
    "data/" + TCurrentTest::StaticName() + ".Test"#N".in"

#define SAMOVAR_UNIT_TEST_OUT(N) \
    "data/" + TCurrentTest::StaticName() + ".Test"#N".out"

#define SAMOVAR_PUSHER_UNIT_TEST_IN(N) \
    "data/pushers/" + TCurrentTest::StaticName() + ".Test"#N".in"

#define SAMOVAR_PUSHER_UNIT_TEST_OUT(N) \
    "data/pushers/" + TCurrentTest::StaticName() + ".Test"#N".out"


#define SAMOVAR_HYPER_UNIT_TEST_IN(N) \
    "data/hyper/" + TCurrentTest::StaticName() + ".Test"#N".in"

#define SAMOVAR_HYPER_UNIT_TEST_OUT(N) \
    "data/hyper/" + TCurrentTest::StaticName() + ".Test"#N".out"


#define SAMOVAR_HOOK_UNIT_TEST_IN(N) \
    "data/hooks/" + TCurrentTest::StaticName() + ".Test"#N".in"

#define SAMOVAR_HOOK_UNIT_TEST_OUT(N) \
    "data/hooks/" + TCurrentTest::StaticName() + ".Test"#N".out"

