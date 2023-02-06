#pragma once

#include <unordered_map>

#include <userver/server/handlers/http_handler_json_base.hpp>

#include <kafka/components/consumer_component.hpp>

namespace kafka_consumer::components {

class TestsKafkaMessagesComponent final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  static constexpr auto kName = "tests-kafka-messages";

  void FindConsumerComponents(const ::components::ComponentConfig& config,
                              const ::components::ComponentContext& context);

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

  TestsKafkaMessagesComponent(const ::components::ComponentConfig& config,
                              const ::components::ComponentContext& context);

 private:
  std::unordered_map<std::string, kafka::KafkaConsumer&> consumers_;
};
}  // namespace kafka_consumer::components
