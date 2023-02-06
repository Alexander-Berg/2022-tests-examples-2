#include <models/grocery/matching_features.hpp>

#include <gtest/gtest.h>

using namespace models::grocery::matching_features;
using namespace models::grocery;

const auto kTestPath =
    Path(Path::Container{}, ::geometry::Distance::from_value(1000.0),
         ::geometry::Distance::from_value(2000.0),
         ::geometry::Distance::from_value(500.0), std::chrono::seconds{1200},
         std::chrono::seconds{2400});

const auto kTestAggregatedSegmentFeatures = AggregatedSegmentFeatures(
    1000.0, 0.25, std::chrono::system_clock::time_point::max(), true, false,
    true, 0);

const auto kTestMarketFeatures = MarketFeatures(2, 0, false);

TEST(GroceryMatchingFeaturesTest, FilterTakenSegments) {
  {
    auto combination = SegmentCombination{}.Push(2).Push(5);

    SegmentCombinationFeatures features{
        combination, kTestPath, kTestAggregatedSegmentFeatures,
        kTestMarketFeatures, SegmentsMeta{::formats::json::Value{}}};

    TakenSegments taken{1, 3, 4};

    ASSERT_EQ(std::nullopt, features.Filter(filters::TakenSegment{taken}));
  }
  {
    auto combination = SegmentCombination{}.Push(1).Push(2);

    SegmentCombinationFeatures features{
        combination, kTestPath, kTestAggregatedSegmentFeatures,
        kTestMarketFeatures, SegmentsMeta{::formats::json::Value{}}};

    TakenSegments taken{1, 3, 4};

    ASSERT_EQ(reject::kSegmentTaken,
              features.Filter(filters::TakenSegment{taken}));
  }
}

TEST(GroceryMatchingFeaturesTest, FilterCandidateCheckinTime) {
  {
    CandidateFeatures features(
        "test_dbid_uuid", CandidateFeatures::TransportType::kPedestrian,
        std::chrono::system_clock::time_point::max(), 25000, 1000,
        ::geometry::Distance::from_value(20000), 2.3,
        std::chrono::seconds{300});

    ASSERT_EQ(std::nullopt,
              features.Filter(filters::CandidateWithoutCheckinTime{}));
  }
  {
    CandidateFeatures features(
        "test_dbid_uuid", CandidateFeatures::TransportType::kPedestrian,
        std::nullopt, 25000, 1000, ::geometry::Distance::from_value(20000), 2.3,
        std::chrono::seconds{300});

    ASSERT_EQ(reject::kCheckinTimeUnknown,
              features.Filter(filters::CandidateWithoutCheckinTime{}));
  }
}
