#include "system_info_holder_test_handler.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/formats/json.hpp>

namespace callcenter_queues::components {

SystemInfoHolderTestHandler::SystemInfoHolderTestHandler(
    const ::components::ComponentConfig& config,
    const ::components::ComponentContext& component_context)
    : server::handlers::HttpHandlerJsonBase(config, component_context),
      component_(component_context.FindComponent<SystemInfoHolder>()),
      enabled_(config["enabled"].As<bool>(false)) {}

const std::string& SystemInfoHolderTestHandler::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value SystemInfoHolderTestHandler::HandleRequestJsonThrow(
    const server::http::HttpRequest& /*request*/,
    const formats::json::Value& /*request_body*/,
    server::request::RequestContext& /*context*/) const {
  if (!enabled_) {
    return {};
  }
  // Just run one circle of checking and notifying
  auto system_info = component_.GetSystemInfo();
  formats::json::ValueBuilder result(formats::json::Type::kObject);
  result["subcluster_list"] = system_info.subcluster_list;
  if (system_info.metaqueues_info.empty()) {
    result["metaqueues_info"] = {formats::json::Type::kObject};
  } else {
    for (const auto& metaqueue : system_info.metaqueues_info) {
      std::vector<formats::json::Value> subs;
      for (const auto& sub_info : metaqueue.second.subclusters) {
        formats::json::ValueBuilder sub(formats::json::Type::kObject);
        sub["subcluster"] = sub_info.subcluster;
        sub["enabled_for_call_balancing"] = sub_info.enabled_for_call_balancing;
        sub["enabled_for_sip_user_autobalancing"] =
            sub_info.enabled_for_sip_user_autobalancing;
        sub["enabled"] = sub_info.enabled;
        subs.push_back(sub.ExtractValue());
      }
      result["metaqueues_info"][metaqueue.first]["subclusters"] = subs;
    }
  }
  return result.ExtractValue();
}

}  // namespace callcenter_queues::components
