#include "utils_test.hpp"
#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

namespace grocery_discounts_calculator {

formats::json::Value ReadFile(const std::string& name) {
  return formats::json::FromString(fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("src/tests/static/" + name)));
}

}  // namespace grocery_discounts_calculator
