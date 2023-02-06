#include "subcluster_loadness_calculator_test_handler.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/formats/json.hpp>

namespace callcenter_queues::components {

SubclusterLoadnessCalculatorTestHandler::
    SubclusterLoadnessCalculatorTestHandler(
        const ::components::ComponentConfig& config,
        const ::components::ComponentContext& component_context)
    : server::handlers::HttpHandlerJsonBase(config, component_context),
      component_(
          component_context.FindComponent<SubclusterLoadnessCalculator>()),
      enabled_(config["enabled"].As<bool>(false)) {}

const std::string& SubclusterLoadnessCalculatorTestHandler::HandlerName()
    const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value
SubclusterLoadnessCalculatorTestHandler::HandleRequestJsonThrow(
    const server::http::HttpRequest& /*request*/,
    const formats::json::Value& /*request_body*/,
    server::request::RequestContext& /*context*/) const {
  if (!enabled_) {
    return {};
  }
  // Just run one circle of checking and notifying
  auto loadness = component_.GetLoadness();
  auto counters = component_.GetCounters();
  formats::json::ValueBuilder result(formats::json::Type::kObject);
  for (const auto& metaqueue : loadness) {
    for (const auto& subcluster : loadness.at(metaqueue.first)) {
      result["loadness"][metaqueue.first][subcluster.first] =
          loadness.at(metaqueue.first).at(subcluster.first);
    }
  }
  for (const auto& [subcluster, counter] : counters.subclusters_counters) {
    result["counters"]["by_subclusters"][subcluster]["total"] = counter.total;
    result["counters"]["by_subclusters"][subcluster]["paused"] = counter.paused;
    result["counters"]["by_subclusters"][subcluster]["connected"] =
        counter.connected;
  }
  for (const auto& [metaqueue, counter] : counters.metaqueues_counters) {
    result["counters"]["by_metaqueues"][metaqueue]["total"] = counter.total;
    result["counters"]["by_metaqueues"][metaqueue]["paused"] = counter.paused;
    result["counters"]["by_metaqueues"][metaqueue]["connected"] =
        counter.connected;
  }
  for (const auto& [metaqueue, metaqueue_to_subclusters] :
       counters.queues_counters) {
    for (const auto& [subcluster, counter] : metaqueue_to_subclusters) {
      result["counters"]["by_queues"][metaqueue][subcluster]["total"] =
          counter.total;
      result["counters"]["by_queues"][metaqueue][subcluster]["paused"] =
          counter.paused;
      result["counters"]["by_queues"][metaqueue][subcluster]["connected"] =
          counter.connected;
    }
  }
  return result.ExtractValue();
}

}  // namespace callcenter_queues::components
