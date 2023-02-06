
#include <eats-places-availability/availability.hpp>
#include <eats-places-availability/utils/time.hpp>
#include <eats-places-availability/utils/utils.hpp>

#include <fmt/format.h>
#include <userver/utils/mock_now.hpp>

#include <gtest/gtest.h>

namespace eats_places_availability {

namespace {

using ::utils::datetime::MockNow;

const std::chrono::minutes kNoPrepare{0};
const std::chrono::minutes kNoOffset{0};
const std::string kTimeFormat{"%Y-%m-%d %H:%M"};

cctz::time_zone utc = cctz::fixed_time_zone(std::chrono::seconds(0));

std::string ToString(const Schedule& v) {
  std::string result;

  for (const auto& i : v) {
    auto start = std::chrono::duration_cast<std::chrono::seconds>(
        i.start.time_since_epoch());

    auto end = std::chrono::duration_cast<std::chrono::seconds>(
        i.end.time_since_epoch());

    result.append(fmt::format("{}-{}\n", std::to_string(start.count()),
                              std::to_string(end.count())));
  }

  return result;
}

std::string ToString(const Info& info) {
  auto from = info.from.has_value() ? cctz::format(kTimeFormat, *info.from, utc)
                                    : "null";

  auto to =
      info.to.has_value() ? cctz::format(kTimeFormat, *info.to, utc) : "null";

  return fmt::format(
      "(is_available = {}, is_available_now = {}, from = {}, to = {})",
      info.is_available, info.is_available_now, from, to);
}

TimeInterval CreateInterval(int from, int to) {
  auto from_sec = std::chrono::seconds(from);
  auto to_sec = std::chrono::seconds(to);

  return TimeInterval{
      std::chrono::system_clock::time_point(from_sec),
      std::chrono::system_clock::time_point(to_sec),
  };
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

}  // namespace

inline bool operator==(const Info& lhs, const Info& rhs) {
  return lhs.is_available == rhs.is_available && lhs.from == rhs.from &&
         lhs.to == rhs.to;
}

TEST(Utils, Compact) {
  auto schedule = Schedule{
      //        |-|
      CreateInterval(7, 10),
      CreateInterval(7, 10),
      //           |--|
      CreateInterval(8, 12),
      //              |-|
      CreateInterval(12, 14),
      // |----|
      CreateInterval(0, 5),
      //   |-|
      CreateInterval(3, 5),
      //   |--|
      CreateInterval(3, 6),
      //                 ||
      CreateInterval(15, 16),
      //                     |
      CreateInterval(18, 18),
  };

  auto merged = utils::Compact(std::move(schedule));

  auto expected = Schedule{
      CreateInterval(0, 6),
      CreateInterval(7, 14),
      CreateInterval(15, 16),
  };

  EXPECT_EQ(expected, merged) << "expected :\n"
                              << ToString(expected) << "actual   :\n"
                              << ToString(merged);
}

TEST(IsPickupAvailable, Simple) {
  Time time(2020, 8, 3, 15, 0);
  EXPECT_TRUE(IsPickupAvailable(MockNow(), utc));
}

TEST(IsPickupAvailable, AfterThreeHours) {
  Time time(2020, 8, 3, 15, 0);
  EXPECT_FALSE(IsPickupAvailable(CreateTime(2020, 8, 3, 18, 1), utc));
}

TEST(IsPickupAvailable, DifferentDays) {
  Time time(2020, 8, 3, 23, 0);
  EXPECT_FALSE(IsPickupAvailable(CreateTime(2020, 8, 4, 1, 11), utc));
}

TEST(IsPickupAvailable, InTwoHours) {
  Time time(2020, 8, 3, 20, 32);
  EXPECT_TRUE(IsPickupAvailable(CreateTime(2020, 8, 3, 22, 11), utc));
}

TEST(IsPickupAvailable, Timezone) {
  auto utc3 = cctz::fixed_time_zone(std::chrono::seconds(10800));
  Time time(2020, 8, 3, 20, 32);
  EXPECT_FALSE(IsPickupAvailable(CreateTime(2020, 8, 3, 22, 11), utc3));
}

TEST(PickupInfo, NoSchedule) {
  Time time(2020, 8, 3, 15, 0);

  auto pickup_time = CreateTime(2020, 8, 3, 0, 0);
  auto preparaion = std::chrono::minutes(100);
  auto schedule = Schedule{};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, Available) {
  Time time(2020, 3, 26, 17, 0);

  auto pickup_time = CreateTime(2020, 3, 26, 17, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 30),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, OpensLaterToday) {
  Time time(2020, 3, 26, 8, 0);

  auto pickup_time = CreateTime(2020, 3, 26, 8, 0);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,                            // is_available
      false,                            // is_available_now
      CreateTime(2020, 3, 26, 10, 30),  // from
      std::nullopt,                     // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, OpensLaterTomorrow) {
  Time time(2020, 3, 26, 23, 30);

  auto pickup_time = CreateTime(2020, 3, 26, 23, 30);
  auto preparaion = std::chrono::minutes(30);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)},
      {CreateTime(2020, 3, 27, 10, 30), CreateTime(2020, 3, 27, 18, 30)},
  };

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, PreorderInHour) {
  Time time(2020, 3, 26, 17, 0);

  auto pickup_time = CreateTime(2020, 3, 26, 18, 0);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      true,                             // is_available
      true,                             // is_available_now
      std::nullopt,                     // from
      CreateTime(2020, 3, 26, 18, 30),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, PreorderInThreeHours) {
  Time time(2020, 3, 26, 10, 0);

  auto pickup_time = CreateTime(2020, 3, 26, 13, 1);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 26, 18, 30)}};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      true,          // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(PickupInfo, PreorderInHourTomorrow) {
  Time time(2020, 3, 26, 23, 30);

  auto pickup_time = CreateTime(2020, 3, 27, 0, 39);
  auto preparaion = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 3, 26, 10, 30), CreateTime(2020, 3, 27, 18, 30)}};

  auto actual = PickupInfo(pickup_time, utc, preparaion, schedule);

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

