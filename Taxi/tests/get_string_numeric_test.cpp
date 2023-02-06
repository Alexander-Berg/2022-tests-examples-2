#include <userver/utest/utest.hpp>

#include <utils/get_string_numeric.hpp>

#include <optional>

namespace eats_report_storage::utils {

struct GetStringNumericData {
  double numeric;
  int simbols_after_comma;
  std::string expected_result;
};

class GetStringNumericFull
    : public ::testing::TestWithParam<GetStringNumericData> {};

const std::vector<GetStringNumericData> kGetStringNumericData{
    {0, 0, "0"},
    {0, 2, "0"},
    {1.1, 0, "1"},
    {1.1, 1, "1.1"},
    {1.1, 2, "1.10"},
    {10000.1, 0, "10 000"},
    {10000.1, 1, "10 000.1"},
    {10000.1, 2, "10 000.10"},
    {100000, 0, "100 000"},
    {100000, 2, "100 000"},
    {100001.789789, 2, "100 001.79"},
    {100001.899999, 0, "100 002"},
    {100001.899999, 1, "100 001.9"},
    {100001.899999, 2, "100 001.90"},
    {-100001.899999, 0, "-100 002"},
    {-100001.899999, 1, "-100 001.9"},
    {-100001.899999, 2, "-100 001.90"},
    {-100001.123, 0, "-100 001"},
    {-100001.123, 1, "-100 001.1"},
    {-100001.123, 2, "-100 001.12"},
    {0.9999999, 0, "1"},
    {0.9999999, 1, "1"},
    {0.9999999, 2, "1"},
    {0.091, 0, "0"},
    {0.091, 1, "0.1"},
    {0.091, 2, "0.09"},
    {0.123456, 5, "0.12346"},
};

INSTANTIATE_TEST_SUITE_P(GetStringNumericData, GetStringNumericFull,
                         ::testing::ValuesIn(kGetStringNumericData));

TEST_P(GetStringNumericFull, function_should_return_string_numeric) {
  const auto& param = GetParam();
  ASSERT_EQ(GetStringNumeric(param.numeric, param.simbols_after_comma),
            param.expected_result);
}

struct GetStringNumericDataWithValueUnitSign {
  double numeric;
  int simbols_after_comma;
  std::optional<std::string> value_unit_sign;
  std::string expected_result;
};

class GetStringNumericWithValueUnitSignFull
    : public ::testing::TestWithParam<GetStringNumericDataWithValueUnitSign> {};

const std::vector<GetStringNumericDataWithValueUnitSign>
    kGetStringNumericDataWithValueUnitSign{
        {0, 0, "%", "0 %"},
        {100001.789789, 2, "%", "100 001.79 %"},
        {0.9999999, 2, "%", "1 %"},
        {0.9999999, 2, std::nullopt, "1"},
    };

INSTANTIATE_TEST_SUITE_P(
    GetStringNumericDataWithValueUnitSign,
    GetStringNumericWithValueUnitSignFull,
    ::testing::ValuesIn(kGetStringNumericDataWithValueUnitSign));

TEST_P(GetStringNumericWithValueUnitSignFull,
       function_should_return_string_numeric_with_value_unit_sign) {
  const auto& param = GetParam();
  ASSERT_EQ(
      GetStringNumericWithValueUnitSign(
          param.numeric, param.simbols_after_comma, param.value_unit_sign),
      param.expected_result);
}

struct GetUnbreakableNumericData {
  double numeric;
  int simbols_after_comma;
  std::optional<std::string> value_unit_sign;
  std::string expected_result;
};

class GetUnbreakableNumericFull
    : public ::testing::TestWithParam<GetUnbreakableNumericData> {};

const std::vector<GetUnbreakableNumericData> kGetUnbreakableNumericData{
    {0, 0, "%", "0&nbsp;%"},
    {100001.789789, 2, "%", "100&nbsp;001.79&nbsp;%"},
    {0.9999999, 2, "%", "1&nbsp;%"},
    {0.9999999, 2, std::nullopt, "1"},
};

INSTANTIATE_TEST_SUITE_P(GetUnbreakableNumericData, GetUnbreakableNumericFull,
                         ::testing::ValuesIn(kGetUnbreakableNumericData));

TEST_P(GetUnbreakableNumericFull,
       function_should_return_unbreaked_string_numeric) {
  const auto& param = GetParam();
  ASSERT_EQ(GetUnbreakableNumeric(param.numeric, param.simbols_after_comma,
                                  param.value_unit_sign),
            param.expected_result);
}

}  // namespace eats_report_storage::utils
