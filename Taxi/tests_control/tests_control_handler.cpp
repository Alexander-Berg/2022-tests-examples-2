#include "tests_control_handler.hpp"

#include <chrono>
#include <cstdlib>

#include <fastcgi2/config.h>
#include <fastcgi2/request.h>

#include <handler_util/errors.hpp>
#include <logging/logger.hpp>
#include <utils/datetime.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include <utils/mock_now.hpp>
#include <utils/testsuite/testsuite.hpp>

void TestsControlHandler::onLoad() {
  handlers::Base::onLoad();
  async_.Accept(context());

  const fastcgi::Config& xml_config = *context()->getConfig();
  const std::string& component_xpath = context()->getComponentXPath();

  mockserver_url_ =
      xml_config.asString(component_xpath + "/mockserver_url", "");
  if (!mockserver_url_.empty()) {
    LOG_INFO() << "[testsuite] Mockserver url " << mockserver_url_;
    utils::testsuite::SetMockserverUrl(mockserver_url_);
  }

  const std::string testpoint_url =
      xml_config.asString(component_xpath + "/testpoint_url", "");
  const int testpoint_timeout =
      xml_config.asInt(component_xpath + "/testpoint_timeout_ms", 0);
  testpoint_control_ = std::make_unique<utils::testsuite::TestPointControl>(
      async_->Get(), testpoint_url, testpoint_timeout);
  const int http_timeout_ms =
      xml_config.asInt(component_xpath + "/httpclient_timeout_ms", 0);
  if (http_timeout_ms) {
    LOG_INFO() << "[testsuite] Forcing HTTP client timeout to "
               << http_timeout_ms;
    utils::testsuite::SetHttpClientTimeoutMs(http_timeout_ms);
  }

  if (xml_config.asInt(component_xpath + "/cache_update_disabled", 0)) {
    LOG_INFO() << "[testsuite] Periodical cache updates disabled";
    cache_update_disabled_ = true;
  }
}

void TestsControlHandler::onUnload() {
  testpoint_control_.reset();
  async_.Release();

  handlers::Base::onUnload();
}

void TestsControlHandler::AddCacheInvalidator(
    [[maybe_unused]] const fastcgi::Component* owner,
    [[maybe_unused]] const utils::CacheInvalidator& invalidator) {
#ifdef MOCK_NOW
  std::lock_guard<std::mutex> guard(mutex_);
  cache_invalidators_.push_back(Invalidator{owner, invalidator});
#endif  // MOCK_NOW
}

void TestsControlHandler::RemoveCacheInvalidator([
    [maybe_unused]] const fastcgi::Component* owner) {
#ifdef MOCK_NOW
  std::lock_guard<std::mutex> guard(mutex_);

  auto it = std::remove_if(
      cache_invalidators_.begin(), cache_invalidators_.end(),
      [owner](const Invalidator& inv) { return inv.owner == owner; });

  if (it == cache_invalidators_.end()) {
    LOG_ERROR() << "component " << owner
                << " is not registed, "
                   "perhaps you forget to call RegisterCacheinvalidator()";
    std::abort();
  }
  cache_invalidators_.erase(it, cache_invalidators_.end());
#endif  // MOCK_NOW
}

void TestsControlHandler::AddWorkerExecuter(
    [[maybe_unused]] const std::string& worker_name,
    [[maybe_unused]] const fastcgi::Component* owner,
    [[maybe_unused]] const utils::WorkerExecuter& executer) {
#ifdef MOCK_NOW
  std::lock_guard<std::mutex> guard(mutex_);
  if (worker_executers_.count(worker_name))
    throw std::logic_error("Worker already registered: " + worker_name);
  worker_executers_[worker_name] = Executer{owner, executer};
#endif  // MOCK_NOW
}

void TestsControlHandler::RemoveWorkerExecuter([
    [maybe_unused]] const fastcgi::Component* owner) {
#ifdef MOCK_NOW
  std::lock_guard<std::mutex> guard(mutex_);

  auto it =
      std::find_if(worker_executers_.begin(), worker_executers_.end(),
                   [owner](const std::pair<std::string, Executer>& value) {
                     return value.second.owner == owner;
                   });

  if (it == worker_executers_.end()) {
    LOG_ERROR() << "component " << owner
                << " is not registed, "
                   "perhaps you forget to call AddWorkerExecuter()";
    std::abort();
  }
  worker_executers_.erase(it);
#endif  // MOCK_NOW
}

void TestsControlHandler::HandleRequestThrow(fastcgi::Request&,
                                             ::handlers::BaseContext& context) {
  using utils::helpers::FetchMemberDef;

#ifndef MOCK_NOW
  LOG_ERROR() << "To use this method please recompile with -DMOCK_NOW"
              << context.log_extra;
  throw BadRequest();
#else   // MOCK_NOW
  handlers::HttpMethod method = context.method;

  if (method != handlers::HttpMethod::Post) throw BadRequest();

  Json::Value data =
      utils::helpers::ParseJsonRequest(context.request_body, context.log_extra);

  bool invalidate_caches = false;
  bool cache_clean_update = true;
  std::time_t now = 0;
  std::vector<std::string> run_workers;

  try {
    std::string now_str;
    FetchMemberDef(now_str, std::string(), data, "now");
    FetchMemberDef(invalidate_caches, false, data, "invalidate_caches");
    FetchMemberDef(cache_clean_update, true, data, "cache_clean_update");
    FetchMemberDef(run_workers, {}, data, "run_workers");

    if (run_workers.empty() && !now_str.empty()) {
      now = std::chrono::duration_cast<std::chrono::seconds>(
                utils::datetime::Stringtime(now_str).time_since_epoch())
                .count();
    }
  } catch (const std::exception& e) {
    throw http_errors::BadRequest(std::string("Failed to parse params: ") +
                                  e.what());
  }

  std::lock_guard<std::mutex> guard(mutex_);

  // You can either mock now and invalidate caches, or run workers.
  // It's because usually in testsuite you don't want to change now() or update
  // caches when running workers
  if (run_workers.empty()) {
    if (now)
      utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(now));
    else
      utils::datetime::MockNowUnset();

    if (invalidate_caches) {
      for (auto invalidator : cache_invalidators_) {
        invalidator.handler(cache_clean_update);
      }
    }
  } else {
    for (const auto& worker_name : run_workers) {
      auto it = worker_executers_.find(worker_name);
      if (it == worker_executers_.end())
        throw http_errors::BadRequest("Worker not found: " + worker_name);

      it->second.handler();
    }
  }

  context.response = "{}";
#endif  // MOCK_NOW
}
