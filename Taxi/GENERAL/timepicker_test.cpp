
#include <eats-places-availability/availability.hpp>
#include <eats-places-availability/timepicker.hpp>

#include <iterator>

#include <fmt/format.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace eats_places_availability {

namespace {

const std::chrono::minutes kNoOffset{0};
const std::string kRFC3339 = "%Y-%m-%dT%H:%M:%S%Ez";

std::chrono::system_clock::time_point CreateTime(
    int y, int m = 1, int d = 1, int hh = 0, int mm = 0,
    const cctz::time_zone& tz = cctz::utc_time_zone()) {
  return cctz::convert(cctz::civil_minute(y, m, d, hh, mm), tz);
}

std::vector<std::chrono::system_clock::time_point> CreatePicker(
    std::initializer_list<TimeInterval> intervals,
    const std::chrono::minutes inteval) {
  std::vector<std::chrono::system_clock::time_point> result;

  for (const auto ival : intervals) {
    for (auto current = ival.start; current <= ival.end; current += inteval) {
      if (result.empty() || result.back() != current) {
        result.push_back(current);
      }
    }
  }

  return result;
}

using Day = std::vector<std::chrono::system_clock::time_point>;

std::string Diff(const Day& expected, const Day& actual) {
  const size_t max = std::max(expected.size(), actual.size());

  std::string result;
  result.append(fmt::format("{:30} {:30}\n", "expected", "actual"));

  for (size_t i = 0; i < max; ++i) {
    std::string left{};
    if (expected.size() > i) {
      left = cctz::format(kRFC3339, expected[i], cctz::utc_time_zone());
    }

    std::string right{};
    if (actual.size() > i) {
      right = cctz::format(kRFC3339, actual[i], cctz::utc_time_zone());
    }

    result.append(fmt::format("{:30} {:30}\n", left, right));
  }

  return result;
}

std::string Diff(const Timepicker& expected, const Timepicker actual) {
  std::string result;
  for (size_t i = 0; i < expected.size(); ++i) {
    result.append(Diff(expected[i], actual[i]));
    result.append("\n");
  }
  return result;
}

void BruteForceDeliveryTest(const Timepicker& timepicker,
                            const cctz::time_zone& user_tz,
                            const std::chrono::minutes travel,
                            const std::chrono::minutes preparation,
                            const Schedule& schedule,
                            const bool delivery_after_hours) {
  for (const auto& day : timepicker) {
    for (const auto& time : day) {
      const auto info =
          DeliveryInfo(time, user_tz, travel, preparation, kNoOffset, schedule,
                       delivery_after_hours, true);
      ASSERT_TRUE(info.is_available) << "invalid timepicker time: "
                                     << cctz::format(kRFC3339, time, user_tz);
    }
  }
}

struct Time {
  explicit Time(int y, int m = 1, int d = 1, int hh = 0, int mm = 0) {
    ::utils::datetime::MockNowSet(CreateTime(y, m, d, hh, mm));
  }
  ~Time() { ::utils::datetime::MockNowUnset(); }
};

}  // namespace

TEST(BuildTimepicker, Empty) {
  Time time(2021, 1, 11, 12, 0);

  const auto travel = std::chrono::minutes{30};
  const auto preparation = std::chrono::minutes{0};

  Timepicker expected{};
  EXPECT_EQ(expected,
            BuildDeliveryTimepicker(Schedule{}, cctz::utc_time_zone(), travel,
                                    preparation, kNoOffset, true));

  {
    const Schedule schedule{
        TimeInterval{
            CreateTime(2021, 1, 10, 8),   // start
            CreateTime(2021, 1, 10, 20),  // end
        },
        TimeInterval{
            CreateTime(2021, 1, 13, 8),   // start
            CreateTime(2021, 1, 13, 20),  // end
        },
    };
    const auto actual = BuildDeliveryTimepicker(
        schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);

    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, true);
  }
  {
    const Schedule schedule{
        TimeInterval{
            CreateTime(2021, 1, 9, 8),   // start
            CreateTime(2021, 1, 9, 20),  // end
        },
        TimeInterval{
            CreateTime(2021, 1, 10, 8),   // start
            CreateTime(2021, 1, 10, 20),  // end
        },
    };
    const auto actual = BuildDeliveryTimepicker(
        schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, true);
  }
  {
    const Schedule schedule{
        TimeInterval{
            CreateTime(2021, 1, 13, 8),   // start
            CreateTime(2021, 1, 13, 20),  // end
        },
        TimeInterval{
            CreateTime(2021, 1, 18, 8),   // start
            CreateTime(2021, 1, 18, 20),  // end
        },
    };
    const auto actual = BuildDeliveryTimepicker(
        schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, true);
  }
}