// тестирует случай из задачи EDADEV-34367. При заказе ко времени в заведении, у
// которого ближайшее время доставки дальше чем выбранное время предзаказа,
// нужно отобразить недоступность, но при этом предать ближайшее доступное время
// предзаказа.
TEST(DeliveryInfo, MarketplaceBeforeAvailableDelivery) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 3, 16, 0);
  auto delivery_duration = std::chrono::minutes(100);
  auto schedule =
      Schedule{{CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)}};

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, false, true);

  auto expected = Info{
      false,                          // is_available
      true,                           // is_available_now
      CreateTime(2020, 8, 3, 17, 0),  // from
      std::nullopt,                   // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

// тестирует обратный случай из задачи EDADEV-34367.
// Доступность заказа ко времени в случае в выбора времени,
// которое вернулось в fromTime предыдущего кейса.
TEST(DeliveryInfo, MarketplaceAvailableDelivery) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 3, 17, 0);
  auto delivery_duration = std::chrono::minutes(100);
  auto schedule =
      Schedule{{CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)}};

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, false, true);

  auto expected = Info{
      true,                           // is_available
      true,                           // is_available_now
      std::nullopt,                   // from
      CreateTime(2020, 8, 3, 22, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, NativeDeliveryTill) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 3, 17, 0);
  auto delivery_duration = std::chrono::minutes(40);
  auto schedule =
      Schedule{{CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)}};

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, true, true);

  auto expected = Info{
      true,                           // is_available
      true,                           // is_available_now
      std::nullopt,                   // from
      CreateTime(2020, 8, 3, 22, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, MarketplaceDeliveryTill) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 3, 17, 0);
  auto delivery_duration = std::chrono::minutes(40);
  auto schedule =
      Schedule{{CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)}};

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, false, true);

  auto expected = Info{
      true,                           // is_available
      true,                           // is_available_now
      std::nullopt,                   // from
      CreateTime(2020, 8, 3, 22, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, NativeUnavailable) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 3, 23, 0);
  auto delivery_duration = std::chrono::minutes(10);
  auto schedule = Schedule{
      {CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)},
      {CreateTime(2020, 8, 4, 12, 0), CreateTime(2020, 8, 4, 22, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, true, true);

  auto expected = Info{
      false,                           // is_available
      true,                            // is_available_now
      CreateTime(2020, 8, 4, 12, 30),  // from
      std::nullopt,                    // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, NativeAfterMax) {
  Time time(2020, 8, 3, 15, 0);

  auto delivery_time = CreateTime(2020, 8, 6, 17, 0);
  auto delivery_duration = std::chrono::minutes(20);
  auto schedule = Schedule{
      {CreateTime(2020, 8, 3, 12, 0), CreateTime(2020, 8, 3, 22, 0)},
      {CreateTime(2020, 8, 4, 12, 0), CreateTime(2020, 8, 4, 22, 0)},
      {CreateTime(2020, 8, 5, 12, 0), CreateTime(2020, 8, 5, 22, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, true, true);

  auto expected = Info{
      false,         // is_available
      true,          // is_available_now
      std::nullopt,  // from
      // cctz::civil_minute(2020, 8, 5, 14, 45),
      std::nullopt,  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, NativeTomorrow) {
  Time time(2020, 9, 30, 17, 30);

  auto delivery_time = CreateTime(2020, 10, 1, 12, 30);
  auto delivery_duration = std::chrono::minutes(70);
  auto schedule = Schedule{
      {CreateTime(2020, 9, 30, 9, 0), CreateTime(2020, 9, 30, 23, 0)},
      {CreateTime(2020, 10, 1, 9, 0), CreateTime(2020, 10, 1, 21, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, true, true);

  auto expected = Info{
      true,                            // is_available
      true,                            // is_available_now
      std::nullopt,                    // from
      CreateTime(2020, 10, 1, 21, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, MarketTomorrow) {
  Time time(2020, 9, 30, 17, 30);

  auto delivery_time = CreateTime(2020, 10, 1, 12, 30);
  auto delivery_duration = std::chrono::minutes(40);
  auto schedule = Schedule{
      {CreateTime(2020, 9, 30, 9, 0), CreateTime(2020, 9, 30, 23, 0)},
      {CreateTime(2020, 10, 1, 9, 0), CreateTime(2020, 10, 1, 21, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, false, true);

  auto expected = Info{
      true,                            // is_available
      true,                            // is_available_now
      std::nullopt,                    // from
      CreateTime(2020, 10, 1, 21, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

// EDADEV-36376
// проверяет, что если интервал заканчивается далеко в будущем,
// то TillTime ограничивается днем заказа.
TEST(DeliveryInfo, NativeTillTimeMustBeToday) {
  Time time(2020, 9, 30, 17, 30);

  auto delivery_time = CreateTime(2020, 10, 1, 12, 30);
  auto delivery_duration = std::chrono::minutes(40);
  auto schedule = Schedule{
      {CreateTime(2020, 9, 30, 9, 0), CreateTime(2021, 9, 30, 23, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, true, true);

  auto expected = Info{
      true,                           // is_available
      true,                           // is_available_now
      std::nullopt,                   // from
      CreateTime(2020, 10, 2, 0, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, MarketTillTimeMustBeToday) {
  Time time(2020, 9, 30, 17, 30);

  auto delivery_time = CreateTime(2020, 10, 1, 12, 30);
  auto delivery_duration = std::chrono::minutes(40);
  auto schedule = Schedule{
      {CreateTime(2020, 9, 30, 9, 0), CreateTime(2021, 9, 30, 23, 0)},
  };

  auto actual = DeliveryInfo(delivery_time, utc, delivery_duration, kNoPrepare,
                             kNoOffset, schedule, false, true);

  auto expected = Info{
      true,                           // is_available
      true,                           // is_available_now
      std::nullopt,                   // from
      CreateTime(2020, 10, 2, 0, 0),  // till
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, NativePrepareTimeFromEnd) {
  Time time{2021, 4, 16, 12, 47};

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),                     // start
          ::utils::datetime::MockNow() + (preparation / 2),  // end
      },
      TimeInterval{
          CreateTime(2021, 4, 17, 9, 0),   // start
          CreateTime(2021, 4, 17, 16, 0),  // end
      },
  };

  auto actual = DeliveryInfo(::utils::datetime::MockNow(),  // at
                             cctz::utc_time_zone(),         // user_tz
                             travel,                        // travel
                             preparation,                   // preparation
                             kNoOffset,                     // offset
                             schedule,                      // schedule
                             true,  // delivery_after_hours
                             true   // supports_preoreder
  );

  auto expected = Info{
      false,  // is_available
      false,  // is_available_now
      utils::CeilToMinutes(CreateTime(2021, 4, 17, 9, 0) + travel + preparation,
                           30,
                           cctz::utc_time_zone()),  // from
      std::nullopt,                                 // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, MarketplacePrepareTimeFromEnd) {
  Time time{2021, 4, 16, 12, 47};

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),                                // start
          ::utils::datetime::MockNow() + (travel + (preparation / 2)),  // end
      },
      TimeInterval{
          CreateTime(2021, 4, 17, 9, 0),   // start
          CreateTime(2021, 4, 17, 16, 0),  // end
      },
  };

  auto actual = DeliveryInfo(::utils::datetime::MockNow(),  // at
                             cctz::utc_time_zone(),         // user_tz
                             travel,                        // travel
                             preparation,                   // preparation
                             kNoOffset,                     // offset
                             schedule,                      // schedule
                             false,  // delivery_after_hours
                             true    // supports_preoreder
  );

  auto expected = Info{
      false,  // is_available
      false,  // is_available_now
      utils::CeilToMinutes(CreateTime(2021, 4, 17, 9, 0) + travel + preparation,
                           30,
                           cctz::utc_time_zone()),  // from
      std::nullopt,                                 // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, PreorderAfterScheduleEnd) {
  Time time{2021, 4, 16, 12, 47};

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),   // start
          CreateTime(2021, 4, 16, 15, 0),  // end
      },
  };

  auto actual = DeliveryInfo(CreateTime(2021, 4, 16, 15, 30),  // at
                             cctz::utc_time_zone(),            // user_tz
                             travel,                           // travel
                             preparation,                      // preparation
                             kNoOffset,                        // offset
                             schedule,                         // schedule
                             true,  // delivery_after_hours
                             true   // supports_preoreder
  );

  auto expected = Info{
      true,                            // is_available
      true,                            // is_available_now
      std::nullopt,                    // from
      CreateTime(2021, 4, 16, 15, 0),  // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, PreorderAfterScheduleEndNoDeliveryAfterHours) {
  Time time{2021, 4, 16, 12, 47};

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),   // start
          CreateTime(2021, 4, 16, 15, 0),  // end
      },
  };

  auto actual = DeliveryInfo(CreateTime(2021, 4, 16, 15, 30),  // at
                             cctz::utc_time_zone(),            // user_tz
                             travel,                           // travel
                             preparation,                      // preparation
                             kNoOffset,                        // offset
                             schedule,                         // schedule
                             false,  // delivery_after_hours
                             true    // supports_preoreder
  );

  auto expected = Info{
      false,         // is_available
      true,          // is_available_now
      std::nullopt,  // from
      std::nullopt,  // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, ASAPCloseToEndNoOffset) {
  Time time{2021, 4, 16, 14, 40};  // end - preparation

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),   // start
          CreateTime(2021, 4, 16, 15, 0),  // end
      },
  };

  auto actual = DeliveryInfo(::utils::datetime::MockNow(),  // at
                             cctz::utc_time_zone(),         // user_tz
                             travel,                        // travel
                             preparation,                   // preparation
                             kNoOffset,                     // offset
                             schedule,                      // schedule
                             true,  // delivery_after_hours
                             true   // supports_preoreder
  );

  auto expected = Info{
      true,                            // is_available
      true,                            // is_available_now
      std::nullopt,                    // from
      CreateTime(2021, 4, 16, 15, 0),  // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, ASAPCloseToEndWithOffset) {
  Time time{2021, 4, 16, 14, 40};  // end - preparation

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto offset = std::chrono::minutes{5};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),   // start
          CreateTime(2021, 4, 16, 15, 0),  // end
      },
  };

  auto actual = DeliveryInfo(::utils::datetime::MockNow(),  // at
                             cctz::utc_time_zone(),         // user_tz
                             travel,                        // travel
                             preparation,                   // preparation
                             offset,                        // offset
                             schedule,                      // schedule
                             true,  // delivery_after_hours
                             true   // supports_preoreder
  );

  auto expected = Info{
      false,         // is_available
      false,         // is_available_now
      std::nullopt,  // from
      std::nullopt,  // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

TEST(DeliveryInfo, ASAPCloseToEndWithOffsetAvailable) {
  Time time{2021, 4, 16, 14, 35};  // end - preparation - offset

  const auto travel = std::chrono::minutes{40};
  const auto preparation = std::chrono::minutes{20};
  const auto offset = std::chrono::minutes{5};
  const auto schedule = Schedule{
      TimeInterval{
          CreateTime(2021, 4, 16, 9, 0),   // start
          CreateTime(2021, 4, 16, 15, 0),  // end
      },
  };

  auto actual = DeliveryInfo(::utils::datetime::MockNow(),  // at
                             cctz::utc_time_zone(),         // user_tz
                             travel,                        // travel
                             preparation,                   // preparation
                             offset,                        // offset
                             schedule,                      // schedule
                             true,  // delivery_after_hours
                             true   // supports_preoreder
  );

  auto expected = Info{
      true,                            // is_available
      true,                            // is_available_now
      std::nullopt,                    // from
      CreateTime(2021, 4, 16, 15, 0),  // to
  };

  EXPECT_EQ(expected, actual) << "expected : " << ToString(expected) << "\n"
                              << "actual   : " << ToString(actual);
}

}  // namespace eats_places_availability
