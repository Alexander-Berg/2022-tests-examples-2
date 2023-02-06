#pragma once

#include <atomic>
#include <optional>

#include <testing/taxi_config.hpp>
#include <userver/concurrent/variable.hpp>
#include <userver/logging/level.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/assert.hpp>

#include <tvm2/http/headers.hpp>
#include <tvm2/utest/mock_client_context.hpp>

// Do not include this header in production code!
#include <clients/userver-sample/impl/client_impl.hpp>

class StatisticsClientMock final : public ::clients::StatisticsReachInterface {
 public:
  void Send(const std::string& metric, unsigned value = 1) const noexcept {
    auto ptr = data_.Lock();
    ptr->metrics[metric] += value;
  }

  bool FallbackFired(const std::string& fallback) const noexcept {
    auto ptr = data_.Lock();
    auto it = ptr->fallbacks.find(fallback);

    if (strict_fallback_check_) {
      EXPECT_NE(it, ptr->fallbacks.end())
          << "asked for nonexisting fallback '" << fallback << "'";
    }

    if (it != ptr->fallbacks.end())
      return it->second;
    else
      return false;
  }

  void MockFallback(const std::string& fallback, bool fired) {
    auto ptr = data_.Lock();
    ptr->fallbacks[fallback] = fired;
  }

  auto GetMetrics() const {
    auto ptr = data_.Lock();
    return ptr->metrics;
  }

  unsigned GetMetric(const std::string& metric) const noexcept {
    auto ptr = data_.Lock();
    auto metric_it = ptr->metrics.find(metric);
    if (metric_it != ptr->metrics.end()) {
      return metric_it->second;
    } else {
      return 0;
    }
  }

  void SetStrictFallbackCheck(bool strict) { strict_fallback_check_ = strict; }

 private:
  struct Data {
    std::unordered_map<std::string, bool> fallbacks;
    std::unordered_map<std::string, size_t> metrics;
  };
  mutable concurrent::Variable<Data> data_;
  std::atomic_bool strict_fallback_check_{false};
};

template <int service_id>
class Tvm2ClientContextMock final : public tvm2::ClientContext {
 public:
  explicit Tvm2ClientContextMock(clients::http::Client& http_client,
                                 std::string service_name)
      : tvm2::ClientContext::ClientContext(http_client),
        service_name_(std::move(service_name)) {}

  tvm2::models::ServiceId GetServiceIdByServiceName(
      const std::string& service_name) const override {
    EXPECT_EQ(service_name_, service_name);
    return tvm2::models::ServiceId{service_id};
  }

  bool CheckCanSignRequestForSource(
      const std::string& service_name) const override {
    EXPECT_EQ(service_name_, service_name);
    return true;
  }

  std::shared_ptr<clients::http::Request> CreateSignedRequest(
      tvm2::models::ServiceId dest_service_id) override {
    EXPECT_EQ(service_id, dest_service_id);

    return CreateNotSignedRequest()->headers({{
        tvm2::http::kXYaServiceTicket,
        "SERVICE TICKET",
    }});
  }

  std::shared_ptr<clients::http::Request> CreateSignedRequestForSource(
      tvm2::models::ServiceId /*src_service_id*/,
      tvm2::models::ServiceId /*dst_service_id*/) override {
    UASSERT(false);
    return {};
  }

 private:
  const std::string service_name_;
};

class ClientWithMock {
 public:
  ClientWithMock(const std::string& url)
      : http_client_(utest::CreateHttpClient()),
        tvm2_context_mock_(*http_client_, "userver-sample"),
        client_(tvm2_context_mock_, dynamic_config::GetDefaultSource(), url,
                std::make_shared<utils::statistics::MetricsStorage>(),
                logging::Level::kDebug, 256, std::nullopt, std::nullopt,
                tvm2_context_mock_.GetServiceIdByServiceName("userver-sample"),
                ::clients::StatisticsReachUserverInterface::Create(
                    statistics_mock_)) {}

  clients::userver_sample::impl::ClientImpl* operator->() { return &client_; }

  StatisticsClientMock& GetStatisticsClient() { return statistics_mock_; }

 private:
  std::shared_ptr<clients::http::Client> http_client_;
  Tvm2ClientContextMock<123> tvm2_context_mock_;
  StatisticsClientMock statistics_mock_;
  clients::userver_sample::impl::ClientImpl client_;
};
