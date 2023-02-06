#include <gtest/gtest.h>

#include "api_base/utils.hpp"

TEST(ApiOverDbUtils, ParseRevision) {
  auto ts = api_over_db::utils::GetTimestampFromRevision(
      "0_1244987904_2523637650",
      formats::parse::To<formats::bson::Timestamp>());
  EXPECT_EQ(1244987904u, ts.GetTimestamp());
  EXPECT_EQ(2523637650u, ts.GetIncrement());
}
