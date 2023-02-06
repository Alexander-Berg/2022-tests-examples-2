#include <dispatch/matching/grocery/scoreboard/scoreboard.hpp>

#include <gtest/gtest.h>

using namespace united_dispatch::matching::grocery::scoreboard;
using namespace ::models::grocery;

namespace formats::json {

std::ostream& operator<<(std::ostream& os, const Value& val) {
  return os << ToString(val);
}

}  // namespace formats::json

struct PassFilter {};

struct TestFeatures {
  std::optional<reject::Reason> Filter(PassFilter) const {
    return pass ? std::nullopt
                : std::optional{
                      reject::Reason{"Test filter reason",
                                     reject::RejectKind::kItemAndAllDerived}};
  }

  int id;
  bool pass;
  double score;
};

bool operator==(const TestFeatures& lhs, const TestFeatures& rhs) {
  return lhs.pass == rhs.pass && lhs.score == rhs.score && lhs.id == rhs.id;
}

struct TestScoreboardPolicy {
  using Features = TestFeatures;
  using ScoreType = double;

  ScoreType GetScore(const Features& features) const { return features.score; }
};

::formats::json::Value Serialize(
    const TestFeatures& features,
    ::formats::serialize::To<::formats::json::Value>) {
  ::formats::json::ValueBuilder builder(::formats::json::Type::kObject);
  builder["id"] = features.id;
  builder["pass"] = features.pass;
  builder["score_"] = features.score;

  return builder.ExtractValue();
}

TEST(ScoreboardTest, Basic) {
  std::vector<TestFeatures> features{
      TestFeatures{0, false, 10.0}, TestFeatures{1, true, 20.0},
      TestFeatures{2, true, 2.0},   TestFeatures{3, false, 1.0},
      TestFeatures{4, true, 5.0},   TestFeatures{5, false, 100.0},
      TestFeatures{6, true, 101.0},
  };

  Scoreboard scoreboard(
      IteratorFeaturesGenerator{features, FilterChain{PassFilter{}}},
      TestScoreboardPolicy{});

  std::vector<TestFeatures> result;
  while (!scoreboard.Empty()) {
    const auto& elem = scoreboard.PopBest();
    result.push_back(elem);
  }

  std::vector<TestFeatures> expected{
      TestFeatures{6, true, 101.0},
      TestFeatures{1, true, 20.0},
      TestFeatures{4, true, 5.0},
      TestFeatures{2, true, 2.0},
  };

  ASSERT_EQ(expected, result);

  const auto logs = scoreboard.GetLogs();
  const auto expected_logs = ::formats::json::FromString(
      R"({
        "features": [
          {
            "id": 6,
            "pass": true,
            "score_": 101.0,
            "score": 101.0
          },
          {
            "id": 1,
            "pass": true,
            "score_": 20.0,
            "score": 20.0
          },
          {
            "id": 4,
            "pass": true,
            "score_": 5.0,
            "score": 5.0
          },
          {
            "id": 2,
            "pass": true,
            "score_": 2.0,
            "score": 2.0
          }
        ],
        "rejected": [
          {
            "id": 0,
            "pass": false,
            "score_": 10.0,
            "reason": "Test filter reason"
          },
          {
            "id": 3,
            "pass": false,
            "score_": 1.0,
            "reason": "Test filter reason"
          },
          {
            "id": 5,
            "pass": false,
            "score_": 100.0,
            "reason": "Test filter reason"
          }
        ]
      })");

  ASSERT_EQ(expected_logs, logs);
}
