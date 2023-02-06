#pragma once

#include <library/cpp/testing/unittest/gtest.h>

#include <memory>

namespace NMordaBlocks {
    class TCore;
    class TSession;
    class TConfig;
    class TTestRequestContext;
    class TUserAgent;
    class TTestStatisticsCollector;
    class TScopedTasksSequenceRunnerBase;
    class TTestHttpResponder;

    class TTestWithCoreBase : public ::testing::Test {
    public:
        TTestWithCoreBase();

        virtual ~TTestWithCoreBase();

        void SetUp() override;

        void TearDown() override;

        TConfig* GetTestConfig() {
            return TestConfig_.get();
        }

        const TConfig* GetTestConfig() const {
            return TestConfig_.get();
        }

        void StopCore();

     private:
        std::unique_ptr<TCore> TestCore_;
        std::unique_ptr<TConfig> TestConfig_;
    };

    class TTestWithCore : public TTestWithCoreBase {
    public:
        TTestWithCore();

        virtual ~TTestWithCore();

        virtual void CreateServices();

        void SetUp() override;

        void TearDown() override;

        // Created at SetUp. Destroyed at TearDown,
        TTestRequestContext* GetTestRequestContext() {
            return TestRequestContext_.Get();
        }

        TUserAgent& GetTestUserAgent();

        void ResetRequestContextToDefault();

        TTestStatisticsCollector* GetTestStatisticsCollector() const {
            return TestStatisticsCollector_;
        }

        TScopedTasksSequenceRunnerBase* GetTestTasksRunner() {
            return TasksRunner_.get();
        }

        void RunPendingTasks();

        TTestHttpResponder* GetTestHttpResponder() {
            return TestHttpResponder_.get();
        }

    private:
        std::unique_ptr<TTestHttpResponder> TestHttpResponder_;
        std::unique_ptr<TScopedTasksSequenceRunnerBase> TasksRunner_;
        TIntrusivePtr<TTestRequestContext> TestRequestContext_;
        TTestStatisticsCollector* TestStatisticsCollector_ = nullptr;
    };

} // namespace NMordaBlocks