TEST(BuildTimepicker, Simple) {
  Time time(2021, 1, 11, 12, 39);

  const std::chrono::minutes interval{30};

  const Schedule schedule{
      TimeInterval{
          CreateTime(2021, 1, 11, 8),   // start
          CreateTime(2021, 1, 11, 20),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 12, 8),   // start
          CreateTime(2021, 1, 12, 20),  // end
      },
  };

  const auto travel = std::chrono::minutes{30};
  const auto preparation = std::chrono::minutes{0};

  {
    const Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 13, 30),  // start
                    CreateTime(2021, 1, 11, 20, 30),  // end
                },
            },
            interval),
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 12, 8, 30),   // start
                    CreateTime(2021, 1, 12, 20, 30),  // end
                },
            },
            interval),
    };

    const auto actual = BuildDeliveryTimepicker(
        schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);

    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, true);
  }
  {
    const Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 13, 30),  // start
                    CreateTime(2021, 1, 11, 20, 0),   // end
                },
            },
            interval),
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 12, 8, 30),  // start
                    CreateTime(2021, 1, 12, 20, 0),  // end
                },
            },
            interval),
    };

    const auto actual =
        BuildDeliveryTimepicker(schedule, cctz::utc_time_zone(), travel,
                                preparation, std::chrono::minutes{30}, true);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);

    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, true);
  }
  {
    const Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 13, 30),  // start
                    CreateTime(2021, 1, 11, 20, 0),   // end
                },
            },
            interval),
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 12, 8, 30),  // start
                    CreateTime(2021, 1, 12, 20, 0),  // end
                },
            },
            interval),
    };

    const auto actual = BuildDeliveryTimepicker(
        schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, false);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);

    BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                           schedule, false);
  }
}

TEST(BuildTimepicker, Compound) {
  Time time(2021, 1, 11, 12, 39);

  const std::chrono::minutes interval{15};
  const auto limit = CreateTime(2021, 1, 12, 22, 0);
  const Schedule schedule{
      TimeInterval{
          CreateTime(2021, 1, 10, 8),   // start
          CreateTime(2021, 1, 10, 20),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 11, 8),   // start
          CreateTime(2021, 1, 11, 13),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 11, 14),  // start
          CreateTime(2021, 1, 11, 15),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 11, 16),  // start
          CreateTime(2021, 1, 11, 18),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 12, 8),   // start
          CreateTime(2021, 1, 12, 10),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 12, 15),  // start
          CreateTime(2021, 1, 12, 18),  // end
      },
      TimeInterval{
          CreateTime(2021, 1, 12, 19),  // start
          CreateTime(2021, 1, 13, 10),  // end
      },
  };
  Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 11, 13, 0),  // start
                  CreateTime(2021, 1, 11, 13, 0),  // end
              },
              {
                  CreateTime(2021, 1, 11, 14, 15),  // start
                  CreateTime(2021, 1, 11, 15, 0),   // end
              },
              {
                  CreateTime(2021, 1, 11, 16, 15),  // start
                  CreateTime(2021, 1, 11, 18, 0),   // end
              },
          },
          interval),
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 12, 8, 15),  // start
                  CreateTime(2021, 1, 12, 10, 0),  // end
              },
              {
                  CreateTime(2021, 1, 12, 15, 15),  // start
                  CreateTime(2021, 1, 12, 18, 0),   // end
              },
              {
                  CreateTime(2021, 1, 12, 19, 15),  // start
                  CreateTime(2021, 1, 12, 21, 45),  // end
              },
          },
          interval),
  };

  const auto actual =
      BuildTimepicker(schedule, cctz::utc_time_zone(), std::chrono::minutes{10},
                      std::chrono::minutes{10}, limit, interval);
  EXPECT_EQ(expected, actual) << Diff(expected, actual);
}

