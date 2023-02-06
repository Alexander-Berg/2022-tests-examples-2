#include "perf_helpers.h"

#include "test_block_runner.h"

#include <portal/morda/blocks/common/block_base.h>
#include <portal/morda/blocks/contexts/request_context_fields.h>
#include <portal/morda/blocks/contexts/request_context_impl.h>
#include <portal/morda/blocks/test_support/json_test_utils.h>

#include <apphost/lib/service_testing/service_testing.h>

#include <library/cpp/json/writer/json_value.h>
#include <library/cpp/testing/unittest/gtest.h>

#include <util/datetime/cputimer.h>
#include <util/generic/yexception.h>
#include <util/stream/str.h>
#include <util/system/thread.h>

#include <iostream>

using NAppHost::NService::TTestContext;

namespace NMordaBlocks {
    namespace {
        class TNoLogsFormatter {
        public:
            static TString AssertNoLogs(ELogPriority /*priority*/, TStringBuf /*data*/) {
                EXPECT_FALSE(true); // no logs expected
                return {};
            }

        private:
            TNoLogsFormatter() = default;
            ~TNoLogsFormatter() = default;
        };

        class TLatencyTestThread : public TThread {
        public:
            TLatencyTestThread(
                TTestBlockRunner* runner,
                int iterationsCount,
                const TTestRequestContext& request,
                const TMap<TString, TString>& rawJsonBlocksSettings,
                const std::function<void(const NJson::TJsonValue*)>& jsonAsserter)
                : TThread(&TLatencyTestThread::SThreadProc, this)
                , Runner_(runner)
                , IterationsCount_(iterationsCount)
                , JsonAsserter_(jsonAsserter) {
                JsonData_ = request.MakeLegacyJson();
                Proto_ = request.MakeProto();
                for (const auto& it : rawJsonBlocksSettings) {
                    JsonBlocksSettings_[it.first] = NTest::ReadJsonFromString(it.second);
                }
            }

            int Latency() const {
                return Latency_;
            }

        private:
            static void* SThreadProc(void* pthis) {
                static_cast<TLatencyTestThread*>(pthis)->ThreadProc();
                return nullptr;
            }

            void ThreadProc() {
                const TInstant start = TInstant::Now();
                for (int i = 0; i < IterationsCount_; ++i) {
                    auto context = MakeIntrusive<TTestContext>(NJson::JSON_ARRAY);
                    context->AddItem(NJson::TJsonValue(JsonData_), REQUEST_SECTION_NAME_LEGACY);
                    context->AddProtobufItem(Proto_, REQUEST_CONTEXT_PROTO_APPHOST_CTX_TYPE);
                    for(const auto&it:JsonBlocksSettings_) {
                        context->AddItem(NJson::TJsonValue(it.second), TString("block_settings_" + it.first));
                    }
                    Runner_->ProcessRequest(context);

                    for (const TString& blockName : Runner_->AddedBlockNames())
                        JsonAsserter_(context->FindFirstItem(blockName + "_formatted"));
                }
                const TInstant end = TInstant::Now();
                Latency_ = static_cast<int>((end - start).MicroSeconds() / IterationsCount_);
            }

        private:
            TTestBlockRunner* Runner_;
            const int IterationsCount_;
            int Latency_ = 0;
            const std::function<void(const NJson::TJsonValue*)>& JsonAsserter_;
            NJson::TJsonValue JsonData_;
            TRequestContextProto Proto_;
            TMap<TString, NJson::TJsonValue> JsonBlocksSettings_;
        };

        class TThroughputTestThread : public TThread {
        public:
            TThroughputTestThread(
                TTestBlockRunner* runner,
                int secondsCount,
                const TTestRequestContext& request,
                const TMap<TString, TString>& rawJsonBlocksSettings,
                const std::function<void(const NJson::TJsonValue*)>& jsonAsserter)
                : TThread(&TThroughputTestThread::SThreadProc, this)
                , Runner_(runner)
                , SecondsCount_(secondsCount)
                , JsonAsserter_(jsonAsserter) {
                JsonData_ = request.MakeLegacyJson();
                Proto_ = request.MakeProto();
                for (const auto& it : rawJsonBlocksSettings) {
                    JsonBlocksSettings_[it.first] = NTest::ReadJsonFromString(it.second);
                }
            }

            int Throughput() const {
                return Throughput_;
            }

