#include "nobuf_external_echo.hpp"

#include <boost/algorithm/string.hpp>

#include <tvm2/components/tvm2.hpp>
#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include <userver/formats/json.hpp>
#include <userver/http/url.hpp>
#include <userver/server/http/http_response_body_stream.hpp>

#include <taxi_config/variables/TVM_API_URL.hpp>

namespace test_service::handlers {

namespace {

const std::string kEchoPrefix = "Echo-";

}  // namespace

NobuffExternalEcho::NobuffExternalEcho(
    const components::ComponentConfig& config,
    const components::ComponentContext& context)
    : server::handlers::HttpHandlerBase(config, context),
      http_client_(
          context.FindComponent<tvm2::components::Tvm2>().GetHttpClient()),
      config_source_(
          context.FindComponent<components::DynamicConfig>().GetSource()) {}

void NobuffExternalEcho::HandleStreamRequest(
    const server::http::HttpRequest& request, server::request::RequestContext&,
    server::http::ResponseBodyStream&& response_body_stream) const {
  ::http::Args args;
  for (auto&& arg : request.ArgNames()) {
    const auto val = request.GetArg(arg);
    args[arg] = val;
  }
  ::clients::http::Headers headers;
  for (const auto& header_name : request.GetHeaderNames()) {
    const auto& header_value = request.GetHeader(header_name);
    headers[header_name] = header_value;
  }

  const auto& config_snapshot = config_source_.GetSnapshot();
  const auto base_url = config_snapshot[taxi_config::TVM_API_URL];

  const auto url = ::http::MakeUrl(base_url + "/echo", args);
  constexpr auto timeout = std::chrono::milliseconds(100);
  constexpr auto retries = 1;

  auto external_request = http_client_.CreateNotSignedRequest()
                              ->get(url)
                              ->headers(std::move(headers))
                              ->timeout(timeout)
                              ->retry(retries);

  // TODO: WAIT FOR response body
  auto response = external_request->perform();

  formats::json::ValueBuilder response_json(formats::json::Type::kObject);
  response_json["response"] = response->body_view();

  for (const auto& header_item : response->headers()) {
    const auto& header_name = header_item.first;
    const auto& header_value = header_item.second;
    response_body_stream.SetHeader(header_name, header_value);
  }
  response_body_stream.SetStatusCode(response->status_code());

  response_body_stream.SetHeader("abc", "def");
  response_body_stream.SetEndOfHeaders();

  constexpr auto kSplitPosition = 10;
  auto response_body = formats::json::ToString(response_json.ExtractValue());
  UASSERT(response_body.size() > kSplitPosition);

  response_body_stream.PushBodyChunk(response_body.substr(0, kSplitPosition));
  response_body_stream.PushBodyChunk(response_body.substr(kSplitPosition));
}

}  // namespace test_service::handlers
