#pragma once

#include <string>

#include <gtest/gtest.h>

namespace eats_adverts_places::utils::test {

template <typename TestCase>
std::string GetName(const TestCase& test_case) {
  std::string result = test_case.name;
  for (auto& ch : result) {
    if (ch == ' ' || ch == ',' || ch == '-') {
      ch = '_';
    }
  }
  return result;
}

}  // namespace eats_adverts_places::utils::test