        private:
            static void* SThreadProc(void* pthis) {
                static_cast<TThroughputTestThread*>(pthis)->ThreadProc();
                return nullptr;
            }

            void ThreadProc() {
                const TInstant start = TInstant::Now();
                int iterationCount = 0;
                while (static_cast<int>((TInstant::Now() - start).Seconds()) < SecondsCount_) {
                    auto context = MakeIntrusive<TTestContext>(NJson::JSON_ARRAY);
                    context->AddItem(NJson::TJsonValue(JsonData_), REQUEST_SECTION_NAME_LEGACY);
                    context->AddProtobufItem(Proto_, REQUEST_CONTEXT_PROTO_APPHOST_CTX_TYPE);
                    for (const auto& it : JsonBlocksSettings_) {
                        context->AddItem(NJson::TJsonValue(it.second), TString("block_settings_" + it.first));
                    }
                    Runner_->ProcessRequest(context);

                    for (const TString& blockName : Runner_->AddedBlockNames())
                        JsonAsserter_(context->FindFirstItem(blockName + "_formatted"));

                    ++iterationCount;
                }
                Throughput_ = iterationCount / SecondsCount_;
            }

        private:
            TTestBlockRunner* Runner_;
            const int SecondsCount_;
            int Throughput_ = 0;
            const std::function<void(const NJson::TJsonValue*)>& JsonAsserter_;
            NJson::TJsonValue JsonData_;
            TRequestContextProto Proto_;
            TMap<TString, NJson::TJsonValue> JsonBlocksSettings_;
        };
    }

    const std::function<void(const NJson::TJsonValue*)> DEFAULT_JSON_ASSERTER =
        [](const NJson::TJsonValue* json)
    {
        EXPECT_TRUE(json);
        EXPECT_TRUE(json->Has("show"));
        EXPECT_TRUE((*json)["show"].GetBooleanRobust());
    };

    int DoLatencyTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int iterationCount,
        const TTestRequestContext& request,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter
    ) {
        return DoLatencyTest(std::move(runner), iterationCount,
                             request, {}, jsonAsserter);
    }

    int DoLatencyTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int iterationCount,
        const TTestRequestContext& request,
        const TMap<TString, TString>& rawJsonBlocksSettings,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter
    ) {
        runner->Start();
        TVector<std::unique_ptr<TLatencyTestThread>> threads(runner->ThreadCount());
        for (auto& it : threads) {
            it = std::make_unique<TLatencyTestThread>(runner.get(), iterationCount, request, rawJsonBlocksSettings, jsonAsserter);
        }
        for (auto& it : threads) {
            it->Start();
        }
        for (auto& it : threads) {
            it->Join();
        }
        int avgLatency = 0;
        for (const auto& it : threads) {
            avgLatency += it->Latency();
        }
        avgLatency /= static_cast<int>(threads.size());
        Cout << "avg latency(us) " << avgLatency << " " << Endl;
        return avgLatency;
    }

    int DoThroughputTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int secondsCount,
        const TTestRequestContext& request,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter) {
        return DoThroughputTest(std::move(runner), secondsCount,
                                request, {}, jsonAsserter);
    }

    int DoThroughputTest(
        std::unique_ptr<TTestBlockRunner> runner,
        int secondsCount,
        const TTestRequestContext& request,
        const TMap<TString, TString>& rawJsonBlocksSettings,
        const std::function<void(const NJson::TJsonValue*)>& jsonAsserter
    ) {
        runner->Start();
        TVector<std::unique_ptr<TThroughputTestThread>> threads(runner->ThreadCount());
        for (auto& it : threads) {
            it = std::make_unique<TThroughputTestThread>(runner.get(), secondsCount, request, rawJsonBlocksSettings, jsonAsserter);
        }
        for (auto& it : threads) {
            it->Start();
        }
        for (auto& it : threads) {
            it->Join();
        }
        int throughput = 0;
        for (const auto& it : threads) {
            throughput += it->Throughput();
        }
        Cout << "throughput(rps) " << throughput << " " << Endl;
        return throughput;
    }

    void TPerfTestRunner::Start() {
        TLoggerOperator<TGlobalLog>::Log().SetFormatter(&TNoLogsFormatter::AssertNoLogs);
        TTestBlockRunner::Start();
    }

} // namespace NMordaBlocks
