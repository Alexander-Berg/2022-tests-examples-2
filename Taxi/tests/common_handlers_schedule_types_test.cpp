#include <cctz/civil_time.h>

#include <gtest/gtest-printers.h>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <common_handlers/schedule/helpers.hpp>
#include <common_handlers/schedule_summary/rules.hpp>
#include <common_handlers/types.hpp>

namespace handlers {

std::ostream& operator<<(std::ostream& os, const ScheduleData& schedule_data) {
  return os << "(" << schedule_data.start << ", " << schedule_data.end << ")";
}

template <class T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& vector) {
  os << "[";

  bool first = true;
  for (const auto& e : vector) {
    if (!first) {
      os << ", ";
    }
    os << e;
    first = false;
  }

  return os << "]";
}

std::ostream& operator<<(std::ostream& os,
                         const ScheduleAdjacentGroup& schedule_adjacent_group) {
  return os << "{start: " << schedule_adjacent_group.start
            << ", end: " << schedule_adjacent_group.end
            << ", schedule_data: " << schedule_adjacent_group.schedule_data
            << "}";
}

bool operator==(const ScheduleData& lhs, const ScheduleData& rhs) {
  return lhs.start == rhs.start && lhs.end == rhs.end;
}

bool operator==(const ScheduleAdjacentGroup& lhs,
                const ScheduleAdjacentGroup& rhs) {
  return lhs.start == rhs.start && lhs.end == rhs.end &&
         lhs.schedule_data == rhs.schedule_data;
}
}  // namespace handlers

namespace {

namespace dt = utils::datetime;

handlers::ExtendedRuleWithProgressPtr CreateStubExtendedSingleRideRule() {
  const bool use_rule_definition = false;
  const int orders_completed = 2;
  const client_geoareas::models::SubventionGeoareas subvention_geoareas{};
  common_handlers::NewSchedule::value_type schedule_item{
      {std::chrono::system_clock::time_point::min(),
       std::chrono::system_clock::time_point::max()},
      {}};

  auto p_extended_rule = std::make_shared<handlers::SmartExtendedRule>(
      subvention_matcher::GroupedRule{bsx::SingleRideRule{}},
      std::move(schedule_item), subvention_geoareas, use_rule_definition);

  return std::make_shared<const handlers::ExtendedRuleWithProgress>(
      p_extended_rule, orders_completed);
}

handlers::ScheduleData CreateMockScheduleData(cctz::civil_minute from,
                                              cctz::civil_minute to) {
  handlers::ScheduleDay schedule_day;
  schedule_day.day = cctz::civil_day(from);
  schedule_day.from = std::move(from);
  schedule_day.to = std::move(to);

  return handlers::ScheduleData(CreateStubExtendedSingleRideRule(),
                                schedule_day, models::ZoneInfo{});
}

}  // namespace

TEST(CommonHandlersSchedule, GroupAdjacent) {
  CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                         cctz::civil_minute(2020, 1, 1, 9, 10));
}

struct GroupAdjacentTestData {
  std::vector<handlers::ScheduleData> schedule;
  std::vector<handlers::ScheduleAdjacentGroup> expected;
};

class GroupAdjacentTestParametrized
    : public ::testing::TestWithParam<GroupAdjacentTestData> {};

TEST_P(GroupAdjacentTestParametrized, Cases) {
  const auto param = GetParam();
  auto actual = GroupAdjacent(param.schedule);

  EXPECT_EQ(actual, param.expected);

  auto gr = handlers::ScheduleAdjacentGroup{
      // start
      cctz::civil_minute(2020, 1, 1, 9, 0),
      // end
      cctz::civil_minute(2020, 1, 1, 9, 10),
      // schedule_data
      {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                              cctz::civil_minute(2020, 1, 1, 9, 10))}};
}

const std::vector<GroupAdjacentTestData> kGroupAdjacentTestData = {
    {

        // schedule
        {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                cctz::civil_minute(2020, 1, 1, 9, 10))},
        // expected
        {handlers::ScheduleAdjacentGroup{
            // start
            cctz::civil_minute(2020, 1, 1, 9, 0),
            // end
            cctz::civil_minute(2020, 1, 1, 9, 10),
            // schedule_data
            {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                    cctz::civil_minute(2020, 1, 1, 9, 10))}}

        }

    },

    {

        // schedule
        {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                cctz::civil_minute(2020, 1, 1, 9, 10)),
         CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 10),
                                cctz::civil_minute(2020, 1, 1, 9, 15)),
         CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 20),
                                cctz::civil_minute(2020, 1, 1, 9, 25))},
        // expected
        {

            handlers::ScheduleAdjacentGroup{
                // start
                cctz::civil_minute(2020, 1, 1, 9, 0),
                // end
                cctz::civil_minute(2020, 1, 1, 9, 15),
                // schedule_data
                {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                        cctz::civil_minute(2020, 1, 1, 9, 10)),
                 CreateMockScheduleData(
                     cctz::civil_minute(2020, 1, 1, 9, 10),
                     cctz::civil_minute(2020, 1, 1, 9, 15))}},

            handlers::ScheduleAdjacentGroup{
                // start
                cctz::civil_minute(2020, 1, 1, 9, 20),
                // end
                cctz::civil_minute(2020, 1, 1, 9, 25),
                // schedule_data
                {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 20),
                                        cctz::civil_minute(2020, 1, 1, 9, 25))}}

        }

    },

    {

        // schedule
        {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                cctz::civil_minute(2020, 1, 1, 9, 10)),
         CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 5),
                                cctz::civil_minute(2020, 1, 1, 9, 15)),
         CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 8, 30),
                                cctz::civil_minute(2020, 1, 1, 9, 25))},
        // expected
        {

            handlers::ScheduleAdjacentGroup{
                // start
                cctz::civil_minute(2020, 1, 1, 8, 30),
                // end
                cctz::civil_minute(2020, 1, 1, 9, 25),
                // schedule_data
                {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 8, 30),
                                        cctz::civil_minute(2020, 1, 1, 9, 25)),
                 CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                        cctz::civil_minute(2020, 1, 1, 9, 10)),
                 CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 5),
                                        cctz::civil_minute(2020, 1, 1, 9, 15))}}

        }

    },

    {

        // schedule
        {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                cctz::civil_minute(2020, 1, 1, 9, 30)),
         CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 5),
                                cctz::civil_minute(2020, 1, 1, 9, 15))},
        // expected
        {

            handlers::ScheduleAdjacentGroup{
                // start
                cctz::civil_minute(2020, 1, 1, 9, 0),
                // end
                cctz::civil_minute(2020, 1, 1, 9, 30),
                // schedule_data
                {CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 0),
                                        cctz::civil_minute(2020, 1, 1, 9, 30)),
                 CreateMockScheduleData(cctz::civil_minute(2020, 1, 1, 9, 5),
                                        cctz::civil_minute(2020, 1, 1, 9, 15))}}

        }

    }

};

INSTANTIATE_TEST_SUITE_P(CommonHandlersSchedule, GroupAdjacentTestParametrized,
                         ::testing::ValuesIn(kGroupAdjacentTestData));
