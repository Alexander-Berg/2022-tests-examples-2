#include "docs_map.hpp"

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json.hpp>

namespace loyalty {

formats::json::Value MockLocalesSupported() {
  formats::json::ValueBuilder json = formats::json::Type::kArray;
  json.PushBack("ru");
  json.PushBack("en");
  json.PushBack("hy");
  json.PushBack("ka");
  return json.ExtractValue();
}

formats::json::Value MockLocalesMapping() {
  formats::json::ValueBuilder json = formats::json::Type::kObject;
  json["be"] = "ru";
  return json.ExtractValue();
}

dynamic_config::DocsMap DocsMapForTest() {
  dynamic_config::DocsMap docs_map;
  docs_map.Set("LOCALES_SUPPORTED", MockLocalesSupported());
  docs_map.Set("LOCALES_MAPPING", MockLocalesMapping());
  return docs_map;
}

}  // namespace loyalty
