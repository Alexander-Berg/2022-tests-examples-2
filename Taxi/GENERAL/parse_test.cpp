#include "parse.hpp"

#include <gtest/gtest.h>

#include "models/exceptions.hpp"

namespace price_estimate_api::models {
static auto Tie(const Rll& rll) { return std::tie(rll.p1, rll.p2); }
static bool operator==(const Rll& lhs, const Rll& rhs) {
  return Tie(lhs) == Tie(rhs);
}
}  // namespace price_estimate_api::models
namespace price_estimate_api::utils::test {

TEST(estimate, parse_rll) {
  using ::geometry::lat;
  using ::geometry::lon;
  using models::Rll;
  EXPECT_EQ(ParseRLL("37.55,44~42.0,56.1"),
            (Rll{::geometry::Position{37.55 * lon, 44.0 * lat},
                 ::geometry::Position{42.0 * lon, 56.1 * lat}}));
  EXPECT_EQ(ParseRLL("37.55,44.0~42.0,56.1"),
            (Rll{::geometry::Position{37.55 * lon, 44.0 * lat},
                 ::geometry::Position{42.0 * lon, 56.1 * lat}}));
  EXPECT_EQ(ParseRLL("37.55,44.0 ~ 42.0,56.1"),
            (Rll{::geometry::Position{37.55 * lon, 44.0 * lat},
                 ::geometry::Position{42.0 * lon, 56.1 * lat}}));
  EXPECT_EQ(ParseRLL("\t37,44.5 ~ 42.0,56.1  "),
            (Rll{::geometry::Position{37.0 * lon, 44.5 * lat},
                 ::geometry::Position{42.0 * lon, 56.1 * lat}}));
  EXPECT_EQ(ParseRLL("37.55,44"),
            (Rll{::geometry::Position{37.55 * lon, 44.0 * lat}, {}}));
  EXPECT_EQ(ParseRLL("-37.55,-44.0~-42.0,-56.1"),
            (Rll{::geometry::Position{-37.55 * lon, -44.0 * lat},
                 ::geometry::Position{-42.0 * lon, -56.1 * lat}}));
  EXPECT_THROW(ParseRLL("37.55%2C44~42.0,56.1"), BadRequest);
  EXPECT_THROW(ParseRLL("-,44~42.0,56.1"), BadRequest);
  EXPECT_THROW(ParseRLL("-~42.0,56.1"), BadRequest);
  EXPECT_THROW(ParseRLL("37,55~-56.1"), BadRequest);
  EXPECT_THROW(ParseRLL("37,55~-"), BadRequest);
  EXPECT_THROW(ParseRLL("-"), BadRequest);
  EXPECT_THROW(ParseRLL("37.55,44~42.0"), BadRequest);
  EXPECT_THROW(ParseRLL("37.55,44~"), BadRequest);
  EXPECT_THROW(ParseRLL("~42.0,56.1"), BadRequest);
  EXPECT_THROW(ParseRLL("~"), BadRequest);
  EXPECT_THROW(ParseRLL("37.55"), BadRequest);
}

}  // namespace price_estimate_api::utils::test
