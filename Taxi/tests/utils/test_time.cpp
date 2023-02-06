#include <gtest/gtest.h>

#include <chrono>

#include "utils/time.hpp"

namespace user_statistics::utils::time {

namespace {  // RoundDateTime
using TimePoint = std::chrono::system_clock::time_point;

template <typename T1, typename T2>
void TestRoundDateTime(TimePoint date, std::chrono::duration<T1, T2> period,
                       TimePoint result) {
  EXPECT_EQ(RoundDateTime(date, period), result);
}

TEST(TestRoundDateTime, Basic) {
  using namespace std::chrono_literals;
  TestRoundDateTime(TimePoint{100s}, 5s, TimePoint{100s});
  TestRoundDateTime(TimePoint{101s}, 5s, TimePoint{100s});
  TestRoundDateTime(TimePoint{102s}, 5s, TimePoint{100s});
  TestRoundDateTime(TimePoint{103s}, 5s, TimePoint{105s});
  TestRoundDateTime(TimePoint{104s}, 5s, TimePoint{105s});
  TestRoundDateTime(TimePoint{105s}, 5s, TimePoint{105s});
}

TEST(TestRoundDateTime, Middle) {
  using namespace std::chrono_literals;
  TestRoundDateTime(TimePoint{110s}, 20s, TimePoint{120s});
  TestRoundDateTime(TimePoint{112s}, 25s, TimePoint{100s});
  TestRoundDateTime(TimePoint{113s}, 25s, TimePoint{125s});
}

TEST(TestRoundDateTime, VariousTimeUnits) {
  using namespace std::chrono_literals;
  TestRoundDateTime(TimePoint{10min + 10s}, 1min, TimePoint{10min});
  TestRoundDateTime(TimePoint{10h + 59min}, 15min, TimePoint{11h});
  TestRoundDateTime(TimePoint{10h + 59min + 4s}, 5s,
                    TimePoint{10h + 59min + 5s});
  TestRoundDateTime(TimePoint{10min + 123456us}, 1min, TimePoint{10min});
  TestRoundDateTime(TimePoint{10min + 1us}, 1us, TimePoint{10min + 1us});
  // nanoseconds don't compile on macOS CI
}

TEST(TestRoundDateTime, ProcessedOrdersCleanUpUseCase) {
  using namespace std::chrono_literals;
  // Не 2020.08.12, но нам любой таймпоинт близкий к сейчас нужен
  const auto date =
      std::chrono::seconds((50 * 365 /* 50 лет с 1970 */ + 8 * 30 + 12) * 24h);
  TestRoundDateTime(TimePoint{date}, 5min, TimePoint{date});
  TestRoundDateTime(TimePoint{date + 14h + 34min}, 5min,
                    TimePoint{date + 14h + 35min});
  TestRoundDateTime(TimePoint{date + 9h + 12min}, 5min,
                    TimePoint{date + 9h + 10min});
  TestRoundDateTime(TimePoint{date + 23h + 55min}, 10min,
                    TimePoint{date + 24h});
}

}  // namespace
}  // namespace user_statistics::utils::time
