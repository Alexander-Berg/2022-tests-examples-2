#include "test_with_core.h"

#include "test_statistics_collector.h"
#include "test_http_responder.h"
#include "test_request_context.h"

#include <portal/morda/blocks/core/config/config.h>
#include <portal/morda/blocks/core/core.h>
#include <portal/morda/blocks/core/session/session.h>
#include <portal/morda/blocks/core/session/session_tasks_sequence.h>

#include <utility>

namespace NMordaBlocks {
    namespace {

        class TTestCore : public TCore {
        public:
            TTestCore() {
                SetReplaceSystemThreadPool(false);
            }
            using TCore::SetGlobalCoreForTest;
        };

        class TTestConfig : public TConfig {
        public:
            using TConfig::TConfig;
            using TConfig::CleanRegisteredParamsForTest;
            using TConfig::SetValue;
        };

    } // namespace

    TTestWithCoreBase::TTestWithCoreBase()
        : TestCore_(std::make_unique<TTestCore>())
        , TestConfig_(std::make_unique<TTestConfig>()) {
        TTestCore::SetGlobalCoreForTest(TestCore_.get());
    }

    TTestWithCoreBase::~TTestWithCoreBase() {
        StopCore();
        TTestCore::SetGlobalCoreForTest(nullptr);
        TTestConfig::CleanRegisteredParamsForTest();
    }

    void TTestWithCoreBase::SetUp() {
    }

    void TTestWithCoreBase::TearDown() {
    }

    void TTestWithCoreBase::StopCore() {
        if (TestCore_->IsStarted()) {
            TestCore_->Stop();
        }
    }

    TTestWithCore::TTestWithCore()
        : TestHttpResponder_(std::make_unique<TTestHttpResponder>()) {
    }

    TTestWithCore::~TTestWithCore() {
        TConfig::SetForTests(nullptr);
    }

    void TTestWithCore::SetUp() {
        TTestWithCoreBase::SetUp();
        if (!TCore::Get()->IsStarted()) {
            CreateServices();
            TConfig::SetForTests(GetTestConfig());
            TCore::Get()->Start(1);
        }
        TasksRunner_ = std::make_unique<TScopedTasksSequenceRunner<TSessionTasksSequence>>();
        TestHttpResponder_->SetTsRunner(TasksRunner_.get());
        ResetRequestContextToDefault();

        TestStatisticsCollector_ = new TTestStatisticsCollector();
        IStatisticsCollector::Set(std::unique_ptr<TTestStatisticsCollector>(TestStatisticsCollector_));
    }

    void TTestWithCore::ResetRequestContextToDefault() {
        TestRequestContext_ = MakeIntrusive<TTestRequestContext>();
        TRequestContext::SetCurrent(TestRequestContext_.Get());
    }

    void TTestWithCore::RunPendingTasks() {
        TasksRunner_->RunPendingTasks();
    }

    void TTestWithCore::TearDown() {
        TestStatisticsCollector_ = nullptr;
        IStatisticsCollector::Set(nullptr);
        TestRequestContext_.Reset();
        TestHttpResponder_->SetTsRunner(nullptr);
        TasksRunner_.reset();
        TTestWithCoreBase::TearDown();
    }

    TUserAgent& TTestWithCore::GetTestUserAgent() {
        return GetTestRequestContext()->GetTestUserAgent();
    }

    void TTestWithCore::CreateServices() {
    }

} // namespace NMordaBlocks
