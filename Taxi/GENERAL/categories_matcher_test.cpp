#include <userver/utest/utest.hpp>

#include <fmt/format.h>

#include <userver/utils/datetime.hpp>

#include "matchers.hpp"

namespace {
namespace dt = utils::datetime;

using Weekday = clients::territories::CountryWeekendsA;

const std::string kBusiness{"business"};
const std::string kComfort{"comfort"};
const std::string kComfortPlus{"comfortplus"};
const std::string kEconom{"econom"};

static const models::Country kCountry{
    {}, {}, {}, {}, {{Weekday::kSaturday, Weekday::kSunday}}, {}, {}};

std::chrono::minutes MinutesFromDayStart(const std::string& str) {
  const std::chrono::seconds seconds_since_midnight{
      utils::datetime::ParseDayTime(str)};
  return std::chrono::duration_cast<std::chrono::minutes>(
      seconds_since_midnight);
}

using CategoryType = models::Conditions::CategoryType;
using DayType = models::Conditions::DayType;

std::string ToString(const CategoryType& type) {
  switch (type) {
    case CategoryType::Application:
      return "application";
    case CategoryType::CallCenter:
      return "callcenter";
  }
}

std::string ToString(const DayType& type) {
  switch (type) {
    case DayType::Everyday:
      return "everyday";
    case DayType::Dayoff:
      return "dayoff";
    case DayType::Workday:
      return "workday";
  }
}

std::string MakeCategoryId(const std::string& name, const CategoryType cat_type,
                           const DayType day_type,
                           const std::string& active_from,
                           const std::string& active_to) {
  return fmt::format("{}_{}_{}_{}_{}", name, ToString(cat_type),
                     ToString(day_type), active_from, active_to);
}

std::pair<std::string, models::CategoryPtr> MakeCategory(
    const std::string& name, const CategoryType cat_type,
    const DayType day_type, const std::string& active_from,
    const std::string& active_to) {
  auto result = std::make_shared<models::Category>();
  result->conditions.time_from = MinutesFromDayStart(active_from);
  result->conditions.time_to = MinutesFromDayStart(active_to);
  result->conditions.day_type = day_type;
  result->conditions.category_type = cat_type;
  result->name = std::move(name);
  result->id = MakeCategoryId(name, cat_type, day_type, active_from, active_to);
  return std::make_pair(result->id, result);
}

const models::CategoriesByIdMap& MakeCategories() {
  static const models::CategoriesByIdMap kCategories{
      MakeCategory(kEconom, CategoryType::CallCenter, DayType::Everyday,
                   "00:00", "23:59"),
      MakeCategory(kEconom, CategoryType::CallCenter, DayType::Dayoff, "00:00",
                   "23:59"),  // Duplicate for test
      MakeCategory(kEconom, CategoryType::CallCenter, DayType::Dayoff, "08:00",
                   "08:59"),  // Another duplicate for test
      MakeCategory(kEconom, CategoryType::Application, DayType::Workday,
                   "00:00", "23:59"),
      MakeCategory(kEconom, CategoryType::Application, DayType::Dayoff, "00:00",
                   "23:59"),
      MakeCategory(kComfort, CategoryType::CallCenter, DayType::Workday,
                   "00:00", "23:59"),
      MakeCategory(kComfort, CategoryType::CallCenter, DayType::Dayoff, "00:00",
                   "23:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Workday,
                   "00:00", "07:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Workday,
                   "08:00", "19:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Workday,
                   "20:00", "23:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Dayoff,
                   "00:00", "07:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Dayoff,
                   "08:00", "19:59"),
      MakeCategory(kComfort, CategoryType::Application, DayType::Dayoff,
                   "20:00", "23:59"),
      MakeCategory(kComfortPlus, CategoryType::Application, DayType::Dayoff,
                   "00:00", "23:59"),
      MakeCategory(kBusiness, CategoryType::Application, DayType::Workday,
                   "06:00", "21:59"),
      MakeCategory(kBusiness, CategoryType::Application, DayType::Workday,
                   "22:00", "05:59"),
      MakeCategory(kBusiness, CategoryType::Application, DayType::Dayoff,
                   "06:00", "21:59"),
      MakeCategory(kBusiness, CategoryType::Application, DayType::Dayoff,
                   "22:00", "05:59"),
  };
  return kCategories;
}

}  // namespace

struct Params {
  std::unordered_set<std::string> requested_categories;
  CategoryType requested_type;
  std::string timestring;
  std::string timezone;
};

struct Results {
  std::unordered_map<std::string /*name*/, std::string /*id*/>
      expected_categories;
};

auto MakeTestParam(
    const std::unordered_set<std::string>& requested_categories,
    const CategoryType requested_type, const std::string& timestring,
    const std::string& timezone,
    const std::unordered_map<std::string /*name*/, std::string /*id*/>&
        expected_categories) {
  Params params{requested_categories, requested_type, timestring, timezone};
  Results results{expected_categories};
  return std::make_tuple(std::move(params), std::move(results));
}

using TestParam = decltype(MakeTestParam({}, {}, {}, {}, {}));

class CategoriesMatcher : public ::testing::TestWithParam<TestParam> {};

UTEST_P(CategoriesMatcher, CategoriesMatcher) {
  const auto& [params, results] = GetParam();

  const auto& matched_categories = utils::matchers::MatchCategories(
      params.requested_categories, params.requested_type,
      dt::Stringtime(params.timestring, params.timezone, "%Y-%m-%dT%H:%M:%E*S"),
      params.timezone, MakeCategories(), kCountry);
  EXPECT_EQ(matched_categories.size(), results.expected_categories.size());

  for (const auto& [_, matched] : matched_categories) {
    const auto it = results.expected_categories.find(matched->name);
    const bool found = (it != results.expected_categories.end());
    EXPECT_TRUE(found);
    if (found) EXPECT_EQ(matched->id, it->second);
  }
}

