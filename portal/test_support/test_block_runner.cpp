#include "test_block_runner.h"

#include "json_test_utils.h"
#include "test_block_data_provider.h"
#include "test_geobase.h"
#include "test_statistics_collector.h"
#include "test_http_responder.h"

#include <portal/morda/blocks/common/block_base.h>
#include <portal/morda/blocks/common/block_input.h>
#include <portal/morda/blocks/core/config/config.h>
#include <portal/morda/blocks/core/core.h>
#include <portal/morda/blocks/core/session/session_tasks_sequence.h>
#include <portal/morda/blocks/environment/block_environment.h>
#include <portal/morda/blocks/tasks_sequence/thread_pool.h>
#include <portal/morda/blocks/test_resources/test_resource_wrappers.h>

#include <portal/morda/blocks/app_host_support/app_host_input_context.h>
#include <portal/morda/blocks/app_host_support/app_host_response_context.h>

#include <apphost/lib/service_testing/service_testing.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/gtest.h>
#include <library/cpp/testing/unittest/registar.h>

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
        };

        class TTestServer : public IServer {
        public:
            TTestServer() = default;
            ~TTestServer() override = default;

            void InitStats() override {
            }

            void RunLoop() override {
            }

            void AddPathWorker(TStringBuf path, IWorker* worker) override {
                if (path.EndsWith("/prepare_processor_formatter")) {
                    Worker_ = worker;
                    WorkerPath_ = TString(path);
                }
            }

            NThreading::TFuture<void> RunOnce(NAppHost::TServiceContextPtr context) {
                NThreading::TFuture<void> future;
                {
                    auto response = MakeIntrusive<TAppHostResponseContext>(context);
                    auto request = MakeIntrusiveConst<TAppHostInputContext>(context);
                    auto workSequence = MakeIntrusive<TSessionTasksSequence>();
                    workSequence->PostTask([this, request, response]() {
                        Worker_->InitSession(WorkerPath_, request);
                        TTasksSequence::Current()->PostTask([this, request, response]() {
                            Worker_->ProcessRequest(WorkerPath_, request, response);
                        });
                    });
                    future = response->GetFuture();
                }
                return future;
            }

        private:
            IWorker* Worker_ = nullptr;
            TString WorkerPath_;
        };
    } // namespace

    class TTestBlockRunner::TTestBlockEnvironment : public TBaseBlockEnvironment {
    public:
        using TBaseBlockEnvironment::RunBlocks;
        using TBaseBlockEnvironment::AddBlock;

        void SetupBlocks() override {
        }

        const TVector<std::unique_ptr<TBlockBase>>& Blocks() const {
            return Blocks_;
        }

        std::unique_ptr<IServer> MakeServer() override {
            TestServer_ = new TTestServer;
            return std::unique_ptr<IServer>(TestServer_);
        }

        NThreading::TFuture<void> RunOnce(NAppHost::TServiceContextPtr context) {
            return TestServer_->RunOnce(context);
        }

    private:
        TTestServer* TestServer_;
    };

    TTestBlockRunner::TTestBlockRunner()
        : TestCore_(std::make_unique<TTestCore>())
        , TestConfig_(std::make_unique<TTestConfig>())
        , TestDataProvider_(std::make_unique<NTest::TTestBlockDataProvider>())
        , TestGeoBase_(std::make_unique<TTestGeoBase>())
        , TestHttpResponder_(std::make_unique<TTestHttpResponder>())
    {
        TTestCore::SetGlobalCoreForTest(TestCore_.get());
        IBlockDataProvider::SetForTests(TestDataProvider_.get());
        IGeoBase::SetForTests(TestGeoBase_.get());

        TestStatisticsCollector_ = new TTestStatisticsCollector();
        IStatisticsCollector::Set(std::unique_ptr<TTestStatisticsCollector>(TestStatisticsCollector_));

        SetConfigFilePath("general", "translations_file_path",
            NTest::LOCAL_TEST_DATA_PATH / "Lang_auto.json");
        SetConfigFileData("general", "madm_holidays_file_path", "{}");
        SetConfigFileData("general", "networks_masks_file_path", "{}");
        SetConfigFileData("general", "auto_holidays_file_path", "{}");
        SetConfigFilePath("general", "app_packages_file_path",
            NTest::LOCAL_TEST_DATA_PATH / "application_package_v2.json");
        SetConfigFileData("general", "services_tabs_file_path", R"({"all":[]})");
        SetConfigFilePath("general", "services_v12_file_path", ToString(NTest::LOCAL_TEST_DATA_PATH / "services_v12_2.json"));
        SetConfigFileData("general", "runtime_settings_file_path", "{}");
        SetConfigFileData("general", "spok_settings_file_path", R"({"all":[]})");
        SetConfigValue("general", "tvm2_client_id", NJson::TJsonValue(123));
        SetConfigValue("general", "tvm2_self_secret", NJson::TJsonValue("fake secret"));
        SetConfigValue("general", "lang_detect_data_file_path",
                       TString(NTest::LOCAL_TEST_DATA_PATH / "lang_detect_data.txt"));
        SetConfigFileData("general", "supported_locales_file_path", R"({"all":[]})");
    }

    TTestBlockRunner::~TTestBlockRunner() {
        Environment_.reset();
        TConfig::SetForTests(nullptr);
        IBlockDataProvider::SetForTests(nullptr);
        IGeoBase::SetForTests(nullptr);
        IStatisticsCollector::Set(nullptr);
        TTestCore::SetGlobalCoreForTest(nullptr);
        TTestConfig::CleanRegisteredParamsForTest();
    }

    void TTestBlockRunner::AddBlock(std::unique_ptr<TBlockBase> block) {
        AddedBlockNames_.push_back(block->BlockName());
        Environment_->AddBlock(std::move(block));
    }

    void TTestBlockRunner::Start() {
        Environment_->Run();
    }

    void TTestBlockRunner::SetConfigValue(TStringBuf section, TStringBuf param,
                                          const NJson::TJsonValue& value) {
        TestConfig_->SetValue(section, param, value);
    }

    void TTestBlockRunner::SetConfigFilePath(TStringBuf section, TStringBuf param,
                                             const TFsPath& filePath) {
        SetConfigValue(section, param, NJson::TJsonValue(filePath));
        TestDataProvider_->LoadDataFromFile(TString(filePath), TString(filePath));
    }

    void TTestBlockRunner::SetConfigFileData(TStringBuf section, TStringBuf param, TString data) {
        const auto key = TString() + section + "_" + param;
        SetConfigValue(section, param, NJson::TJsonValue(key));
        TestDataProvider_->SetData(key, std::move(data));
    }

    void TTestBlockRunner::SetHttpOkResponse(TStringBuf httpResourceId, TString data) {
        TestHttpResponder_->AutoSendRepeatedlyOkData(TString(httpResourceId), data);
        AppHostHttpResponses_[TString(httpResourceId)] = data;
    }

    void TTestBlockRunner::InitEnvironment() {
        TConfig::SetForTests(TestConfig_.get());
        Environment_ = std::make_unique<TTestBlockEnvironment>();
        TVector<const char*> args;
        args.push_back("TTestBlockRunner");
        const TString threadCount = "thread_count=" + ToString(ThreadCount_);
        args.push_back(threadCount.c_str());
        Environment_->Init(static_cast<int>(args.size()), args.data());
    }

    void TTestBlockRunner::ProcessRequest(NAppHost::TServiceContextPtr context) {
        for (const auto& it : AppHostHttpResponses_) {
            TProcessorInput::THttpResponse response;
            response.SetStatusCode(200);
            response.SetContent(it.second);
            context->AddProtobufItem(response, TProcessorInput::MakeHttpResponseContextType(it.first));
        }
        NThreading::TFuture<void> future = Environment_->RunOnce(context);
        future.Wait();
    }

    const TVector<std::unique_ptr<TBlockBase>>& TTestBlockRunner::Blocks() const {
        return Environment_->Blocks();
    }

    void TTestBlockRunner::SetThreadCount(size_t threadCount) {
        Y_ASSERT(!TestCore_->IsStarted());
        ThreadCount_ = threadCount;
    }

} // namespace NMordaBlocks
