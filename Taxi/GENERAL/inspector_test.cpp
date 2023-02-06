#include <chrono>

#include <fmt/format.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <eats-places-availability/availability.hpp>
#include <eats-places-availability/inspector.hpp>
#include <eats-places-availability/utils/time.hpp>
#include <eats-places-availability/utils/utils.hpp>

namespace eats_places_availability {

namespace {

using ::utils::datetime::MockNow;

const std::string kTimeFormat{"%Y-%m-%d %H:%M"};

cctz::time_zone utc = cctz::fixed_time_zone(std::chrono::seconds(0));

std::string ToString(const Info& info) {
  auto from = info.from.has_value() ? cctz::format(kTimeFormat, *info.from, utc)
                                    : "null";

  auto to =
      info.to.has_value() ? cctz::format(kTimeFormat, *info.to, utc) : "null";

  return fmt::format(
      "(is_available = {}, is_available_now = {}, from = {}, to = {})",
      info.is_available, info.is_available_now, from, to);
}

std::chrono::system_clock::time_point CreateTime(int y, int m = 1, int d = 1,
                                                 int hh = 0, int mm = 0) {
  return cctz::convert(cctz::civil_minute(y, m, d, hh, mm), utc);
}

struct Time {
  explicit Time(int y, int m = 1, int d = 1, int hh = 0, int mm = 0) {
    ::utils::datetime::MockNowSet(CreateTime(y, m, d, hh, mm));
  }
  ~Time() { ::utils::datetime::MockNowUnset(); }
};

Inspector CreateInspector(const bool new_pickup_flow,
                          int user_late_minutes = 30) {
  return Inspector{
      InspectorConfig{
          new_pickup_flow,                          // enable_new_pickup_flow
          std::chrono::minutes{user_late_minutes},  // pickup_user_late
      },
  };
}

}  // namespace

inline bool operator==(const Info& lhs, const Info& rhs) {
  return lhs.is_available == rhs.is_available && lhs.from == rhs.from &&
         lhs.to == rhs.to;
}

UTEST(Inspector, Pickup_NoSchedule) {
  Time time(2020, 8, 3, 15, 0);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 8, 3, 0, 0);
  auto preparaion = std::chrono::minutes(100);
  auto schedule = Schedule{};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, Pickup_Available) {
  Time time(2020, 3, 26, 17, 0);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 17, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 30),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_OpensLaterToday) {
  Time time(2020, 3, 26, 8, 0);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 8, 0);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,                            // is_available
      false,                            // is_available_now
      CreateTime(2020, 3, 26, 10, 30),  // from
      std::nullopt,                     // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_OpensLaterTomorrow) {
  Time time(2020, 3, 26, 23, 30);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 23, 30);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)},
      {CreateTime(2020, 3, 27, 10, 30), CreateTime(2020, 3, 27, 18, 30)},
  };

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInHour) {
  Time time(2020, 3, 26, 17, 0);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 18, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 30),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInThreeHours) {
  Time time(2020, 3, 26, 10, 0);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 13, 1);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      true,          // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInHourTomorrow) {
  Time time(2020, 3, 26, 23, 30);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 27, 0, 39);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 27, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_BeforeOpen) {
  Time time(2020, 3, 26, 10, 15);

  const auto inspector = CreateInspector(false);

  auto pickup_time = CreateTime(2020, 3, 26, 10, 15);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {
          CreateTime(2020, 3, 26, 10, 30),
          CreateTime(2020, 3, 27, 18, 30),
      },
  };

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 27, 18, 30),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, Pickup_NoSchedule_NewFlow) {
  Time time(2020, 8, 3, 15, 0);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 8, 3, 0, 0);
  auto preparaion = std::chrono::minutes(100);
  auto schedule = Schedule{};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, Pickup_Available_NewFlow) {
  Time time(2020, 3, 26, 17, 0);

  const auto inspector = CreateInspector(true, 5);

  auto pickup_time = CreateTime(2020, 3, 26, 17, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 10),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_OpensLaterToday_NewFlow) {
  Time time(2020, 3, 26, 8, 0);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 26, 8, 0);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_OpensLaterTomorrow_NewFlow) {
  Time time(2020, 3, 26, 23, 30);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 26, 23, 30);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)},
      {CreateTime(2020, 3, 27, 10, 30), CreateTime(2020, 3, 27, 18, 30)},
  };

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInHour_NewFlow) {
  Time time(2020, 3, 26, 17, 0);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 26, 18, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 00),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInThreeHours_NewFlow) {
  Time time(2020, 3, 26, 10, 0);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 26, 13, 1);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      true,          // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_PreorderInHourTomorrow_NewFlow) {
  Time time(2020, 3, 26, 23, 30);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 27, 0, 39);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 27, 18, 30)}};

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

UTEST(Inspector, PickupInfo_BeforeOpen_NewFlow) {
  Time time(2020, 3, 26, 10, 15);

  const auto inspector = CreateInspector(true);

  auto pickup_time = CreateTime(2020, 3, 26, 10, 15);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {
          CreateTime(2020, 3, 26, 10, 30),
          CreateTime(2020, 3, 27, 18, 30),
      },
  };

  auto actual = inspector.Pickup(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,  // is_available
      false,  // is_available_now
      std::nullopt,
      std::nullopt,
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

}  // namespace eats_places_availability
