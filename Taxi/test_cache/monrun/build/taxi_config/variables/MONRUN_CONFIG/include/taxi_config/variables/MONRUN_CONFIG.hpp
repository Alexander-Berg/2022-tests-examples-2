/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/configs/declarations/locales/MONRUN_CONFIG.yaml

#pragma once

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/value.hpp>

#include <array>
#include <boost/type_traits/has_equal_to.hpp>
#include <codegen/convert_to_json_optional.hpp>
#include <codegen/format.hpp>
#include <codegen/parsing_flags.hpp>
#include <string>
#include <unordered_map>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log_helper_fwd.hpp>

namespace taxi_config::monrun_config {

struct MonrunConfig {
  ::std::unordered_map<std::string, ::std::string> extra{};
};

MonrunConfig Parse(
    const formats::json::Value& elem, formats::parse::To<MonrunConfig>,
    ::codegen::ParsingFlags flags = ::codegen::ParsingFlags::kParseExtra);

template <typename U>
std::enable_if_t<std::is_same<U, MonrunConfig>::value, bool> operator==(
    const U& lhs, const U& rhs)
{
  // template magic identifies whether all struct fields are comparable
  static_assert(boost::has_equal_to<decltype(lhs.extra)>::value,
                "No operator==() defined for field 'extra' of type "
                "'::std::unordered_map<std::string, ::std::string>'");

  return std::tie(lhs.extra) == std::tie(rhs.extra);
}

template <typename U>
std::enable_if_t<std::is_same<U, MonrunConfig>::value, bool> operator!=(
    const U& lhs, const U& rhs)
{
  return !(lhs == rhs);
}

}

namespace taxi_config::monrun_config {

using VariableType = ::taxi_config::monrun_config::MonrunConfig;

VariableType ParseVariable(const dynamic_config::DocsMap&);

}

namespace taxi_config {

inline constexpr dynamic_config::Key<monrun_config::ParseVariable>
    MONRUN_CONFIG;

}
