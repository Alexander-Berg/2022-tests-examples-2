#include "test_point.hpp"

#include <atomic>
#include <memory>

#include <httpclient/client.hpp>
#include <httpclient/content_types.hpp>
#include <httpclient/headers.hpp>
#include <utils/helpers/json.hpp>
#include <utils/uuid4.hpp>

namespace {

class TestPointClient {
 public:
  TestPointClient(const utils::Async& async, const std::string& url,
                  int timeout)
      : url_(url), timeout_(timeout), http_client_(async, pool_size_, name_) {}

  bool IsEnabled() { return !url_.empty(); }

  Json::Value PerformRequest(const std::string& id, const std::string& name,
                             const Json::Value& data,
                             const LogExtra& log_extra_orig) {
    if (!IsEnabled()) return Json::Value(Json::objectValue);

    LogExtra log_extra(log_extra_orig);
    log_extra.Extend({{"testpoint_id", id}, {"testpoint", name}});

    LOG_INFO() << "Running testpoint " << name << " data "
               << utils::helpers::WriteJson(data, true) << log_extra;

    Json::Value request_data;
    request_data["id"] = id;
    request_data["name"] = name;
    request_data["data"] = data;
    const auto response =
        http_client_.CreateRequest(log_extra)
            ->post(url_, utils::helpers::WriteJson(request_data))
            ->headers({{utils::http::headers::kContentType,
                        utils::http::content_types::kJson}})
            ->timeout(timeout_)
            ->perform();

    if (response->status_code() == 200) {
      auto res = utils::helpers::ParseJson(response->body());
      LOG_INFO() << "Testpoint returned "
                 << utils::helpers::WriteJson(res, true) << log_extra;
      return res;
    }

    // Do not fail if testpoint handler is not yet available
    LOG_WARNING() << "Testpoint finished with status code "
                  << response->status_code() << " content " << response->body()
                  << log_extra;
    return Json::Value(Json::objectValue);
  }

 private:
  const int pool_size_ = 1;
  const std::string name_ = "testpoint";
  const std::string url_;
  const int timeout_;
  utils::http::Client http_client_;
};

std::atomic_bool client_initialized{false};
std::shared_ptr<TestPointClient> client;
std::weak_ptr<TestPointClient> client_weak;

}  // namespace

namespace utils {
namespace testsuite {

TestPointControl::TestPointControl(const utils::Async& async,
                                   const std::string& url, int timeout) {
  client = std::make_shared<TestPointClient>(async, url, timeout);
  client_weak = client;
  client_initialized = true;
}

TestPointControl::~TestPointControl() { client.reset(); }

Json::Value TestPoint(const std::string& name, const Json::Value& data,
                      const LogExtra& log_extra) {
  Json::Value res(Json::objectValue);
  if (!client_initialized) return res;
  auto client_local = client_weak.lock();
  if (client_local) {
    const auto& id = utils::generators::Uuid4();
    res = client_local->PerformRequest(id, name, data, log_extra);
  }
  return res;
}

bool IsTestPointEnabled() {
  if (!client_initialized) return false;
  auto client_local = client_weak.lock();
  return client_local && client_local->IsEnabled();
}

}  // namespace testsuite
}  // namespace utils
