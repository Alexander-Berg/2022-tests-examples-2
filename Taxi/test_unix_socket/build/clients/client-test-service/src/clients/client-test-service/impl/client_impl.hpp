/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/services/client-test-service/api/api.yaml

#pragma once

#include <cstddef>
#include <optional>
#include <string>

#include <clients/client-test-service/client.hpp>

#include <clients/http_fwd.hpp>
#include <userver/clients/http/request.hpp>
#include <userver/dynamic_config/source.hpp>
#include <userver/logging/level.hpp>
#include <userver/utils/statistics/metrics_storage.hpp>

#include <clients/impl/method_metric.hpp>
#include <clients/statistics.hpp>
#include <userver/crypto/certificate.hpp>
#include <userver/crypto/private_key.hpp>

namespace clients::http {
class ResponseFuture;
}

namespace clients::client_test_service::impl {

// Do NOT use this class directly!
//
// Use clients::client_test_service::Client instead!
class ClientImpl final: public Client {
 public:
  explicit ClientImpl(
      ::clients::Http& http_client, const ::dynamic_config::Source& config,
      const std::string& base_url, utils::statistics::MetricsStoragePtr metrics,
      ::logging::Level body_log_level, size_t body_log_limit,
      std::optional<std::string> proxy,
      std::optional<clients::http::ProxyAuthType> proxy_auth_type,
      ::clients::StatisticsReachUserverInterface statistics_userver_client);

  ~ClientImpl();

 private:
  const ::dynamic_config::Source config_;
  ::clients::Http& http_client_;
  std::string base_url_;
  const std::string base_path_;
  std::string unix_socket_path_;
  utils::statistics::MetricsStoragePtr metrics_;
  const ::logging::Level body_log_level_;
  const std::size_t body_log_limit_;
  std::optional<std::string> proxy_;
  std::optional<clients::http::ProxyAuthType> proxy_auth_type_;
  const ::clients::StatisticsReachInterface& statistics_client_;

  class Impl;
  static constexpr size_t kSize = 24;
  static constexpr size_t kAlignment = 8;
  utils::FastPimpl<Impl, kSize, kAlignment> impl_;
};

}