INSTANTIATE_UTEST_SUITE_P(
    CategoriesMatcher, CategoriesMatcher,
    ::testing::Values(  //
        MakeTestParam({"unknown"}, CategoryType::Application,
                      "2019-08-01T12:00:00", dt::kDefaultDriverTimezone,
                      {}),  // 0
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-02T08:30:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Everyday, "00:00",
                                       "23:59")}}),  // 1
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-03T07:30:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Dayoff, "00:00",
                                       "23:59")}}),  // 2
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-03T07:59:59", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Dayoff, "00:00",
                                       "23:59")}}),  // 3
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-03T08:00:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Dayoff, "08:00",
                                       "08:59")}}),  // 4
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-03T08:30:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Dayoff, "08:00",
                                       "08:59")}}),  // 5
        MakeTestParam({kEconom}, CategoryType::CallCenter,
                      "2019-08-03T08:59:59", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::CallCenter,
                                       DayType::Dayoff, "08:00",
                                       "08:59")}}),  // 6
        MakeTestParam({kEconom}, CategoryType::Application,
                      "2019-08-02T08:30:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::Application,
                                       DayType::Workday, "00:00",
                                       "23:59")}}),  // 7
        MakeTestParam({kEconom}, CategoryType::Application,
                      "2019-08-03T08:30:00", dt::kDefaultDriverTimezone,
                      {{kEconom,
                        MakeCategoryId(kEconom, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "23:59")}}),  // 8
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T08:30:00", dt::kDefaultDriverTimezone,
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "08:00",
                                       "19:59")}}),  // 9
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T07:59:59", "Asia/Yekaterinburg",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "07:59")}}),  // 10
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T08:00:00", "Asia/Yekaterinburg",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "08:00",
                                       "19:59")}}),  // 11
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T07:59:59", "Europe/Kaliningrad",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "07:59")}}),  // 12
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T08:00:00", "Europe/Kaliningrad",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "08:00",
                                       "19:59")}}),  // 13
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-02T23:59:59", "Asia/Yekaterinburg",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Workday, "20:00",
                                       "23:59")}}),  // 14
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T00:00:00", "Asia/Yekaterinburg",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "07:59")}}),  // 15
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-02T23:59:59", "Europe/Kaliningrad",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Workday, "20:00",
                                       "23:59")}}),  // 16
        MakeTestParam({kComfort}, CategoryType::Application,
                      "2019-08-03T00:00:00", "Europe/Kaliningrad",
                      {{kComfort,
                        MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "07:59")}}),  // 17
        MakeTestParam(
            {kEconom, kComfort}, CategoryType::CallCenter,
            "2019-08-01T08:30:00", dt::kDefaultDriverTimezone,
            {{kEconom, MakeCategoryId(kEconom, CategoryType::CallCenter,
                                      DayType::Everyday, "00:00", "23:59")},
             {kComfort,
              MakeCategoryId(kComfort, CategoryType::CallCenter,
                             DayType::Workday, "00:00", "23:59")}}),  // 18
        MakeTestParam(
            {kComfort, kEconom}, CategoryType::Application,
            "2019-08-01T07:59:59", dt::kDefaultDriverTimezone,
            {{kComfort, MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Workday, "00:00", "07:59")},
             {kEconom,
              MakeCategoryId(kEconom, CategoryType::Application,
                             DayType::Workday, "00:00", "23:59")}}),  // 19
        MakeTestParam(
            {kComfort, kEconom}, CategoryType::Application,
            "2019-08-03T23:59:59", dt::kDefaultDriverTimezone,
            {{kComfort, MakeCategoryId(kComfort, CategoryType::Application,
                                       DayType::Dayoff, "20:00", "23:59")},
             {kEconom,
              MakeCategoryId(kEconom, CategoryType::Application,
                             DayType::Dayoff, "00:00", "23:59")}}),  // 20
        MakeTestParam({kComfortPlus}, CategoryType::Application,
                      "2019-08-03T08:30:00", dt::kDefaultDriverTimezone,
                      {{kComfortPlus,
                        MakeCategoryId(kComfortPlus, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "23:59")}}),  // 21
        MakeTestParam({kComfortPlus}, CategoryType::CallCenter,
                      "2019-08-03T08:30:00", dt::kDefaultDriverTimezone,
                      {{kComfortPlus,
                        MakeCategoryId(kComfortPlus, CategoryType::Application,
                                       DayType::Dayoff, "00:00",
                                       "23:59")}}),  // 22
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T00:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "22:00",
                                       "05:59")}}),  // 23
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T05:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "22:00",
                                       "05:59")}}),  // 24
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T06:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "06:00",
                                       "21:59")}}),  // 25
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T21:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "06:00",
                                       "21:59")}}),  // 26
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T22:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "22:00",
                                       "05:59")}}),  // 27
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-02T23:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Workday, "22:00",
                                       "05:59")}}),  // 28
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T00:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "22:00",
                                       "05:59")}}),  // 29
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T05:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "22:00",
                                       "05:59")}}),  // 30
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T06:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "06:00",
                                       "21:59")}}),  // 31
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T21:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "06:00",
                                       "21:59")}}),  // 32
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T22:00:00", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "22:00",
                                       "05:59")}}),  // 33
        MakeTestParam({kBusiness}, CategoryType::Application,
                      "2019-08-03T23:59:59", dt::kDefaultDriverTimezone,
                      {{kBusiness,
                        MakeCategoryId(kBusiness, CategoryType::Application,
                                       DayType::Dayoff, "22:00",
                                       "05:59")}})  // 34
        ));
