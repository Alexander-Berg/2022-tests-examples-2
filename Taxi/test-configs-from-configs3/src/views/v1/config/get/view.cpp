#include "view.hpp"

#include <handlers/dependencies.hpp>
#include <taxi_config/variables/EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT.hpp>
#include <taxi_config/variables/EXPERIMENTS3_CLIENT_DISABLE_API_KEY.hpp>
#include <taxi_config/variables/EXPERIMENTS3_COMMON_LIBRARY_SETTINGS.hpp>

#include <userver/formats/serialize/common_containers.hpp>

namespace handlers::v1_config::get {

Response View::Handle(Request&& request, Dependencies&& deps) {
  formats::json::ValueBuilder builder;
  if (request.name == "EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT") {
    builder["value"] =
        deps.config[taxi_config::EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT];
  } else if (request.name == "EXPERIMENTS3_CLIENT_DISABLE_API_KEY") {
    builder["value"] =
        deps.config[taxi_config::EXPERIMENTS3_CLIENT_DISABLE_API_KEY];
  } else if (request.name == "EXPERIMENTS3_COMMON_LIBRARY_SETTINGS") {
    const auto& value =
        deps.config[taxi_config::EXPERIMENTS3_COMMON_LIBRARY_SETTINGS];
    auto general_settings = builder["value"]["general_settings"];
    general_settings["mandatory_config_loading_retries"] =
        value.general_settings.mandatory_config_loading_retries;
    general_settings["mandatory_config_loading_retry_timeout"] =
        value.general_settings.mandatory_config_loading_retry_timeout.count();
    if (value.features) {
      builder["value"]["features"] = value.features->extra;
    }
  } else {
    throw std::runtime_error("Bad config name: " + request.name);
  }

  Response200 response;
  response.extra = builder.ExtractValue();
  return response;
}

}  // namespace handlers::v1_config::get
