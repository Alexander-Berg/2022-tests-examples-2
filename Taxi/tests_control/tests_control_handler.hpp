#pragma once

#include <memory>
#include <mutex>
#include <vector>

#include <cache/cache_invalidator.hpp>
#include <component_util/named_component.hpp>
#include <components/async_pool.hpp>
#include <handler_util/base.hpp>
#include <utils/testsuite/test_point.hpp>
#include <workers/worker_executer.hpp>

class TestsControlHandler
    : public handlers::Base,
      public components::NamedComponentMixIn<TestsControlHandler> {
 public:
  static constexpr const char* const name = "tests-control";

  using handlers::Base::Base;

  void onLoad() override;
  void onUnload() override;

  void AddCacheInvalidator(const fastcgi::Component* owner,
                           const utils::CacheInvalidator& invalidator);
  void RemoveCacheInvalidator(const fastcgi::Component* owner);

  void AddWorkerExecuter(const std::string& worker_name,
                         const fastcgi::Component* owner,
                         const utils::WorkerExecuter& executer);
  void RemoveWorkerExecuter(const fastcgi::Component* owner);

  bool GetCacheUpdateDisabled() const { return cache_update_disabled_; }
  const std::string& GetMockserverUrl() const { return mockserver_url_; }

 protected:
  void HandleRequestThrow(fastcgi::Request& request,
                          ::handlers::BaseContext& context) override;

 private:
#ifdef MOCK_NOW
  struct Invalidator {
    const fastcgi::Component* owner;
    utils::CacheInvalidator handler;
  };

  std::vector<Invalidator> cache_invalidators_;

  struct Executer {
    const fastcgi::Component* owner;
    utils::WorkerExecuter handler;
  };

  std::unordered_map<std::string, Executer> worker_executers_;

  std::mutex mutex_;
#endif  // MOCK_NOW
  components::AsyncPool::CPtr async_;
  std::unique_ptr<utils::testsuite::TestPointControl> testpoint_control_;
  bool cache_update_disabled_ = false;
  std::string mockserver_url_;
};
