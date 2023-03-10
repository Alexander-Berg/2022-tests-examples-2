/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/services/client-test-service/api/api-3.0.yaml,
// taxi/schemas/schemas/services/client-test-service/api/api.yaml

#include <clients/client-test-service/impl/client_impl.hpp>

#include <clients/impl/client_helpers.hpp>
#include <codegen/impl/split_by.hpp>

#include <clients/codegen/propagated_headers.hpp>
#include <clients/codegen/qos_dict.hpp>
#include <clients/codegen/response_future.hpp>
#include <clients/http.hpp>
#include <clients/impl/envoy_metric.hpp>
#include <codegen/prepare_json.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/http/common_headers.hpp>
#include <userver/utils/algo.hpp>
#include <userver/utils/impl/wait_token_storage.hpp>
#include <userver/utils/text.hpp>
#include <userver/utils/underlying_value.hpp>

#include <taxi_config/variables/CLIENT_TEST_SERVICE_CLIENT_QOS.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/parse/common_containers.hpp>

#include <boost/algorithm/string/join.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <codegen/impl/convert.hpp>
#include <codegen/impl/parsers.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>

namespace {

namespace headers {}  // namespace headers

}

namespace clients::client_test_service::impl {

struct Metrics final {
  clients::impl::MethodMetric v1_my_arg_smth_get;
  clients::impl::MethodMetric v1_my_arg_smth_post;
  clients::impl::MethodMetric v2_smth_get;
  clients::impl::MethodMetric v2_smth_post;
  clients::impl::MethodMetric v3_smth_get;
  clients::impl::MethodMetric v3_smth_post;
  clients::impl::MethodMetric root__get;
  clients::impl::MethodMetric root__post;
};

formats::json::ValueBuilder DumpMetric(Metrics& m)
{
  formats::json::ValueBuilder builder;
  builder["/v1/my-arg/smth-get"] = DumpMethodMetric(m.v1_my_arg_smth_get);
  builder["/v1/my-arg/smth-post"] = DumpMethodMetric(m.v1_my_arg_smth_post);
  builder["/v2/smth-get"] = DumpMethodMetric(m.v2_smth_get);
  builder["/v2/smth-post"] = DumpMethodMetric(m.v2_smth_post);
  builder["/v3/smth-get"] = DumpMethodMetric(m.v3_smth_get);
  builder["/v3/smth-post"] = DumpMethodMetric(m.v3_smth_post);
  builder["/-get"] = DumpMethodMetric(m.root__get);
  builder["/-post"] = DumpMethodMetric(m.root__post);

  return builder;
}

utils::statistics::MetricTag<Metrics> kStatistics(
    "clients.client-test-service.operations");

namespace {

struct EnvoyMetrics final {
  ::clients::impl::EnvoyVHostCounter v1_my_arg_smth_get{};
  ::clients::impl::EnvoyVHostCounter v1_my_arg_smth_post{};
  ::clients::impl::EnvoyVHostCounter v2_smth_get{};
  ::clients::impl::EnvoyVHostCounter v2_smth_post{};
  ::clients::impl::EnvoyVHostCounter v3_smth_get{};
  ::clients::impl::EnvoyVHostCounter v3_smth_post{};
  ::clients::impl::EnvoyVHostCounter root__get{};
  ::clients::impl::EnvoyVHostCounter root__post{};
};

::formats::json::ValueBuilder DumpMetric(EnvoyMetrics& m)
{
  ::formats::json::ValueBuilder builder(::formats::json::Type::kObject);

  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v1_my_arg_smth_get;
    if (mm.SizeApprox() > 0) {
      builder["/v1/my-arg/smth-get"] =
          ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v1_my_arg_smth_post;
    if (mm.SizeApprox() > 0) {
      builder["/v1/my-arg/smth-post"] =
          ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v2_smth_get;
    if (mm.SizeApprox() > 0) {
      builder["/v2/smth-get"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v2_smth_post;
    if (mm.SizeApprox() > 0) {
      builder["/v2/smth-post"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v3_smth_get;
    if (mm.SizeApprox() > 0) {
      builder["/v3/smth-get"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.v3_smth_post;
    if (mm.SizeApprox() > 0) {
      builder["/v3/smth-post"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.root__get;
    if (mm.SizeApprox() > 0) {
      builder["/-get"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }
  // keep solomon clear from empty metrics
  {
    const auto& mm = m.root__post;
    if (mm.SizeApprox() > 0) {
      builder["/-post"] = ::clients::impl::DumpEnvoyVHostCounter(mm);
    }
  }

  return builder;
}

void ResetMetric(EnvoyMetrics& m) {
  m.v1_my_arg_smth_get.Clear();
  m.v1_my_arg_smth_post.Clear();
  m.v2_smth_get.Clear();
  m.v2_smth_post.Clear();
  m.v3_smth_get.Clear();
  m.v3_smth_post.Clear();
  m.root__get.Clear();
  m.root__post.Clear();
}

::utils::statistics::MetricTag<EnvoyMetrics> kEnvoyStatistics(
    "envoy.client-test-service.operations");

}  // namespace

class ClientImpl::Impl {
 public:
  mutable ::utils::impl::WaitTokenStorage wts;
};

ClientImpl::ClientImpl(
    ::clients::Http& http_client, const ::dynamic_config::Source& config,
    const std::string& base_url, utils::statistics::MetricsStoragePtr metrics,
    ::logging::Level body_log_level, size_t body_log_limit,
    std::optional<std::string> proxy,
    std::optional<clients::http::ProxyAuthType> proxy_auth_type,
    clients::StatisticsReachUserverInterface statistics_userver_client)
    : config_(config),
      http_client_(http_client),
      base_url_(base_url),
      base_path_(::http::ExtractPath(base_url_)),
      metrics_(std::move(metrics)),
      body_log_level_(body_log_level),
      body_log_limit_(body_log_limit),
      proxy_(std::move(proxy)),
      proxy_auth_type_(std::move(proxy_auth_type)),
      statistics_client_(statistics_userver_client.GetStandardInterface())
{
  static const std::string kUnix = "unix:/";
  if (utils::text::StartsWith(base_url_, kUnix)) {
    // strip starting "unix:" without the slash
    unix_socket_path_ = base_url_.substr(kUnix.size() - 1);

    base_url_ = "http://localhost";
  }
}

ClientImpl::~ClientImpl() = default;

v1_my_arg_smth::get::Response ClientImpl::V1MyArgSmthGet(
    const v1_my_arg_smth::get::Request& request,
    const CommandControl& command_control) const {
  auto future = AsyncV1MyArgSmthGet(request, command_control);
  return future.Get();
}

::clients::codegen::ResponseFuture<v1_my_arg_smth::get::Response>
ClientImpl::AsyncV1MyArgSmthGet(const v1_my_arg_smth::get::Request& request,
                                const CommandControl& command_control) const {
  const auto limit_retries = statistics_client_.FallbackFired(
      "handler.client-test-service./v1/my-arg/smth-get.fallback");

  const auto config = config_.GetSnapshot();
  const auto& qos_dict = config[::taxi_config::CLIENT_TEST_SERVICE_CLIENT_QOS];
  const auto qos = clients::codegen::GetQosInfoForOperation(
      qos_dict, base_path_ + "/v1/my-arg/smth", "get");

  const auto retries =
      limit_retries ? 1 : command_control.retries.value_or(qos.attempts);
  const auto timeout = command_control.timeout.value_or(qos.timeout_ms);

  return [&]() {
    [[maybe_unused]] ::clients::http::Headers request_headers;
    request_headers = request.GetHeaders();

    auto http_request = http_client_.CreateNotSignedRequest();

    if (!unix_socket_path_.empty()) {
      http_request->unix_socket_path(unix_socket_path_);
    }

    if (proxy_) {
      http_request->proxy(*proxy_);
      if (proxy_auth_type_) {
        http_request->proxy_auth_type(*proxy_auth_type_);
      }
    }

    const std::string url = base_url_ + request.GetPath();

    http_request->SetLoggedUrl(url);  // with no query

    http_request->headers(std::move(request_headers))
        ->timeout(timeout)
        ->retry(retries)
        ->SetDestinationMetricName(base_url_ + "/v1/_my-arg_/smth")
        ->get(::http::MakeUrl(url, request.GetQuery()));

    auto token = impl_->wts.GetToken();
    return clients::codegen::ResponseFuture<v1_my_arg_smth::get::Response>{
        http_request->async_perform(),
        [this, token = std::move(token)](::clients::http::ResponseFuture&& x) {
          return ParseV1MyArgSmthGet(std::move(x));
        },
    };
  }();
}

v1_my_arg_smth::get::Response ClientImpl::ParseV1MyArgSmthGet(
    ::clients::http::ResponseFuture&& future) const {
  namespace handle = v1_my_arg_smth::get;
  static const std::string kStatisticsError =
      "handler.client-test-service./v1/my-arg/smth-get.error";
  static const std::string kStatisticsSuccess =
      "handler.client-test-service./v1/my-arg/smth-get.success";
  static const std::string kStatistics4xx =
      "handler.client-test-service./v1/my-arg/smth-get.success.4xx";
  static const std::string kStatisticsTimeout =
      "handler.client-test-service./v1/my-arg/smth-get.error.timeout";

  std::optional<int> status_code;
  try {
    auto http_result = future.Get();

    LOG(body_log_level_) << "Response body: "
                         << utils::log::ToLimitedUtf8(http_result->body_view(),
                                                      body_log_limit_);

    const auto& headers = http_result->headers();

    {
      // envoy appends vhost header to response
      // so we could know which endpoint was used
      const std::string* vhost_ptr =
          ::utils::FindOrNullptr(headers, ::clients::impl::kEnvoyVHostHeader);
      if (vhost_ptr) {
        auto& vhost_metric = metrics_->GetMetric(kEnvoyStatistics)
                                 .v1_my_arg_smth_get[*vhost_ptr];
        (*vhost_metric)++;
      }
    }

    const auto http_status_code = http_result->status_code();
    status_code = http_status_code;
    if (500 <= http_status_code || 429 == http_status_code) {
      statistics_client_.Send(kStatisticsError, 1);
    } else {
      statistics_client_.Send(kStatisticsSuccess, 1);

      if (http_status_code < 500 && http_status_code >= 400) {
        statistics_client_.Send(kStatistics4xx, 1);
      }
    }

    const auto status = utils::UnderlyingValue(http_status_code);
    switch (status) {
      case 200: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response200 response{[](std::string_view sw) {
          clients::client_test_service::v1_my_arg_smth::get::Response200 result;
          // .cpp_type:
          // clients::client_test_service::v1_my_arg_smth::get::Response200
          // .optional_subtype: None
          // cpp_type:
          // clients::client_test_service::v1_my_arg_smth::get::Response200
          clients::client_test_service::v1_my_arg_smth::get::parser::
              PResponse200 parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }

      default: {
        metrics_->GetMetric(kStatistics).v1_my_arg_smth_get.unknown_code++;

        auto response_headers =
            clients::codegen::ExtractPropagatedHeaders(headers);
        clients::impl::ThrowUnexpectedResponseCode<
            handle::ExceptionWithStatusCode>(status,
                                             std::move(response_headers));
      }
    }

  } catch (const handle::Exception& /*e*/) {
    throw;

    // V1MyArgSmthGet must throw only handle::Exception based exceptions
  } catch (const ::clients::http::TimeoutException& e) {
    statistics_client_.Send(kStatisticsError, 1);
    statistics_client_.Send(kStatisticsTimeout, 1);
    ::clients::impl::ThrowRuntimeErrorFor<handle::TimeoutException>(e.what());
  } catch (const std::exception& e) {
    statistics_client_.Send(kStatisticsError, 1);
    if (status_code) {
      ::clients::impl::ThrowRuntimeErrorFor<handle::ExceptionWithStatusCode>(
          *status_code, e.what());
    } else {
      ::clients::impl::ThrowRuntimeErrorFor<handle::Exception>(e.what());
    }
  }
}

v1_my_arg_smth::post::Response ClientImpl::V1MyArgSmthPost(
    const v1_my_arg_smth::post::Request& request,
    const CommandControl& command_control) const {
  auto future = AsyncV1MyArgSmthPost(request, command_control);
  return future.Get();
}

::clients::codegen::ResponseFuture<v1_my_arg_smth::post::Response>
ClientImpl::AsyncV1MyArgSmthPost(const v1_my_arg_smth::post::Request& request,
                                 const CommandControl& command_control) const {
  const auto limit_retries = statistics_client_.FallbackFired(
      "handler.client-test-service./v1/my-arg/smth-post.fallback");

  const auto config = config_.GetSnapshot();
  const auto& qos_dict = config[::taxi_config::CLIENT_TEST_SERVICE_CLIENT_QOS];
  const auto qos = clients::codegen::GetQosInfoForOperation(
      qos_dict, base_path_ + "/v1/my-arg/smth", "post");

  const auto retries =
      limit_retries ? 1 : command_control.retries.value_or(qos.attempts);
  const auto timeout = command_control.timeout.value_or(qos.timeout_ms);

  return [&]() {
    [[maybe_unused]] ::clients::http::Headers request_headers;
    request_headers = request.GetHeaders();

    auto http_request = http_client_.CreateNotSignedRequest();

    if (!unix_socket_path_.empty()) {
      http_request->unix_socket_path(unix_socket_path_);
    }

    if (proxy_) {
      http_request->proxy(*proxy_);
      if (proxy_auth_type_) {
        http_request->proxy_auth_type(*proxy_auth_type_);
      }
    }

    const std::string url = base_url_ + request.GetPath();

    http_request->headers(std::move(request_headers))
        ->timeout(timeout)
        ->retry(retries)
        ->SetDestinationMetricName(base_url_ + "/v1/_my-arg_/smth")
        ->post(::http::MakeUrl(url, request.GetQuery()), [&request, this] {
          auto body = request.GetBody();
          LOG(body_log_level_)
              << "Request body: "
              << utils::log::ToLimitedUtf8(body, body_log_limit_);
          return body;
        }());

    auto token = impl_->wts.GetToken();
    return clients::codegen::ResponseFuture<v1_my_arg_smth::post::Response>{
        http_request->async_perform(),
        [this, token = std::move(token)](::clients::http::ResponseFuture&& x) {
          return ParseV1MyArgSmthPost(std::move(x));
        },
    };
  }();
}

v1_my_arg_smth::post::Response ClientImpl::ParseV1MyArgSmthPost(
    ::clients::http::ResponseFuture&& future) const {
  namespace handle = v1_my_arg_smth::post;
  static const std::string kStatisticsError =
      "handler.client-test-service./v1/my-arg/smth-post.error";
  static const std::string kStatisticsSuccess =
      "handler.client-test-service./v1/my-arg/smth-post.success";
  static const std::string kStatistics4xx =
      "handler.client-test-service./v1/my-arg/smth-post.success.4xx";
  static const std::string kStatisticsTimeout =
      "handler.client-test-service./v1/my-arg/smth-post.error.timeout";

  std::optional<int> status_code;
  try {
    auto http_result = future.Get();

    LOG(body_log_level_) << "Response body: "
                         << utils::log::ToLimitedUtf8(http_result->body_view(),
                                                      body_log_limit_);

    const auto& headers = http_result->headers();

    {
      // envoy appends vhost header to response
      // so we could know which endpoint was used
      const std::string* vhost_ptr =
          ::utils::FindOrNullptr(headers, ::clients::impl::kEnvoyVHostHeader);
      if (vhost_ptr) {
        auto& vhost_metric = metrics_->GetMetric(kEnvoyStatistics)
                                 .v1_my_arg_smth_post[*vhost_ptr];
        (*vhost_metric)++;
      }
    }

    const auto http_status_code = http_result->status_code();
    status_code = http_status_code;
    if (500 <= http_status_code || 429 == http_status_code) {
      statistics_client_.Send(kStatisticsError, 1);
    } else {
      statistics_client_.Send(kStatisticsSuccess, 1);

      if (http_status_code < 500 && http_status_code >= 400) {
        statistics_client_.Send(kStatistics4xx, 1);
      }
    }

    const auto status = utils::UnderlyingValue(http_status_code);
    switch (status) {
      case 200: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response200 response{[](std::string_view sw) {
          clients::client_test_service::v1_my_arg_smth::post::Response200
              result;
          // .cpp_type:
          // clients::client_test_service::v1_my_arg_smth::post::Response200
          // .optional_subtype: None
          // cpp_type:
          // clients::client_test_service::v1_my_arg_smth::post::Response200
          clients::client_test_service::v1_my_arg_smth::post::parser::
              PResponse200 parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }
      case 201: {
        handle::Response201 response;

        return response;
      }
      case 404: {
        handle::Response404 response;

        static_assert(std::is_base_of_v<std::exception, handle::Response404>,
                      "Trying to throw non-exception type");
        throw response;
      }

      default: {
        metrics_->GetMetric(kStatistics).v1_my_arg_smth_post.unknown_code++;

        auto response_headers =
            clients::codegen::ExtractPropagatedHeaders(headers);
        clients::impl::ThrowUnexpectedResponseCode<
            handle::ExceptionWithStatusCode>(status,
                                             std::move(response_headers));
      }
    }

  } catch (const handle::Exception& /*e*/) {
    throw;

    // V1MyArgSmthPost must throw only handle::Exception based exceptions
  } catch (const ::clients::http::TimeoutException& e) {
    statistics_client_.Send(kStatisticsError, 1);
    statistics_client_.Send(kStatisticsTimeout, 1);
    ::clients::impl::ThrowRuntimeErrorFor<handle::TimeoutException>(e.what());
  } catch (const std::exception& e) {
    statistics_client_.Send(kStatisticsError, 1);
    if (status_code) {
      ::clients::impl::ThrowRuntimeErrorFor<handle::ExceptionWithStatusCode>(
          *status_code, e.what());
    } else {
      ::clients::impl::ThrowRuntimeErrorFor<handle::Exception>(e.what());
    }
  }
}

v3_smth::get::Response ClientImpl::V3SmthGet(
    const CommandControl& command_control) const {
  auto future = AsyncV3SmthGet(command_control);
  return future.Get();
}

::clients::codegen::ResponseFuture<v3_smth::get::Response>
ClientImpl::AsyncV3SmthGet(const CommandControl& command_control) const {
  const auto limit_retries = statistics_client_.FallbackFired(
      "handler.client-test-service./v3/smth-get.fallback");

  const auto config = config_.GetSnapshot();
  const auto& qos_dict = config[::taxi_config::CLIENT_TEST_SERVICE_CLIENT_QOS];
  const auto qos = clients::codegen::GetQosInfoForOperation(
      qos_dict, base_path_ + "/v3/smth", "get");

  const auto retries =
      limit_retries ? 1 : command_control.retries.value_or(qos.attempts);
  const auto timeout = command_control.timeout.value_or(qos.timeout_ms);

  return [&]() {
    [[maybe_unused]] ::clients::http::Headers request_headers;

    auto http_request = http_client_.CreateNotSignedRequest();

    if (!unix_socket_path_.empty()) {
      http_request->unix_socket_path(unix_socket_path_);
    }

    if (proxy_) {
      http_request->proxy(*proxy_);
      if (proxy_auth_type_) {
        http_request->proxy_auth_type(*proxy_auth_type_);
      }
    }

    const std::string url = base_url_ + "/v3/smth";

    http_request->timeout(timeout)->retry(retries)->get(url);

    auto token = impl_->wts.GetToken();
    return clients::codegen::ResponseFuture<v3_smth::get::Response>{
        http_request->async_perform(),
        [this, token = std::move(token)](::clients::http::ResponseFuture&& x) {
          return ParseV3SmthGet(std::move(x));
        },
    };
  }();
}

v3_smth::get::Response ClientImpl::ParseV3SmthGet(
    ::clients::http::ResponseFuture&& future) const {
  namespace handle = v3_smth::get;
  static const std::string kStatisticsError =
      "handler.client-test-service./v3/smth-get.error";
  static const std::string kStatisticsSuccess =
      "handler.client-test-service./v3/smth-get.success";
  static const std::string kStatistics4xx =
      "handler.client-test-service./v3/smth-get.success.4xx";
  static const std::string kStatisticsTimeout =
      "handler.client-test-service./v3/smth-get.error.timeout";

  std::optional<int> status_code;
  try {
    auto http_result = future.Get();

    LOG(body_log_level_) << "Response body: "
                         << utils::log::ToLimitedUtf8(http_result->body_view(),
                                                      body_log_limit_);

    const auto& headers = http_result->headers();

    {
      // envoy appends vhost header to response
      // so we could know which endpoint was used
      const std::string* vhost_ptr =
          ::utils::FindOrNullptr(headers, ::clients::impl::kEnvoyVHostHeader);
      if (vhost_ptr) {
        auto& vhost_metric =
            metrics_->GetMetric(kEnvoyStatistics).v3_smth_get[*vhost_ptr];
        (*vhost_metric)++;
      }
    }

    const auto http_status_code = http_result->status_code();
    status_code = http_status_code;
    if (500 <= http_status_code || 429 == http_status_code) {
      statistics_client_.Send(kStatisticsError, 1);
    } else {
      statistics_client_.Send(kStatisticsSuccess, 1);

      if (http_status_code < 500 && http_status_code >= 400) {
        statistics_client_.Send(kStatistics4xx, 1);
      }
    }

    const auto status = utils::UnderlyingValue(http_status_code);
    switch (status) {
      case 200: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response200 response{[](std::string_view sw) {
          clients::client_test_service::v3_smth::get::Response200 result;
          // .cpp_type: clients::client_test_service::v3_smth::get::Response200
          // .optional_subtype: None
          // cpp_type: clients::client_test_service::v3_smth::get::Response200
          clients::client_test_service::v3_smth::get::parser::PResponse200
              parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }

      default: {
        metrics_->GetMetric(kStatistics).v3_smth_get.unknown_code++;

        auto response_headers =
            clients::codegen::ExtractPropagatedHeaders(headers);
        clients::impl::ThrowUnexpectedResponseCode<
            handle::ExceptionWithStatusCode>(status,
                                             std::move(response_headers));
      }
    }

  } catch (const handle::Exception& /*e*/) {
    throw;

    // V3SmthGet must throw only handle::Exception based exceptions
  } catch (const ::clients::http::TimeoutException& e) {
    statistics_client_.Send(kStatisticsError, 1);
    statistics_client_.Send(kStatisticsTimeout, 1);
    ::clients::impl::ThrowRuntimeErrorFor<handle::TimeoutException>(e.what());
  } catch (const std::exception& e) {
    statistics_client_.Send(kStatisticsError, 1);
    if (status_code) {
      ::clients::impl::ThrowRuntimeErrorFor<handle::ExceptionWithStatusCode>(
          *status_code, e.what());
    } else {
      ::clients::impl::ThrowRuntimeErrorFor<handle::Exception>(e.what());
    }
  }
}

root_::get::Response ClientImpl::NsGet(
    const root_::get::Request& request,
    const CommandControl& command_control) const {
  auto future = AsyncNsGet(request, command_control);
  return future.Get();
}

::clients::codegen::ResponseFuture<root_::get::Response> ClientImpl::AsyncNsGet(
    const root_::get::Request& request,
    const CommandControl& command_control) const {
  const auto limit_retries = statistics_client_.FallbackFired(
      "handler.client-test-service./-get.fallback");

  const auto config = config_.GetSnapshot();
  const auto& qos_dict = config[::taxi_config::CLIENT_TEST_SERVICE_CLIENT_QOS];
  const auto qos = clients::codegen::GetQosInfoForOperation(
      qos_dict, base_path_ + "/", "get");

  const auto retries =
      limit_retries ? 1 : command_control.retries.value_or(qos.attempts);
  const auto timeout = command_control.timeout.value_or(qos.timeout_ms);

  return [&]() {
    [[maybe_unused]] ::clients::http::Headers request_headers;
    request_headers = request.GetHeaders();

    auto http_request = http_client_.CreateNotSignedRequest();

    if (!unix_socket_path_.empty()) {
      http_request->unix_socket_path(unix_socket_path_);
    }

    if (proxy_) {
      http_request->proxy(*proxy_);
      if (proxy_auth_type_) {
        http_request->proxy_auth_type(*proxy_auth_type_);
      }
    }

    const std::string url = base_url_ + "/";

    auto query = request.GetQuery();
    query.erase("secret");
    http_request->SetLoggedUrl(::http::MakeUrl(url, query) +
                               " (some query params were hidden)");

    http_request->headers(std::move(request_headers))
        ->timeout(timeout)
        ->retry(retries)
        ->get(::http::MakeUrl(url, request.GetQuery()));

    auto token = impl_->wts.GetToken();
    return clients::codegen::ResponseFuture<root_::get::Response>{
        http_request->async_perform(),
        [this, token = std::move(token)](::clients::http::ResponseFuture&& x) {
          return ParseNsGet(std::move(x));
        },
    };
  }();
}

root_::get::Response ClientImpl::ParseNsGet(
    ::clients::http::ResponseFuture&& future) const {
  namespace handle = root_::get;
  static const std::string kStatisticsError =
      "handler.client-test-service./-get.error";
  static const std::string kStatisticsSuccess =
      "handler.client-test-service./-get.success";
  static const std::string kStatistics4xx =
      "handler.client-test-service./-get.success.4xx";
  static const std::string kStatisticsTimeout =
      "handler.client-test-service./-get.error.timeout";

  std::optional<int> status_code;
  try {
    auto http_result = future.Get();

    LOG(body_log_level_) << "Response body: "
                         << utils::log::ToLimitedUtf8(http_result->body_view(),
                                                      body_log_limit_);

    const auto& headers = http_result->headers();

    {
      // envoy appends vhost header to response
      // so we could know which endpoint was used
      const std::string* vhost_ptr =
          ::utils::FindOrNullptr(headers, ::clients::impl::kEnvoyVHostHeader);
      if (vhost_ptr) {
        auto& vhost_metric =
            metrics_->GetMetric(kEnvoyStatistics).root__get[*vhost_ptr];
        (*vhost_metric)++;
      }
    }

    const auto http_status_code = http_result->status_code();
    status_code = http_status_code;
    if (500 <= http_status_code || 429 == http_status_code) {
      statistics_client_.Send(kStatisticsError, 1);
    } else {
      statistics_client_.Send(kStatisticsSuccess, 1);

      if (http_status_code < 500 && http_status_code >= 400) {
        statistics_client_.Send(kStatistics4xx, 1);
      }
    }

    const auto status = utils::UnderlyingValue(http_status_code);
    switch (status) {
      case 200: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response200 response{[](std::string_view sw) {
          clients::client_test_service::root_::get::Response200 result;
          // .cpp_type: clients::client_test_service::root_::get::Response200
          // .optional_subtype: None
          // cpp_type: clients::client_test_service::root_::get::Response200
          clients::client_test_service::root_::get::parser::PResponse200 parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }

      default: {
        metrics_->GetMetric(kStatistics).root__get.unknown_code++;

        auto response_headers =
            clients::codegen::ExtractPropagatedHeaders(headers);
        clients::impl::ThrowUnexpectedResponseCode<
            handle::ExceptionWithStatusCode>(status,
                                             std::move(response_headers));
      }
    }

  } catch (const handle::Exception& /*e*/) {
    throw;

    // NsGet must throw only handle::Exception based exceptions
  } catch (const ::clients::http::TimeoutException& e) {
    statistics_client_.Send(kStatisticsError, 1);
    statistics_client_.Send(kStatisticsTimeout, 1);
    ::clients::impl::ThrowRuntimeErrorFor<handle::TimeoutException>(e.what());
  } catch (const std::exception& e) {
    statistics_client_.Send(kStatisticsError, 1);
    if (status_code) {
      ::clients::impl::ThrowRuntimeErrorFor<handle::ExceptionWithStatusCode>(
          *status_code, e.what());
    } else {
      ::clients::impl::ThrowRuntimeErrorFor<handle::Exception>(e.what());
    }
  }
}

root_::post::Response ClientImpl::NsPost(
    const root_::post::Request& request,
    const CommandControl& command_control) const {
  auto future = AsyncNsPost(request, command_control);
  return future.Get();
}

::clients::codegen::ResponseFuture<root_::post::Response>
ClientImpl::AsyncNsPost(const root_::post::Request& request,
                        const CommandControl& command_control) const {
  const auto limit_retries = statistics_client_.FallbackFired(
      "handler.client-test-service./-post.fallback");

  const auto config = config_.GetSnapshot();
  const auto& qos_dict = config[::taxi_config::CLIENT_TEST_SERVICE_CLIENT_QOS];
  const auto qos = clients::codegen::GetQosInfoForOperation(
      qos_dict, base_path_ + "/", "post");

  const auto retries =
      limit_retries ? 1 : command_control.retries.value_or(qos.attempts);
  const auto timeout = command_control.timeout.value_or(qos.timeout_ms);

  return [&]() {
    [[maybe_unused]] ::clients::http::Headers request_headers;
    request_headers = request.GetHeaders();

    auto http_request = http_client_.CreateNotSignedRequest();

    if (!unix_socket_path_.empty()) {
      http_request->unix_socket_path(unix_socket_path_);
    }

    if (proxy_) {
      http_request->proxy(*proxy_);
      if (proxy_auth_type_) {
        http_request->proxy_auth_type(*proxy_auth_type_);
      }
    }

    const std::string url = base_url_ + "/";

    http_request->headers(std::move(request_headers))
        ->timeout(timeout)
        ->retry(retries)
        ->post(::http::MakeUrl(url, request.GetQuery()), [&request, this] {
          auto body = request.GetBody();
          LOG(body_log_level_)
              << "Request body: "
              << utils::log::ToLimitedUtf8(body, body_log_limit_);
          return body;
        }());

    auto token = impl_->wts.GetToken();
    return clients::codegen::ResponseFuture<root_::post::Response>{
        http_request->async_perform(),
        [this, token = std::move(token)](::clients::http::ResponseFuture&& x) {
          return ParseNsPost(std::move(x));
        },
    };
  }();
}

root_::post::Response ClientImpl::ParseNsPost(
    ::clients::http::ResponseFuture&& future) const {
  namespace handle = root_::post;
  static const std::string kStatisticsError =
      "handler.client-test-service./-post.error";
  static const std::string kStatisticsSuccess =
      "handler.client-test-service./-post.success";
  static const std::string kStatistics4xx =
      "handler.client-test-service./-post.success.4xx";
  static const std::string kStatisticsTimeout =
      "handler.client-test-service./-post.error.timeout";

  std::optional<int> status_code;
  try {
    auto http_result = future.Get();

    LOG(body_log_level_) << "Response body: "
                         << utils::log::ToLimitedUtf8(http_result->body_view(),
                                                      body_log_limit_);

    const auto& headers = http_result->headers();

    {
      // envoy appends vhost header to response
      // so we could know which endpoint was used
      const std::string* vhost_ptr =
          ::utils::FindOrNullptr(headers, ::clients::impl::kEnvoyVHostHeader);
      if (vhost_ptr) {
        auto& vhost_metric =
            metrics_->GetMetric(kEnvoyStatistics).root__post[*vhost_ptr];
        (*vhost_metric)++;
      }
    }

    const auto http_status_code = http_result->status_code();
    status_code = http_status_code;
    if (500 <= http_status_code || 429 == http_status_code) {
      statistics_client_.Send(kStatisticsError, 1);
    } else {
      statistics_client_.Send(kStatisticsSuccess, 1);

      if (http_status_code < 500 && http_status_code >= 400) {
        statistics_client_.Send(kStatistics4xx, 1);
      }
    }

    const auto status = utils::UnderlyingValue(http_status_code);
    switch (status) {
      case 200: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response200 response{[](std::string_view sw) {
          clients::client_test_service::root_::post::Response200 result;
          // .cpp_type: clients::client_test_service::root_::post::Response200
          // .optional_subtype: None
          // cpp_type: clients::client_test_service::root_::post::Response200
          clients::client_test_service::root_::post::parser::PResponse200
              parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }
      case 201: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response201 response{[](std::string_view sw) {
          clients::client_test_service::root_::post::Response201 result;
          // .cpp_type: clients::client_test_service::root_::post::Response201
          // .optional_subtype: None
          // cpp_type: clients::client_test_service::root_::post::Response201
          clients::client_test_service::root_::post::parser::PResponse201
              parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        return response;
      }
      case 404: {
        auto body = ::codegen::PrepareJsonString(http_result->body_view());

        handle::Response404 response{[](std::string_view sw) {
          clients::client_test_service::root_::post::Response404 result;
          // .cpp_type: clients::client_test_service::root_::post::Response404
          // .optional_subtype: None
          // cpp_type: clients::client_test_service::root_::post::Response404
          clients::client_test_service::root_::post::parser::PResponse404
              parser;

          parser.Reset();
          ::formats::json::parser::SubscriberSink sink(result);
          parser.Subscribe(sink);

          formats::json::parser::ParserState state;
          state.PushParser(parser.GetParser());
          state.ProcessInput(sw);
          return result;
        }(body)};

        static_assert(std::is_base_of_v<std::exception, handle::Response404>,
                      "Trying to throw non-exception type");
        throw response;
      }

      default: {
        metrics_->GetMetric(kStatistics).root__post.unknown_code++;

        auto response_headers =
            clients::codegen::ExtractPropagatedHeaders(headers);
        clients::impl::ThrowUnexpectedResponseCode<
            handle::ExceptionWithStatusCode>(status,
                                             std::move(response_headers));
      }
    }

  } catch (const handle::Exception& /*e*/) {
    throw;

    // NsPost must throw only handle::Exception based exceptions
  } catch (const ::clients::http::TimeoutException& e) {
    statistics_client_.Send(kStatisticsError, 1);
    statistics_client_.Send(kStatisticsTimeout, 1);
    ::clients::impl::ThrowRuntimeErrorFor<handle::TimeoutException>(e.what());
  } catch (const std::exception& e) {
    statistics_client_.Send(kStatisticsError, 1);
    if (status_code) {
      ::clients::impl::ThrowRuntimeErrorFor<handle::ExceptionWithStatusCode>(
          *status_code, e.what());
    } else {
      ::clients::impl::ThrowRuntimeErrorFor<handle::Exception>(e.what());
    }
  }
}

}
