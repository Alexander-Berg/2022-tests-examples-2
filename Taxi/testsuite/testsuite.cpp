#include "testsuite.hpp"

#include <atomic>

#include <fastcgi2/component.h>
#include <boost/algorithm/string/predicate.hpp>

#include <tests_control/tests_control_handler.hpp>

namespace utils {
namespace testsuite {

namespace {

std::atomic<int> http_client_timeout_ms{0};
std::atomic<bool> mockserver_url_set{false};
std::string mockserver_url;

}  // namespace

void SetHttpClientTimeoutMs(int timeout_ms) {
  http_client_timeout_ms = timeout_ms;
}

int GetHttpClientTimeoutMs() { return http_client_timeout_ms; }

bool GetPeriodicalUpdateDisabled(fastcgi::ComponentContext* ccontext) {
  auto component =
      ccontext->findComponent<TestsControlHandler>("tests-control");
  if (!component) return false;
  return component->GetCacheUpdateDisabled();
}

void SetMockserverUrl(const std::string& url) {
  mockserver_url = url;
  mockserver_url_set = true;
}

void CheckHttpUrl(const std::string& url) {
  if (!mockserver_url_set) return;

  LOG_INFO() << "Checking url: " << url
             << " mockserver url: " << mockserver_url;

  if (!boost::starts_with(url, mockserver_url)) {
    LOG_ERROR() << "Trying to access external http resource " << url
                << " from testsuite, please change it to mockserver";
    std::abort();
  }
}

}  // namespace testsuite
}  // namespace utils
