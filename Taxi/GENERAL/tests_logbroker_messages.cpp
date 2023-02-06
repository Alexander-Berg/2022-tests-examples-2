#include <logbroker-consumer/tests_logbroker_messages.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace logbroker_consumer {

TestsLogbrokerMessages::TestsLogbrokerMessages(
    const components::ComponentConfig& config,
    const components::ComponentContext& component_context)
    : server::handlers::HttpHandlerJsonBase(config, component_context),
      component_(FindConsumerComponent(config, component_context)) {}

Component& TestsLogbrokerMessages::FindConsumerComponent(
    const components::ComponentConfig& config,
    const components::ComponentContext& component_context) {
  auto consumer_component_name =
      config["consumer_component"].As<std::optional<std::string>>();
  return consumer_component_name ? component_context.FindComponent<Component>(
                                       *consumer_component_name)
                                 : component_context.FindComponent<Component>();
}

const std::string& TestsLogbrokerMessages::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value TestsLogbrokerMessages::HandleRequestJsonThrow(
    const server::http::HttpRequest& /*request*/,
    const formats::json::Value& request_body,
    server::request::RequestContext& /*context*/) const {
  auto consumer_name = request_body["consumer"].As<std::string>();
  auto consumer = component_.GetConsumer(consumer_name);

  std::string data;
  if (request_body.HasMember("data_b64"))
    data = crypto::base64::Base64Decode(
        request_body["data_b64"].As<std::string>());
  else
    data = request_body["data"].As<std::string>();
  auto topic = request_body["topic"].As<std::string>();
  auto cookie = request_body["cookie"].As<std::optional<std::string>>();

  const Offset offset = Offset{request_body.HasMember("offset")
                                   ? request_body["offset"].As<uint64_t>()
                                   : 0};
  Message::TimePoint create_time, write_time;
  const auto partition =
      request_body["partition"].As<std::optional<int>>().value_or(0);
  std::string source_id =
      request_body.HasMember("source_id") && !request_body["source_id"].IsNull()
          ? request_body["source_id"].As<std::string>()
          : "";
  uint64_t seq_no =
      request_body.HasMember("seq_no") && !request_body["seq_no"].IsNull()
          ? request_body["seq_no"].As<uint64_t>()
          : 0;

  auto message = std::make_unique<Message>(
      std::move(data), std::move(topic), create_time, write_time, offset,
      partition, source_id, seq_no, [cookie] {
        if (cookie) {
          TESTPOINT("logbroker_commit",
                    formats::json::ValueBuilder(*cookie).ExtractValue());
        }
      });

  consumer->PushMessageDebug(std::move(message));

  return {};
}

}  // namespace logbroker_consumer
