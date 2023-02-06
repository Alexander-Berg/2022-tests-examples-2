#include "test_helpers.hpp"

#include <algorithm>

#include <userver/utils/text.hpp>

namespace eventus::operations::details::test_helpers {

std::string PrintOperationArg(const eventus::common::OperationArgument& arg,
                              int idx) {
  std::string result;
  const auto name = arg.name.value_or("arg" + std::to_string(idx));
  if (std::holds_alternative<bool>(arg.value)) {
    const auto value = std::get<bool>(arg.value);
    result += name + "-" + (value ? std::string("true") : std::string("false"));
  } else if (std::holds_alternative<std::vector<bool>>(arg.value)) {
    const auto value = std::get<std::vector<bool>>(arg.value);
    std::vector<std::string> value_str;
    std::transform(value.begin(), value.end(), std::back_inserter(value_str),
                   [](const bool& v) {
                     return (v ? std::string("true") : std::string("false"));
                   });
    result += name + "-" + utils::text::Join(value_str, ",");
  } else if (std::holds_alternative<std::vector<std::string>>(arg.value)) {
    const auto value = std::get<std::vector<std::string>>(arg.value);
    result += name + "-" + utils::text::Join(value, ",");
  } else if (std::holds_alternative<std::string>(arg.value)) {
    const auto value = std::get<std::string>(arg.value);
    result += name + "-" + value;
  } else if (std::holds_alternative<std::vector<double>>(arg.value)) {
    const auto value = std::get<std::vector<double>>(arg.value);
    std::vector<std::string> value_str;
    std::transform(value.begin(), value.end(), std::back_inserter(value_str),
                   [](const double& v) { return std::to_string(v); });
    result += name + "-" + utils::text::Join(value_str, ",");
  } else if (std::holds_alternative<double>(arg.value)) {
    const auto value = std::get<double>(arg.value);
    result += name + "-" + std::to_string(value);
  } else {
    result += name + "-unknown_type";
  }
  return result;
}

std::string PrintOperationArgs(const OperationArgsV& args) {
  std::string result = "";
  std::string_view sep = "";
  int idx = 0;
  for (const auto& arg : args) {
    result += sep;
    result += PrintOperationArg(arg, idx++);
    sep = "__";
  }
  std::replace_if(
      result.begin(), result.end(),
      [](const char ch) { return !isalnum(ch) && ch != '_'; }, '_');
  return result;
}

}  // namespace eventus::operations::details::test_helpers
