#include <eventus/mappers/rms_history_test_mapper.hpp>

namespace eventus::mappers {

std::shared_ptr<HistoryClientWrapper> RmsHistoryMapper::CreateClientWrapperPtr(
    Client& client) {
  details::Handler<handler::Response200, handler::Request> handler_lambda =
      [&client](handler::Request request) {
        return client.V1EventsHistory(request);
      };
  details::ParseBody<handler::Body> parse_body_lambda =
      [](formats::json::Value& json) {
        return handler::Parse(json, formats::parse::To<handler::Body>{});
      };
  details::SerializeResponse<handler::Response200> serialize_response_lambda =
      [](handler::Response200& resp) {
        return handler::Serialize(
            resp, formats::serialize::To<formats::json::Value>{});
      };

  return std::make_shared<HistoryClientWrapper>(
      handler_lambda, parse_body_lambda, serialize_response_lambda);
}

}  // namespace eventus::mappers
