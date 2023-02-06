#include <kafka/components/tests_kafka_messages.hpp>
#include <kafka/kafka.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/parse/common_containers.hpp>

namespace kafka_consumer::components {

TestsKafkaMessagesComponent::TestsKafkaMessagesComponent(
    const ::components::ComponentConfig& config,
    const ::components::ComponentContext& context)
    : server::handlers::HttpHandlerJsonBase(config, context) {
  FindConsumerComponents(config, context);
}

void TestsKafkaMessagesComponent::FindConsumerComponents(
    const ::components::ComponentConfig& config,
    const ::components::ComponentContext& context) {
  auto consumer_names = config["consumers_list"].As<std::vector<std::string>>();
  for (const auto& name : consumer_names) {
    consumers_.emplace(
        name,
        context.FindComponent<KafkaConsumerComponent>(name).GetConsumer());
  }
}

const std::string& TestsKafkaMessagesComponent::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value TestsKafkaMessagesComponent::HandleRequestJsonThrow(
    const server::http::HttpRequest& request,
    const formats::json::Value& request_body,
    server::request::RequestContext& /*context*/) const {
  kafka::MessagePolled polled_message;
  if (request_body.HasMember("data_b64")) {
    polled_message.payload = crypto::base64::Base64Decode(
        request_body["data_b64"].As<std::string>());
  } else {
    polled_message.payload = request_body["data"].As<std::string>();
  }
  polled_message.topic = request_body["topic"].As<std::string>();
  polled_message.topic =
      request_body["key"].As<std::optional<std::string>>().value_or("");
  consumers_.at(request.GetPathArg("component_name"))
      .PushTestMessage(std::move(polled_message));
  return {};
}

}  // namespace kafka_consumer::components
