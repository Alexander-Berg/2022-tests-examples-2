#include "unique_driver.hpp"

#include <gtest/gtest.h>

using UniqueDriverNewbieParam =
    std::tuple<bool, short,
               boost::optional<std::chrono::system_clock::time_point>>;

class UniqueDriverNewbie
    : public ::testing::Test,
      public ::testing::WithParamInterface<UniqueDriverNewbieParam> {};

TEST_P(UniqueDriverNewbie, One) {
  models::driver::UniqueDriver driver;

  bool newbie;
  std::tie(newbie, driver.exam_score, driver.acknowledged_time) = GetParam();

  EXPECT_EQ(newbie, driver.IsNewbie());
}

INSTANTIATE_TEST_CASE_P(
    UniqueDriver, UniqueDriverNewbie,
    ::testing::Values(
        UniqueDriverNewbieParam(true, 0, boost::none),
        UniqueDriverNewbieParam(true, 1, boost::none),
        UniqueDriverNewbieParam(true, 2, boost::none),
        UniqueDriverNewbieParam(false, 3, boost::none),
        UniqueDriverNewbieParam(false, 4, boost::none),
        UniqueDriverNewbieParam(false, 5, boost::none),
        UniqueDriverNewbieParam(false, 0,
                                std::chrono::system_clock::time_point()),
        UniqueDriverNewbieParam(true, 1,
                                std::chrono::system_clock::time_point()),
        UniqueDriverNewbieParam(true, 2,
                                std::chrono::system_clock::time_point()),
        UniqueDriverNewbieParam(false, 3,
                                std::chrono::system_clock::time_point()),
        UniqueDriverNewbieParam(false, 4,
                                std::chrono::system_clock::time_point()),
        UniqueDriverNewbieParam(false, 5,
                                std::chrono::system_clock::time_point())), );
