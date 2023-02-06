#pragma once

#include "test_block_runner.h"
#include "test_request_context.h"

#include <library/cpp/logger/global/global.h>

#include <util/generic/vector.h>

namespace NJson {
    class TJsonValue;
}

namespace NMordaBlocks {
    class TTestBlockRunner;

    extern const std::function<void(const NJson::TJsonValue*)> DEFAULT_JSON_ASSERTER;

    int DoLatencyTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int iterationCount,
        const TTestRequestContext& request,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter);

    int DoLatencyTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int iterationCount,
        const TTestRequestContext& request,
        const TMap<TString, TString>& rawJsonBlocksSettings,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter);

    int DoThroughputTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int secondsCount,
        const TTestRequestContext& request,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter);


    int DoThroughputTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int secondsCount,
        const TTestRequestContext& request,
        const TMap<TString, TString>& rawJsonBlocksSettings,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter);

    class TPerfTestRunner : public TTestBlockRunner {
        void Start() override;
    };

} // namespace NMordaBlocks
