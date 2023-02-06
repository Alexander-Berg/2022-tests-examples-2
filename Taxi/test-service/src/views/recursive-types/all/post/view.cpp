#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::recursive_types_all::post {

namespace {

template <class SourceT, class TargetT>
void CopyViaJson(const SourceT& source, TargetT& target) {
  formats::json::Value source_json =
      Serialize(source, formats::serialize::To<formats::json::Value>());

  target = Parse(std::move(source_json), formats::parse::To<TargetT>());
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns = clients::test_service::recursive_types_all::post;

  auto& client = dependencies.test_service_client;

  client_ns::Request client_req{};
  CopyViaJson(request.body, client_req.body);

  auto client_resp = client.RecursiveTypesAll(std::move(client_req));

  Response200 response{};
  CopyViaJson(client_resp.value, response.value);

  return response;
}

}  // namespace handlers::recursive_types_all::post
