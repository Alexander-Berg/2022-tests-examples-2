#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include <models/postgres/digest.hpp>

namespace hejmdal::models::postgres {

TEST(TestDigest, GetNotOkPercent) {
  models::postgres::Digest digest1{
      1,  "test digest", "a@a.a", time::TimePoint{}, 1, "incident_list", "",
      {}, std::nullopt,  {}};
  EXPECT_DOUBLE_EQ(0.0, digest1.GetNotOkTimeFraction());

  models::postgres::Digest digest2{
      1,
      "test digest",
      "a@a.a",
      time::TimePoint{},
      1,
      "incident_list",
      "",
      {},
      std::nullopt,
      formats::json::MakeObject("not_ok_time_fraction", 0.2)};

  EXPECT_DOUBLE_EQ(0.2, digest2.GetNotOkTimeFraction());
}

}  // namespace hejmdal::models::postgres
