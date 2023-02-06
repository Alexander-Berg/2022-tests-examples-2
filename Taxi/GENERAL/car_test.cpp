
#include <ctime>
#include <limits>

#include <gtest/gtest.h>
#include "car.hpp"

namespace {
const int kManufactureMonth = 8;
}  // namespace

TEST(CarAge, ManufactureYearToAgeOverflows) {
  EXPECT_EQ(std::numeric_limits<uint8_t>::max(),
            models::driver::Car::ManufactureYearToAge(1707, kManufactureMonth));
  // This test will fail quite soon, sorry. Please, just update the year.
  EXPECT_EQ(0,
            models::driver::Car::ManufactureYearToAge(2099, kManufactureMonth));
}

TEST(CarAge, GetEffectiveYear) {
  std::tm calendar;
  calendar.tm_mon = 0;
  calendar.tm_year = 0;
  EXPECT_EQ(1899, models::driver::Car::GetEffectiveYear(&calendar,
                                                        kManufactureMonth));

  for (int month = 0; month < 8; ++month) {
    calendar.tm_mon = month;
    calendar.tm_year = 116;
    EXPECT_EQ(2015, models::driver::Car::GetEffectiveYear(&calendar,
                                                          kManufactureMonth));
  }
  for (int month = 8; month < 12; ++month) {
    calendar.tm_mon = month;
    calendar.tm_year = 116;
    EXPECT_EQ(2016, models::driver::Car::GetEffectiveYear(&calendar,
                                                          kManufactureMonth));
  }
}
