#include <dispatch/matching/grocery/scoreboard/candidate_policy.hpp>

#include <gtest/gtest.h>

using namespace united_dispatch::matching::grocery::scoreboard;
using namespace models::grocery;

TEST(CheckinTimeCandidatePolicyTest, GetScore) {
  const auto now = ::utils::datetime::Now();

  CheckinTimeCandidatePolicy p{now};
  CandidateFeatures features(
      "test_dbid_uuid", CandidateFeatures::TransportType::kPedestrian,
      now - std::chrono::seconds{100}, 25000.0, 1.0,
      ::geometry::Distance::from_value(20000), 2.3, std::chrono::seconds{300});

  ASSERT_EQ(std::chrono::seconds{100}, p.GetScore(features));
}
