#pragma once

#include <robot/samovar/boiler/hyperworkers/common/hyperworker.h>
#include <robot/samovar/ut/lib/worker_test_base.h>

#include <library/cpp/testing/unittest/registar.h>

namespace NSamovarTest {
    void RunHyperWorkerTest(
        const TString& input,
        const TString& expected,
        std::function<NSamovar::THyperWorkerPtr()>
    );
}

#define SAMOVAR_HYPERWORKER_UNIT_TEST_SUITE_IMPL(cls, func, ...) \
    struct cls: public TSamovarWorkerTestBase { \
        static ::NSamovar::THyperWorkerPtr CreateWorker() { \
            return func(__VA_ARGS__); \
        } \
        static void RunTest(const TString& input, const TString& expected) { \
            ::NSamovarTest::RunHyperWorkerTest(input, expected, &CreateWorker); \
        } \
    }; \
    Y_UNIT_TEST_SUITE_IMPL(cls, cls)

#define SAMOVAR_HYPERWORKER_UNIT_TEST_SUITE(func, ...) \
    SAMOVAR_HYPERWORKER_UNIT_TEST_SUITE_IMPL(T##func, func, ##__VA_ARGS__)

#define SAMOVAR_HYPERWORKER_UNIT_TEST(name)                                                           \
    Y_UNIT_TEST(name) {                                                                          \
        TCurrentTest::RunTest(SAMOVAR_HYPER_UNIT_TEST_IN(name), SAMOVAR_HYPER_UNIT_TEST_OUT(name));   \
    }
