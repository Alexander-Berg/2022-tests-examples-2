#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/validate_request.hpp>

namespace eats_restapp_promo::utils {

struct TestSettingsValue {
  std::optional<bool> required;
  std::optional<int> min_value;
  std::optional<int> max_value;
  std::optional<unsigned int> min_size;
  std::optional<unsigned int> max_size;
  std::optional<int> min_value_day;
  std::optional<int> max_value_day;
  std::optional<int> min_value_time;
  std::optional<int> max_value_time;
};

struct CheckRequiredData {
  std::optional<int> value;
  std::optional<bool> required;
  bool is_throw;
};

class CheckRequiredDataFull
    : public ::testing::TestWithParam<CheckRequiredData> {};

const std::vector<CheckRequiredData> kCheckRequiredData{
    {{}, {}, false},  {1, {}, false},   {{}, false, false},
    {1, false, true}, {{}, true, true}, {1, true, false},
};

INSTANTIATE_TEST_SUITE_P(CheckRequiredData, CheckRequiredDataFull,
                         ::testing::ValuesIn(kCheckRequiredData));

TEST_P(CheckRequiredDataFull, CheckRequired) {
  auto param = GetParam();
  TestSettingsValue settings;
  settings.required = param.required;
  if (param.is_throw) {
    ASSERT_THROW(CheckRequired(param.value,
                               std::optional<TestSettingsValue>{settings}, {}),
                 models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckRequired(
        param.value, std::optional<TestSettingsValue>{settings}, {}));
  }
}

TEST(CheckRequiredDataFull, CheckNullSettings) {
  std::optional<TestSettingsValue> settings;
  ASSERT_NO_THROW(CheckRequired(std::optional<int>{}, settings, {}));
  ASSERT_NO_THROW(CheckRequired(std::optional<int>{1}, settings, {}));
}

struct CheckValueRangeData {
  int value;
  std::optional<int> min;
  std::optional<int> max;
  bool is_throw;
};

class CheckValueRangeDataFull
    : public ::testing::TestWithParam<CheckValueRangeData> {};

const std::vector<CheckValueRangeData> kCheckValueRangeData{
    {3, {}, {}, false}, {3, 2, {}, false}, {3, {}, 4, false},
    {3, 2, 4, false},   {3, 3, 3, false},  {3, 4, {}, true},
    {3, {}, 2, true},   {3, 5, 6, true},   {3, 1, 2, true},
};

INSTANTIATE_TEST_SUITE_P(CheckValueRangeData, CheckValueRangeDataFull,
                         ::testing::ValuesIn(kCheckValueRangeData));

TEST_P(CheckValueRangeDataFull, CheckValueRange) {
  auto param = GetParam();
  if (param.is_throw) {
    ASSERT_THROW(CheckValueRange(param.value, param.min, param.max, {}),
                 models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckValueRange(param.value, param.min, param.max, {}));
  }
}

struct CheckRequestValueData {
  std::optional<int> value;
  std::optional<int> min_value;
  std::optional<int> max_value;
  bool is_throw;
};

class CheckRequestValueDataFull
    : public ::testing::TestWithParam<CheckRequestValueData> {};

const std::vector<CheckRequestValueData> kCheckRequestValueData{
    {{}, {}, {}, false}, {{}, 1, {}, false}, {{}, {}, 2, false},
    {{}, 1, 2, false},   {3, {}, {}, false}, {3, 2, {}, false},
    {3, {}, 4, false},   {3, 2, 4, false},   {3, 3, 3, false},
    {3, 4, {}, true},    {3, {}, 2, true},   {3, 5, 6, true},
    {3, 1, 2, true},
};

INSTANTIATE_TEST_SUITE_P(CheckRequestValueData, CheckRequestValueDataFull,
                         ::testing::ValuesIn(kCheckRequestValueData));

TEST_P(CheckRequestValueDataFull, CheckRequestValue) {
  auto param = GetParam();
  TestSettingsValue settings;
  settings.min_value = param.min_value;
  settings.max_value = param.max_value;
  if (param.is_throw) {
    ASSERT_THROW(
        CheckRequestValue(param.value,
                          std::optional<TestSettingsValue>{settings}, {}),
        models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckRequestValue(
        param.value, std::optional<TestSettingsValue>{settings}, {}));
  }
}

TEST(CheckRequestValueDataFull, CheckNullSettings) {
  std::optional<TestSettingsValue> settings;
  ASSERT_NO_THROW(CheckRequestValue(std::optional<int>{}, settings, {}));
  ASSERT_NO_THROW(CheckRequestValue(std::optional<int>{1}, settings, {}));
}

struct CheckRequestValuesSizeData {
  std::optional<std::vector<int>> value;
  std::optional<unsigned int> min_size;
  std::optional<unsigned int> max_size;
  bool is_throw;
};

class CheckRequestValuesSizeDataFull
    : public ::testing::TestWithParam<CheckRequestValuesSizeData> {};

const std::vector<CheckRequestValuesSizeData> kCheckRequestValuesSizeData{
    {std::nullopt, {}, {}, false},
    {std::nullopt, 1, {}, false},
    {std::nullopt, {}, 2, false},
    {std::nullopt, 1, 2, false},
    {std::vector<int>{}, {}, {}, false},
    {std::vector<int>{}, 1, {}, true},
    {std::vector<int>{}, 0, {}, false},
    {std::vector<int>{}, {}, 1, false},
    {std::vector<int>{}, 1, 2, true},
    {std::vector<int>{}, 0, 2, false},
    {std::vector<int>{1, 2}, {}, {}, false},
    {std::vector<int>{1, 2}, 1, {}, false},
    {std::vector<int>{1, 2}, 3, {}, true},
    {std::vector<int>{1, 2}, {}, 3, false},
    {std::vector<int>{1, 2}, {}, 1, true},
    {std::vector<int>{1, 2}, 3, 4, true},
    {std::vector<int>{1, 2}, 0, 1, true},
    {std::vector<int>{1, 2}, 0, 4, false},
};

INSTANTIATE_TEST_SUITE_P(CheckRequestValuesSizeData,
                         CheckRequestValuesSizeDataFull,
                         ::testing::ValuesIn(kCheckRequestValuesSizeData));

TEST_P(CheckRequestValuesSizeDataFull, CheckRequestValuesSize) {
  auto param = GetParam();
  TestSettingsValue settings;
  settings.min_size = param.min_size;
  settings.max_size = param.max_size;
  if (param.is_throw) {
    ASSERT_THROW(
        CheckRequestValuesSize(param.value,
                               std::optional<TestSettingsValue>{settings}, {}),
        models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckRequestValuesSize(
        param.value, std::optional<TestSettingsValue>{settings}, {}));
  }
}

TEST(CheckRequestValuesSizeDataFull, CheckNullSettings) {
  std::optional<TestSettingsValue> settings;
  ASSERT_NO_THROW(
      CheckRequestValuesSize(std::optional<std::vector<int>>{}, settings, {}));
  ASSERT_NO_THROW(
      CheckRequestValuesSize(std::optional<std::vector<int>>{1}, settings, {}));
}

struct CheckRequestValuesData {
  std::optional<std::vector<int>> value;
  std::optional<unsigned int> min_size;
  std::optional<unsigned int> max_size;
  std::optional<int> min_value;
  std::optional<int> max_value;
  bool is_throw;
};

class CheckRequestValuesDataFull
    : public ::testing::TestWithParam<CheckRequestValuesData> {};

const std::vector<CheckRequestValuesData> kCheckRequestValuesData{
    {std::nullopt, {}, {}, {}, {}, false},
    {std::nullopt, 1, {}, {}, {}, false},
    {std::nullopt, {}, 2, {}, {}, false},
    {std::nullopt, 1, 2, {}, {}, false},
    {std::vector<int>{}, {}, {}, {}, {}, false},
    {std::vector<int>{}, 1, {}, {}, {}, true},
    {std::vector<int>{}, 0, {}, {}, {}, false},
    {std::vector<int>{}, {}, 1, {}, {}, false},
    {std::vector<int>{}, 1, 2, {}, {}, true},
    {std::vector<int>{}, 0, 2, {}, {}, false},
    {std::vector<int>{1, 2}, {}, {}, {}, {}, false},
    {std::vector<int>{1, 2}, 1, {}, {}, {}, false},
    {std::vector<int>{1, 2}, 3, {}, {}, {}, true},
    {std::vector<int>{1, 2}, {}, 3, {}, {}, false},
    {std::vector<int>{1, 2}, {}, 1, {}, {}, true},
    {std::vector<int>{1, 2}, 3, 4, {}, {}, true},
    {std::vector<int>{1, 2}, 0, 4, {}, {}, false},
    {std::vector<int>{}, {}, {}, 1, 2, false},
    {std::vector<int>{1, 2}, {}, {}, 3, 4, true},
    {std::vector<int>{3, 4}, {}, {}, 1, 2, true},
    {std::vector<int>{1, 2}, {}, {}, 2, {}, true},
    {std::vector<int>{1, 2}, {}, {}, {}, 1, true},
    {std::vector<int>{5, 3, 7}, {}, {}, 5, 7, true},
    {std::vector<int>{5, 6, 7}, {}, {}, 5, 7, false},
};

INSTANTIATE_TEST_SUITE_P(CheckRequestValuesData, CheckRequestValuesDataFull,
                         ::testing::ValuesIn(kCheckRequestValuesData));

TEST_P(CheckRequestValuesDataFull, CheckRequestValues) {
  auto param = GetParam();
  TestSettingsValue settings;
  settings.min_size = param.min_size;
  settings.max_size = param.max_size;
  settings.min_value = param.min_value;
  settings.max_value = param.max_value;
  if (param.is_throw) {
    ASSERT_THROW(
        CheckRequestValues(param.value,
                           std::optional<TestSettingsValue>{settings}, {}),
        models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckRequestValues(
        param.value, std::optional<TestSettingsValue>{settings}, {}));
  }
}

TEST(CheckRequestValuesDataFull, CheckNullSettings) {
  std::optional<TestSettingsValue> settings;
  ASSERT_NO_THROW(
      CheckRequestValues(std::optional<std::vector<int>>{}, settings, {}));
  ASSERT_NO_THROW(
      CheckRequestValues(std::optional<std::vector<int>>{1}, settings, {}));
}

struct CheckRequestSchedulesData {
  std::optional<std::vector<handlers::PromoSchedule>> value;
  std::optional<unsigned int> min_size;
  std::optional<unsigned int> max_size;
  std::optional<int> min_value_day;
  std::optional<int> max_value_day;
  std::optional<int> min_value_time;
  std::optional<int> max_value_time;
  bool is_throw;
};

class CheckRequestSchedulesDataFull
    : public ::testing::TestWithParam<CheckRequestSchedulesData> {};

const std::vector<CheckRequestSchedulesData> kCheckRequestSchedulesData{
    {std::nullopt, {}, {}, {}, {}, {}, {}, false},
    {std::nullopt, 1, {}, {}, {}, {}, {}, false},
    {std::nullopt, {}, 2, {}, {}, {}, {}, false},
    {std::nullopt, 1, 2, {}, {}, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{}, {}, {}, {}, {}, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{}, 1, {}, {}, {}, {}, {}, true},
    {std::vector<handlers::PromoSchedule>{}, 0, {}, {}, {}, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{}, {}, 1, {}, {}, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{}, 1, 2, {}, {}, {}, {}, true},
    {std::vector<handlers::PromoSchedule>{}, 0, 2, {}, {}, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     {},
     {},
     {},
     {},
     {},
     false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     1,
     {},
     {},
     {},
     {},
     {},
     false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     3,
     {},
     {},
     {},
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     3,
     {},
     {},
     {},
     {},
     false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     1,
     {},
     {},
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     3,
     4,
     {},
     {},
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     0,
     4,
     {},
     {},
     {},
     {},
     false},
    {std::vector<handlers::PromoSchedule>{}, {}, {}, 1, 2, {}, {}, false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     {},
     3,
     4,
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{3, 10, 15}, {4, 20, 25}},
     {},
     {},
     1,
     2,
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     {},
     2,
     {},
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 15}, {2, 20, 25}},
     {},
     {},
     {},
     1,
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 10, 15}, {3, 20, 25}, {7, 30, 35}},
     {},
     {},
     5,
     7,
     {},
     {},
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 10, 15}, {6, 20, 25}, {7, 30, 35}},
     {},
     {},
     5,
     7,
     {},
     {},
     false},

    {std::vector<handlers::PromoSchedule>{}, {}, {}, {}, {}, 1, 2, false},
    {std::vector<handlers::PromoSchedule>{{1, 10, 35}, {2, 20, 35}},
     {},
     {},
     {},
     {},
     30,
     40,
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 3}, {2, 20, 3}},
     {},
     {},
     {},
     {},
     0,
     5,
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 25}, {2, 20, 25}},
     {},
     {},
     {},
     {},
     20,
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 10}, {2, 20, 10}},
     {},
     {},
     {},
     {},
     {},
     10,
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 10, 15}, {3, 20, 15}, {7, 30, 35}},
     {},
     {},
     {},
     {},
     9,
     29,
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 10, 15}, {6, 20, 15}, {7, 30, 15}},
     {},
     {},
     {},
     {},
     10,
     30,
     false},

    {std::vector<handlers::PromoSchedule>{}, {}, {}, {}, {}, 1, 2, false},
    {std::vector<handlers::PromoSchedule>{{1, 35, 10}, {2, 35, 20}},
     {},
     {},
     {},
     {},
     30,
     40,
     true},
    {std::vector<handlers::PromoSchedule>{{1, 3, 10}, {2, 3, 20}},
     {},
     {},
     {},
     {},
     0,
     5,
     true},
    {std::vector<handlers::PromoSchedule>{{1, 25, 10}, {2, 25, 20}},
     {},
     {},
     {},
     {},
     20,
     {},
     true},
    {std::vector<handlers::PromoSchedule>{{1, 10, 10}, {2, 10, 20}},
     {},
     {},
     {},
     {},
     {},
     10,
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 15, 10}, {3, 15, 20}, {7, 35, 30}},
     {},
     {},
     {},
     {},
     9,
     29,
     true},
    {std::vector<handlers::PromoSchedule>{
         {5, 15, 10}, {6, 15, 20}, {7, 15, 30}},
     {},
     {},
     {},
     {},
     10,
     30,
     false},
};

