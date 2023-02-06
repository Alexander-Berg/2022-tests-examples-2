#pragma once

#include <string>

namespace eats_upsell::utils {

/// @struct Функтор, возвращающий название сценария теста.
template <typename TestCase>
struct GetTestNameOp {
  std::string operator()(const TestCase& test_case) const {
    return test_case.param.name;
  }
};

/// @brief Возвращает название теста, которое может распознать gtest.
template <typename TestCase, typename GetNameOp = GetTestNameOp<TestCase>>
std::string GetTestName(const TestCase& test_case,
                        GetNameOp get_name_op = GetTestNameOp<TestCase>()) {
  auto result = get_name_op(test_case);
  for (auto& ch : result) {
    if (ch == ' ' || ch == ',' || ch == '-') {
      ch = '_';
    }
  }
  return result;
}

}  // namespace eats_upsell::utils
