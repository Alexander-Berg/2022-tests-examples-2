#include <yt-logger/constants.hpp>
#include <yt-logger/timestamp.hpp>

#include <chrono>
#include <string>

#include <cctz/time_zone.h>

#include <userver/utils/datetime.hpp>

#include <userver/utest/utest.hpp>

namespace yt_logger {

TEST(Timestamp, Rfc3339Precision6) {
  using namespace std::chrono_literals;
  static const auto local_tz = cctz::fixed_time_zone(3h);
  auto test_time = std::chrono::system_clock::from_time_t(1617965987) + 42ms;

  EXPECT_EQ("2021-04-09T13:59:47.042000+03:00",
            utils::datetime::Timestring(test_time, local_tz.name(),
                                        kRfc3339Precision6Format));

  // check that everything after 6 digits is actually ignored (or rounded).
  // Doesn't matter which in this case - as long as there are exactly 6
  // digits after dot.
  // We need time_point_cast because of MacOS. And test will always work
  // on MacOS even if code is wrong - but who cares about MacOS anyway.
  test_time = std::chrono::time_point_cast<
      std::chrono::system_clock::time_point::duration>(
      std::chrono::system_clock::from_time_t(1617965987) + 42ns);
  EXPECT_EQ("2021-04-09T13:59:47.000000+03:00",
            utils::datetime::Timestring(test_time, local_tz.name(),
                                        kRfc3339Precision6Format));
}

}  // namespace yt_logger