TEST(BuildTimepicker, TodayEmpty) {
  Time time(2021, 1, 11, 12, 0);
  const std::chrono::minutes interval{30};
  const auto limit = CreateTime(2021, 1, 13, 0, 0);

  {
    const Schedule schedule{
        TimeInterval{
            CreateTime(2021, 1, 12, 8, 0),   // start
            CreateTime(2021, 1, 12, 20, 0),  // end
        },
    };
    const Timepicker expected{
        CreatePicker({}, interval),
        CreatePicker(
            {
                TimeInterval{
                    CreateTime(2021, 1, 12, 8, 30),  // start
                    CreateTime(2021, 1, 12, 20, 0),  // end
                },
            },
            interval),
    };
    const auto actual = BuildTimepicker(
        schedule, cctz::utc_time_zone(), std::chrono::minutes{10},
        std::chrono::minutes{0}, limit, interval);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }
  {
    const Schedule schedule{
        {
            CreateTime(2021, 1, 8, 8),   // start
            CreateTime(2021, 1, 8, 20),  // end
        },
        {
            CreateTime(2021, 1, 10, 8),   // start
            CreateTime(2021, 1, 10, 20),  // end
        },
        {
            CreateTime(2021, 1, 12, 8),   // start
            CreateTime(2021, 1, 12, 20),  // end
        },
    };
    const Timepicker expected{
        CreatePicker({}, interval),
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 12, 8, 30),   // start
                    CreateTime(2021, 1, 12, 20, 30),  // end
                },
            },
            interval),
    };
    const auto actual = BuildTimepicker(
        schedule, cctz::utc_time_zone(), std::chrono::minutes{30},
        std::chrono::minutes{30}, limit, interval);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }

  {
    const Schedule schedule{
        {
            CreateTime(2021, 1, 8, 8),   // start
            CreateTime(2021, 1, 8, 20),  // end
        },
        {
            CreateTime(2021, 1, 11, 8),   // start
            CreateTime(2021, 1, 11, 12),  // end
        },
        {
            CreateTime(2021, 1, 12, 8),   // start
            CreateTime(2021, 1, 12, 20),  // end
        },
    };
    const Timepicker expected{
        CreatePicker({}, interval),
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 12, 8, 30),  // start
                    CreateTime(2021, 1, 12, 20, 0),  // end
                },
            },
            interval),
    };
    const auto actual = BuildTimepicker(
        schedule, cctz::utc_time_zone(), std::chrono::minutes{30},
        std::chrono::minutes{0}, limit, interval);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }
}

TEST(BuildTimepicker, TomorrowEmpty) {
  Time time(2021, 1, 11, 12, 21);
  const std::chrono::minutes interval{30};
  const auto limit = CreateTime(2021, 1, 13, 0, 0);

  {
    const Schedule schedule{
        {
            CreateTime(2021, 1, 11, 8, 0),   // start
            CreateTime(2021, 1, 11, 20, 0),  // end
        },
    };
    const Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 13, 0),  // start
                    CreateTime(2021, 1, 11, 20, 0),  // end
                },
            },
            interval),
        {},
    };

    const auto actual = BuildTimepicker(
        schedule, cctz::utc_time_zone(), std::chrono::minutes{25},
        std::chrono::minutes{25}, limit, interval);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }

  {
    const Schedule schedule{
        {
            CreateTime(2021, 1, 8, 8),   // start
            CreateTime(2021, 1, 8, 20),  // end
        },
        {
            CreateTime(2021, 1, 11, 8),   // start
            CreateTime(2021, 1, 11, 20),  // end
        },
        {
            CreateTime(2021, 1, 13, 8),   // start
            CreateTime(2021, 1, 13, 20),  // end
        },
    };
    const Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 12, 30),  // start
                    CreateTime(2021, 1, 11, 20, 0),   // end
                },
            },
            interval),
        {},
    };
    const auto actual = BuildTimepicker(
        schedule, cctz::utc_time_zone(), std::chrono::minutes{5},
        std::chrono::minutes{0}, limit, interval);
    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }
}

