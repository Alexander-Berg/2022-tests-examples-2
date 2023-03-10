/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/configs/declarations/CLIENT_TEST_SERVICE_CLIENT_QOS.yaml

#pragma once

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/value.hpp>

#include <array>
#include <boost/type_traits/has_equal_to.hpp>
#include <chrono>
#include <codegen/convert_to_json_optional.hpp>
#include <codegen/format.hpp>
#include <codegen/parsing_flags.hpp>
#include <optional>
#include <string>
#include <unordered_map>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log_helper_fwd.hpp>

namespace taxi_config::client_test_service_client_qos {

struct QosInfo {
  int attempts{};
  ::std::chrono::milliseconds timeout_ms{};
};

QosInfo Parse(const formats::json::Value& elem, formats::parse::To<QosInfo>);

template <typename U>
std::enable_if_t<std::is_same<U, QosInfo>::value, bool> operator==(const U& lhs,
                                                                   const U& rhs)
{
  // template magic identifies whether all struct fields are comparable
  static_assert(boost::has_equal_to<decltype(lhs.attempts)>::value,
                "No operator==() defined for field 'attempts' of type 'int'");
  static_assert(boost::has_equal_to<decltype(lhs.timeout_ms)>::value,
                "No operator==() defined for field 'timeout_ms' of type "
                "'::std::chrono::milliseconds'");

  return std::tie(lhs.attempts, lhs.timeout_ms) ==
         std::tie(rhs.attempts, rhs.timeout_ms);
}

template <typename U>
std::enable_if_t<std::is_same<U, QosInfo>::value, bool> operator!=(const U& lhs,
                                                                   const U& rhs)
{
  return !(lhs == rhs);
}

}

namespace taxi_config::client_test_service_client_qos {

using VariableType = ::dynamic_config::ValueDict<
    taxi_config::client_test_service_client_qos::QosInfo>;

VariableType ParseVariable(const dynamic_config::DocsMap&);

}

namespace taxi_config {

inline constexpr dynamic_config::Key<
    client_test_service_client_qos::ParseVariable>
    CLIENT_TEST_SERVICE_CLIENT_QOS;

}
