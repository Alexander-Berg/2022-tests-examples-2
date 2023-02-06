#include <agl/core/dynamic_config.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/sourcing/resources-storage.hpp>
#include <agl/sourcing/sources-polling-state.hpp>
#include <agl/sourcing/userver-http-client.hpp>
#include <sourcing/dependencies.hpp>
#include <sourcing/fallback.hpp>
#include <sourcing/sequencer.hpp>
#include <sourcing/source.hpp>

#include <clients/http.hpp>
#include <clients/statistics.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/storages/secdist/secdist.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace agl::sourcing::tests {

namespace {

class MockSourceStorage : public SourceStorage {
 public:
  MockSourceStorage() {
    source_.name_ = "source_name";
    source_.resource_ = "source_resource";
    source_.enabled_ = true;
    source_.fail_policy_.EmplaceBack(
        FailPolicy::Filter(),
        FailPolicy::Action(FailPolicy::Action::Kind::IGNORE));
  }

  const Source& GetSource(const size_t) const override { return source_; }

 private:
  Source source_;
};

class MockStatClient : public clients::StatisticsReachInterface {
 public:
  void Send(const std::string& /*metric*/, unsigned /*value*/) const noexcept {}
  bool FallbackFired(const std::string& /*fallback*/) const noexcept {
    return false;
  }
  unsigned GetMetric(const std::string& /*metric*/) const noexcept { return 0; }
};

class MockTvmClient : public tvm2::ClientContext {
 public:
  MockTvmClient(std::shared_ptr<clients::http::Client>& http_client)
      : tvm2::ClientContext(*http_client), client_(http_client) {}

  virtual tvm2::models::ServiceId GetServiceIdByServiceName(
      const std::string& /*service_name*/) const override {
    return 0;
  }

  virtual bool CheckCanSignRequestForSource(
      const tvm2::models::ServiceName& /*src_service_name*/) const override {
    return true;
  }

  virtual std::shared_ptr<clients::http::Request> CreateSignedRequest(
      tvm2::models::ServiceId /*dest_service_id*/) override {
    return nullptr;
  }

  virtual std::shared_ptr<clients::http::Request> CreateSignedRequestForSource(
      tvm2::models::ServiceId /*src_service_id*/,
      tvm2::models::ServiceId /*dst_service_id*/) override {
    return nullptr;
  }

 private:
  std::shared_ptr<clients::http::Client> client_;
};

}  // namespace

class ResourcesProcessedCallbackHolderImpl
    : public ResourcesProcessedCallbackHolder {
 public:
  ResourcesProcessedCallbackHolderImpl(engine::SingleConsumerEvent& event)
      : event_(event) {}

  void Call() override { event_.Send(); }

 private:
  engine::SingleConsumerEvent& event_;
};

UTEST(TestSequencer, TestTaskCancel) {
  engine::SingleConsumerEvent event;
  auto task = utils::Async("test_task_cancel", [&event] {
    Sequencer::ExecutionQueue execution_queue = {0};
    Dependencies deps;
    MockSourceStorage source_storage;
    FallbackStorage fallback_storage;
    SourcesPollingState src_polling_state;

    core::ExecuterState executer_state;

    MockStatClient stat_client;
    executer_state.RegisterBinding(
        static_cast<clients::StatisticsReachInterface&>(stat_client));

    Resource resource;
    resource.url = ResourceUrl("http://foo/bar");
    resource.method = clients::http::HttpMethod::kGet;
    resource.timeout = 1000;
    resource.max_retries = 2;

    ResourcesStorage resources_storage;
    resources_storage.Insert("source_resource", resource);
    executer_state.RegisterBinding(resources_storage);

    std::shared_ptr<clients::http::Client> http_client_ptr =
        utest::CreateHttpClient();
    MockTvmClient mock_tvm_client(http_client_ptr);
    UserverHttpClient userver_http_client{mock_tvm_client};
    agl::sourcing::HttpClient& http_client = userver_http_client;

    executer_state.RegisterBinding(http_client);

    Sequencer seq(execution_queue, {}, deps, {}, source_storage, {},
                  fallback_storage, src_polling_state, executer_state);
    EXPECT_THROW(
        seq.TestRun(
            std::make_unique<ResourcesProcessedCallbackHolderImpl>(event)),
        std::runtime_error);
  });

  EXPECT_TRUE(event.WaitForEvent());
  task.SyncCancel();
}

}  // namespace agl::sourcing::tests
