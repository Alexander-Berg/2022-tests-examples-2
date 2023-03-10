/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/uservices/libraries/test-lib/experiments3/declarations/test_exp.yaml

#pragma once

#include <experiments3/models/experiment_type.hpp>

#include <array>
#include <boost/type_traits/has_equal_to.hpp>
#include <codegen/convert_to_json_optional.hpp>
#include <codegen/format.hpp>
#include <codegen/parsing_flags.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log_helper_fwd.hpp>

#include <codegen/parser/datetime_parser.hpp>
#include <codegen/parser/dummy_parser.hpp>  // TODO: for debug only
#include <codegen/parser/enum_parser.hpp>
#include <codegen/parser/extra_helper.hpp>
#include <codegen/parser/null_swallow.hpp>
#include <codegen/parser/nullable_helper.hpp>
#include <codegen/parser/parser_converter.hpp>
#include <codegen/parser/parser_dom.hpp>
#include <codegen/parser/parser_empty.hpp>
#include <codegen/parser/parser_non_null_ptr.hpp>
#include <codegen/parser/validator.hpp>
#include <codegen/parser/value_builder_helper.hpp>
#include <userver/formats/json/parser/parser.hpp>

namespace experiments3 {
struct TestExp {
  using Value = int;
  enum class Type { kExperiment, kConfig, kUnion };
  static constexpr auto kType = Type::kExperiment;
  static constexpr bool kCacheResult = false;
  static const std::string kName;
};
}
