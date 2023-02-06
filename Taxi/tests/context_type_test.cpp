#include <cargo_custom_contexts/cargo_custom_contexts.hpp>
#include <cargo_custom_contexts/errors.hpp>

#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>

#include "constants.hpp"

using namespace cargo_custom_contexts;
using namespace test_constants;

struct ContextTypeParam {
  formats::json::Value value;
  std::optional<ContextType> expected_type;
  std::string test_name;
};

class ContextTypeTest : public testing::TestWithParam<ContextTypeParam> {};

const std::vector<ContextTypeParam> kTestParams = {
    {kEatsCustomContextWithoutTypeJson, std::nullopt, "EatsWithoutType"},
    {kEatsCustomContextWithTypeJson, ContextType::kEats, "EatsWithType"},
    {kGroceryCustomContextWithoutTypeJson, std::nullopt, "GroceryWithoutType"},
    {kGroceryCustomContextWithTypeJson, ContextType::kGrocery,
     "GroceryWithType"},
};

TEST_P(ContextTypeTest, TryGetContextType) {
  const auto& param = GetParam();
  const auto& result = TryGetContextType(param.value);
  ASSERT_EQ(result, param.expected_type);
}

TEST_P(ContextTypeTest, GetContextType) {
  const auto& param = GetParam();
  if (param.expected_type.has_value()) {
    ASSERT_EQ(GetContextType(param.value), param.expected_type.value());
  } else {
    ASSERT_THROW(GetContextType(param.value), ArgumentException);
  }
}

INSTANTIATE_TEST_SUITE_P(CargoCustomContextsLib, ContextTypeTest,
                         testing::ValuesIn(kTestParams),
                         utest::PrintTestName());
