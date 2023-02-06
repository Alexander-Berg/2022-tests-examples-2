/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/configs/declarations/some/CONFIG.yaml

#include <codegen/impl/convert.hpp>
#include <codegen/impl/get_validation_length.hpp>
#include <codegen/impl/optional_convert.hpp>
#include <codegen/impl/parsers.hpp>
#include <cstring>
#include <taxi_config/variables/CONFIG.hpp>
#include <unordered_set>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/common/meta.hpp>
#include <userver/formats/json/serialize_variant.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/formats/parse/variant.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>
#include <userver/utils/underlying_value.hpp>

namespace taxi_config::config {

taxi_config::config::OneOfWithDiscriminator Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<taxi_config::config::OneOfWithDiscriminator>) {
  const auto discriminator = elem["type"].As<std::string>();
  if (discriminator == "def") {
    return taxi_config::config::OneOfWithDiscriminator{
        elem.As<taxi_config::dir_file::Def>(),
    };
  } else if (discriminator == "def2") {
    return taxi_config::config::OneOfWithDiscriminator{
        elem.As<taxi_config::dir_file::Def2>(),
    };
  } else {
    throw formats::json::Value::ParseException(
        "Value of discriminator '" + discriminator + "' for path '" +
        elem.GetPath() +
        "' does not match any known mapping from ['def', 'def2']");
  }
}

}

namespace taxi_config::config {

VariableType ParseVariable(const dynamic_config::DocsMap& docs_map) {
  return docs_map.Get("CONFIG").As<std::string>();
}

}