#include <gtest/gtest.h>

#include "models/driver_rating.hpp"
#include "test_helpers.hpp"

static const char kDelimiter = '\t';

TEST(DriverRatingsCache, SerilaizeModel) {
  {
    models::DriverRatingInfo info{
        "1", false, "0_0_0", {0.1234567, 1, 0.1234567}};
    const std::string expected = "1\t0.123457\t1\t0.123457\t0\t0_0_0";
    EXPECT_EQ(info.ToString<kDelimiter>(), expected);
    EXPECT_EQ(models::DriverRatingInfo::FromString<kDelimiter>(
                  info.ToString<kDelimiter>())
                  .ToString<kDelimiter>(),
              expected);
  }
  {
    models::DriverRatingInfo info{
        "1", false, "0_0_0", {boost::none, boost::none, boost::none}};
    const std::string expected = "1\t \t \t \t0\t0_0_0";
    EXPECT_EQ(info.ToString<kDelimiter>(), expected);
    EXPECT_EQ(models::DriverRatingInfo::FromString<kDelimiter>(
                  info.ToString<kDelimiter>())
                  .ToString<kDelimiter>(),
              expected);
  }
}
