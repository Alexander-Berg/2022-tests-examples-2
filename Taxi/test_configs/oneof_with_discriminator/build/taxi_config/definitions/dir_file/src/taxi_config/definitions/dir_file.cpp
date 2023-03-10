/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/configs/definitions/dir/file.yaml

#include <taxi_config/definitions/dir_file.hpp>

#include <codegen/impl/convert.hpp>
#include <codegen/impl/get_validation_length.hpp>
#include <codegen/impl/optional_convert.hpp>
#include <codegen/impl/parsers.hpp>
#include <cstring>
#include <unordered_set>
#include <userver/formats/common/meta.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>
#include <userver/utils/underlying_value.hpp>

namespace taxi_config::dir_file {

taxi_config::dir_file::Def2 Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<taxi_config::dir_file::Def2>) {
  taxi_config::dir_file::Def2 result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.type = elem["type"].As<std::optional<::std::string>>();

  return result;
}

}
namespace taxi_config::dir_file {

taxi_config::dir_file::Def Parse(
    [[maybe_unused]] const formats::json::Value& elem,
    formats::parse::To<taxi_config::dir_file::Def>) {
  taxi_config::dir_file::Def result;

  elem.CheckNotMissing();
  elem.CheckObjectOrNull();

  result.type = elem["type"].As<std::optional<::std::string>>();

  return result;
}

}
