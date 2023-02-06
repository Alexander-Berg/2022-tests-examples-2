#include <fmt/format.h>
#include <gtest/gtest.h>
#include <tuple>
#include <utils/weight.hpp>

using eats_full_text_search_indexer::utils::GetWeightInGrams;

std::string ToString(const std::optional<uint64_t> value_opt) {
  if (value_opt.has_value()) {
    return std::to_string(value_opt.value());
  }
  return "nullopt";
}

::testing::AssertionResult CheckResult(const std::string& input,
                                       std::optional<uint64_t> expected,
                                       std::optional<uint64_t> result) {
  const auto error_msg =
      fmt::format("input: {}, expected {}, but got {}", input,
                  ToString(expected), ToString(result));

  if (expected.has_value() != result.has_value()) {
    return ::testing::AssertionFailure() << error_msg;
  }

  if (expected.has_value() && expected.value() != result.value()) {
    return ::testing::AssertionFailure() << error_msg;
  }

  return ::testing::AssertionSuccess();
}

TEST(Weight, Parse) {
  std::vector<std::tuple<std::string, std::optional<uint64_t>>> test_cases = {
      {"100 гр", 100},
      {"100 ГР", 100},
      {"100 г", 100},
      {"100 гр.", 100},
      {"100 GRM", 100},
      {"100г", 100},
      {"100 мл", 100},
      {"100 MLT", 100},
      {"1 кг", 1000},
      {"1 KGRM", 1000},
      {"1 kgrm", 1000},
      {"1 л", 1000},
      {"1 LT", 1000},
      {"1,00 кг", 1000},
      {"1,51 кг", 1510},
      {"1,51 г", 1},
      {"1.0 кг", 1000},
      {"0 кг", 0},
      {"0 г", 0},
      {"-1 кг", std::nullopt},
      {"1 килограмм", std::nullopt},
      {"кг", std::nullopt},
      {"1 пачка", std::nullopt},
      {"1 рулон", std::nullopt},
      {"1 шт.", std::nullopt},
      {"1шт. / 100г", std::nullopt},
      {"1000", std::nullopt},
      {"без веса", std::nullopt},
      {"", std::nullopt},
      {"-", std::nullopt},
  };

  for (const auto& [input, expected_result] : test_cases) {
    const auto result = GetWeightInGrams(input);
    EXPECT_TRUE(CheckResult(input, expected_result, result));
  }
}
