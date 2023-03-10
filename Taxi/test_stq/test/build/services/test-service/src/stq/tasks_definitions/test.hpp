/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/uservices/services/test-service/docs/stq/test.yaml

#pragma once

#include <array>
#include <boost/type_traits/has_equal_to.hpp>
#include <chrono>
#include <codegen/convert_to_json_optional.hpp>
#include <codegen/format.hpp>
#include <codegen/non_null_ptr.hpp>
#include <codegen/parsing_flags.hpp>
#include <optional>
#include <stq/tasks_definitions/test_definitions.hpp>
#include <string>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log_helper_fwd.hpp>
#include <vector>

namespace stq_tasks::test {

struct Args {
  ::std::string simple_string{};
  ::std::vector<std::string> array{};
  ::std::optional<double> optional_number{};
  ::std::optional<::stq_tasks::test_definitions::TestObject> object_field{};
  ::std::optional<::std::chrono::system_clock::time_point> datetime_field{};
};

::formats::json::Value Serialize(
    const stq_tasks::test::Args& value,
    ::formats::serialize::To<::formats::json::Value>);

void WriteToStream(const stq_tasks::test::Args& value,
                   formats::json::StringBuilder& sw, bool hide_brackets = false,
                   const char* hide_field_name = nullptr);

Args Parse(const formats::json::Value& elem, formats::parse::To<Args>);

}
