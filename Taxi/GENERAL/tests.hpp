#pragma once

#include <string>

namespace eats_adverts_goods::utils::tests {

// @brief Возвращает название теста, которое можно зарегистрировать в utest.
template <typename TestParam>
std::string GetName(TestParam&& test_param) {
  std::string name(test_param.name);
  for (auto& ch : name) {
    if (ch == ' ' || ch == ',' || ch == '-') {
      ch = '_';
    }
  }
  return name;
}

}  // namespace eats_adverts_goods::utils::tests