TEST(BuildTimepicker, EarlyMorning) {
  Time time(2021, 1, 11, 4);
  const std::chrono::minutes interval{30};
  const auto limit = CreateTime(2021, 1, 13, 0, 0);
  const Schedule schedule{
      {
          CreateTime(2021, 1, 9, 8, 0),
          CreateTime(2021, 1, 9, 20, 0),
      },
      {
          CreateTime(2021, 1, 11, 9, 0),
          CreateTime(2021, 1, 11, 11, 0),
      },
      {
          CreateTime(2021, 1, 11, 19, 0),
          CreateTime(2021, 1, 11, 20, 0),
      },
      {
          CreateTime(2021, 1, 12, 8, 0),
          CreateTime(2021, 1, 12, 10, 0),
      },
      {
          CreateTime(2021, 1, 12, 12, 0),
          CreateTime(2021, 1, 12, 13, 0),
      },
      {
          CreateTime(2021, 1, 12, 15, 0),
          CreateTime(2021, 1, 12, 19, 30),
      },
      {
          CreateTime(2021, 1, 12, 20, 0),
          CreateTime(2021, 1, 12, 22, 0),
      },
  };
  const Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 11, 9, 30),
                  CreateTime(2021, 1, 11, 11, 0),
              },
              {
                  CreateTime(2021, 1, 11, 19, 30),
                  CreateTime(2021, 1, 11, 20, 0),
              },
          },
          interval),

      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 12, 8, 30),
                  CreateTime(2021, 1, 12, 10, 0),
              },
              {
                  CreateTime(2021, 1, 12, 12, 30),
                  CreateTime(2021, 1, 12, 13, 0),
              },
              {
                  CreateTime(2021, 1, 12, 15, 30),
                  CreateTime(2021, 1, 12, 19, 30),
              },
              {
                  CreateTime(2021, 1, 12, 20, 30),
                  CreateTime(2021, 1, 12, 22, 0),
              },
          },
          interval),
  };

  const auto actual =
      BuildTimepicker(schedule, cctz::utc_time_zone(), std::chrono::minutes{10},
                      std::chrono::minutes{10}, limit, interval);
  EXPECT_EQ(expected, actual) << Diff(expected, actual);
}

TEST(BuildTimepicker, LateTonight) {
  Time time(2021, 1, 11, 21, 0);
  const std::chrono::minutes interval{10};

  const Schedule schedule{
      {
          CreateTime(2021, 1, 9, 8),   // start
          CreateTime(2021, 1, 9, 20),  // end
      },
      {
          CreateTime(2021, 1, 11, 0, 0),  // start
          CreateTime(2021, 1, 12, 7, 0),  // end
      },
      {
          CreateTime(2021, 1, 12, 8),   // start
          CreateTime(2021, 1, 12, 10),  // end
      },
      {
          CreateTime(2021, 1, 12, 12),  // start
          CreateTime(2021, 1, 13, 0),   // end
      },
  };

  const Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 11, 21, 20),  // start
                  CreateTime(2021, 1, 12, 6, 0),    // end
              },
          },
          interval),
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 12, 6, 10),  // start
                  CreateTime(2021, 1, 12, 7, 10),  // end
              },
              {
                  CreateTime(2021, 1, 12, 8, 20),   // start
                  CreateTime(2021, 1, 12, 10, 10),  // end
              },
              {
                  CreateTime(2021, 1, 12, 12, 20),  // start
                  CreateTime(2021, 1, 12, 19, 0),   // end
              },
          },
          interval),
  };

  const auto actual = BuildTimepicker(
      schedule, cctz::utc_time_zone(), std::chrono::minutes{17},
      std::chrono::minutes{17}, CreateTime(2021, 1, 12, 19, 5), interval);

  EXPECT_EQ(expected, actual) << Diff(expected, actual);
}

TEST(BuildTimepicker, AllDayRestaurant) {
  Time time(2021, 1, 10, 21, 32);

  const std::chrono::minutes interval{30};

  const Schedule schedule{
      {
          CreateTime(2021, 1, 10, 0, 0),    // start
          CreateTime(2021, 1, 13, 23, 59),  // end
      },
  };
  Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 10, 22, 0),  // start
                  CreateTime(2021, 1, 11, 6, 0),   // end
              },
          },
          interval),

      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 11, 6, 30),   // start
                  CreateTime(2021, 1, 11, 23, 30),  // end
              },
          },
          interval),
  };

  const auto travel = std::chrono::minutes{17};
  const auto preparation = std::chrono::minutes{0};

  const auto actual = BuildDeliveryTimepicker(
      schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);

  EXPECT_EQ(expected, actual) << Diff(expected, actual);

  BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                         schedule, true);
}