INSTANTIATE_TEST_SUITE_P(CheckRequestSchedulesData,
                         CheckRequestSchedulesDataFull,
                         ::testing::ValuesIn(kCheckRequestSchedulesData));

TEST_P(CheckRequestSchedulesDataFull, CheckRequestSchedules) {
  auto param = GetParam();
  TestSettingsValue settings;
  settings.min_size = param.min_size;
  settings.max_size = param.max_size;
  settings.min_value_day = param.min_value_day;
  settings.max_value_day = param.max_value_day;
  settings.min_value_time = param.min_value_time;
  settings.max_value_time = param.max_value_time;
  if (param.is_throw) {
    ASSERT_THROW(
        CheckRequestSchedules(param.value,
                              std::optional<TestSettingsValue>{settings}, {}),
        models::ValidationError);
  } else {
    ASSERT_NO_THROW(CheckRequestSchedules(
        param.value, std::optional<TestSettingsValue>{settings}, {}));
  }
}

TEST(CheckRequestSchedulesDataFull, CheckNullSettings) {
  std::optional<TestSettingsValue> settings;
  ASSERT_NO_THROW(CheckRequestSchedules(
      std::optional<std::vector<handlers::PromoSchedule>>{}, settings, {}));
  ASSERT_NO_THROW(CheckRequestSchedules(
      std::optional<std::vector<handlers::PromoSchedule>>{1}, settings, {}));
}

}  // namespace eats_restapp_promo::utils
