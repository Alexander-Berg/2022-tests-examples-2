#include <set>
#include <string>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <discounts-match/conditions.hpp>
#include <discounts/models/names.hpp>

#include <taxi_config/variables/APPLICATION_MAP_BRAND.hpp>
#include <taxi_config/variables/APPLICATION_MAP_DISCOUNTS.hpp>

#include <models/names.hpp>
#include <utils/utils.hpp>

namespace {

using Strings = std::vector<std::string>;
using Container = std::set<std::string>;

struct IntersectsTestData {
  const Container lhs;
  const Container rhs;
  bool intersects = false;
};

class IntersectsP : public testing::Test,
                    public testing::WithParamInterface<IntersectsTestData> {};

}  // namespace

TEST_P(IntersectsP, Utils) {
  const auto& param = GetParam();

  ASSERT_EQ(utils::Intersects(cbegin(param.lhs), cend(param.lhs),
                              cbegin(param.rhs), cend(param.rhs)),
            param.intersects);
}

INSTANTIATE_TEST_SUITE_P(
    Intersects, IntersectsP,
    testing::Values(IntersectsTestData{{}, {}, false},
                    IntersectsTestData{{}, {""}, false},
                    IntersectsTestData{{""}, {}, false},
                    IntersectsTestData{{""}, {""}, true},
                    IntersectsTestData{{"a"}, {"b"}, false},
                    IntersectsTestData{{"a", "c"}, {"b", "c"}, true},
                    IntersectsTestData{{"a", "b"}, {"a", "c"}, true},
                    IntersectsTestData{{"a", "c", "e"}, {"b", "c", "d"}, true},
                    IntersectsTestData{{"b"}, {"a", "b", "c"}, true},
                    IntersectsTestData{{"a", "b", "c"}, {"b"}, true}));

TEST(GetStartTime, NotIsUtc) {
  auto time_point = utils::datetime::Stringtime("2021-01-01T12:00:00+0000");
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Moscow", &tz);
  {
    rules_match::generated::TimeRangeValue time_range{time_point, false,
                                                      time_point, false};
    ASSERT_EQ(utils::GetStartTime(time_range, tz),
              utils::datetime::Stringtime("2021-01-01T09:00:00+0000"));
  }

  {
    rules_match::generated::TimeRangeValue time_range{time_point, false,
                                                      time_point, false};
    ASSERT_EQ(utils::GetStartTime(time_range, tz),
              utils::datetime::Stringtime("2021-01-01T09:00:00+0000"));
  }
}

TEST(GetStartTime, IsUtc) {
  auto time_point = utils::datetime::Stringtime("2021-01-01T12:00:00+0000");
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Moscow", &tz);
  rules_match::generated::TimeRangeValue time_range{time_point, true,
                                                    time_point, true};
  ASSERT_EQ(utils::GetStartTime(time_range, tz),
            utils::datetime::Stringtime("2021-01-01T12:00:00+0000"));
}
