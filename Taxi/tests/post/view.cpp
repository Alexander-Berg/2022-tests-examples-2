#include <views/admin/v1/endpoints/tests/post/view.hpp>

#include <models/tests.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/uuid4.hpp>

namespace handlers::admin_v1_endpoints_tests::post {

namespace {

server::http::HttpMethod ToServerMethod(const handlers::HttpMethod& method) {
  switch (method) {
    case handlers::HttpMethod::kGet:
      return server::http::HttpMethod::kGet;
    case handlers::HttpMethod::kPost:
      return server::http::HttpMethod::kPost;
    case handlers::HttpMethod::kDel:
      return server::http::HttpMethod::kDelete;
    case handlers::HttpMethod::kPut:
      return server::http::HttpMethod::kPut;
    case handlers::HttpMethod::kPatch:
      return server::http::HttpMethod::kPatch;
  }
  throw std::runtime_error(
      "Failed to convert handlers::method to server::http::HttpMethod");
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto configuration_state = dependencies.extra.configuration_.GetState();
  const auto& handler_match = configuration_state->FindHandler(
      ToServerMethod(request.body.method), request.body.endpoint);

  Response200 response;
  response.test_run_id = utils::generators::GenerateUuid();
  response.created = utils::datetime::Now();
  response.status = handlers::TestsInvocationDataDefStatus::kSuccess;
  std::vector<std::string> messages =
      api_proxy::models::RunTests(handler_match, dependencies.extra.secdist_,
                                  dependencies.pg_api_proxy->GetCluster());

  if (!messages.empty()) {
    response.status = handlers::TestsInvocationDataDefStatus::kFailure;
    response.messages = messages;
  }
  return response;
}

}  // namespace handlers::admin_v1_endpoints_tests::post