TEST(BuildTimepicker, Pickup) {
  const std::chrono::minutes interval{30};
  const Schedule schedule{
      {
          CreateTime(2021, 1, 10, 0, 0),    // start
          CreateTime(2021, 1, 13, 23, 59),  // end
      },
  };

  {
    Time time(2021, 1, 10, 21, 32);
    Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 10, 22, 0),   // start
                    CreateTime(2021, 1, 10, 23, 30),  // end
                },
            },
            interval),

        CreatePicker({}, interval),
    };

    const auto actual = BuildPickupTimepicker(schedule, cctz::utc_time_zone(),
                                              std::chrono::minutes{17});

    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }
  {
    Time time(2021, 1, 11, 11, 10);
    Timepicker expected{
        CreatePicker(
            {
                {
                    CreateTime(2021, 1, 11, 11, 30),  // start
                    CreateTime(2021, 1, 11, 14, 0),   // end
                },
            },
            interval),

        CreatePicker({}, interval),
    };

    const auto actual = BuildPickupTimepicker(schedule, cctz::utc_time_zone(),
                                              std::chrono::minutes{17});

    EXPECT_EQ(expected, actual) << Diff(expected, actual);
  }
}

TEST(BuildTimepicker, AlmostOverlap) {
  Time time(2021, 1, 10, 0, 0);

  const std::chrono::minutes interval{30};
  const Schedule schedule{
      {
          CreateTime(2021, 1, 10, 0, 0),   // start
          CreateTime(2021, 1, 10, 12, 0),  // end
      },
      {
          CreateTime(2021, 1, 10, 12, 0),  // start
          CreateTime(2021, 1, 11, 0, 0),   // end
      },
  };

  Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 10, 0, 30),  // start
                  CreateTime(2021, 1, 11, 0, 0),   // end
              },
          },
          interval),
      CreatePicker({}, interval),
  };

  const auto travel = std::chrono::minutes{17};
  const auto preparation = std::chrono::minutes{0};

  const auto actual = BuildDeliveryTimepicker(
      schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);

  EXPECT_EQ(expected, actual) << Diff(expected, actual);

  BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                         schedule, true);
}

TEST(BuildTimepicker, Overlap) {
  Time time(2021, 1, 10, 0, 0);

  const std::chrono::minutes interval{30};
  const Schedule schedule{
      {
          CreateTime(2021, 1, 10, 0, 0),   // start
          CreateTime(2021, 1, 10, 14, 0),  // end
      },
      {
          CreateTime(2021, 1, 10, 12, 0),  // start
          CreateTime(2021, 1, 11, 0, 0),   // end
      },
  };

  Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 1, 10, 0, 30),  // start
                  CreateTime(2021, 1, 11, 0, 0),   // end
              },
          },
          interval),
      CreatePicker({}, interval),
  };

  const auto travel = std::chrono::minutes{17};
  const auto preparation = std::chrono::minutes{0};

  const auto actual = BuildDeliveryTimepicker(
      schedule, cctz::utc_time_zone(), travel, preparation, kNoOffset, true);

  EXPECT_EQ(expected, actual) << Diff(expected, actual);

  BruteForceDeliveryTest(actual, cctz::utc_time_zone(), travel, preparation,
                         schedule, true);
}

TEST(BuildTimepicker, Offsets) {
  Time time(2021, 4, 17, 0, 0);

  const std::chrono::minutes interval{30};
  const Schedule schedule{
      {
          CreateTime(2021, 4, 17, 0, 0),   // start
          CreateTime(2021, 4, 17, 14, 0),  // end
      },
  };

  Timepicker expected{
      CreatePicker(
          {
              {
                  CreateTime(2021, 4, 17, 1, 0),   // start
                  CreateTime(2021, 4, 17, 13, 0),  // end
              },
          },
          interval),
  };

  const auto actual = BuildTimepicker(
      schedule, cctz::utc_time_zone(), std::chrono::minutes{60},
      std::chrono::minutes{-60}, CreateTime(2021, 5, 1, 0, 0), interval);

  EXPECT_EQ(expected, actual) << Diff(expected, actual);
}

}  // namespace eats_places_availability
