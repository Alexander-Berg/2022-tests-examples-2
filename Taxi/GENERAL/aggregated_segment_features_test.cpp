#include <models/grocery/matching_features/aggregated_segment_features.hpp>
#include <models/grocery/reject_reason.hpp>

#include <geometry/distance.hpp>
#include "models/grocery/matching_features/filters.hpp"

#include <gtest/gtest.h>

using namespace models::grocery::matching_features;
using namespace models::grocery;

TEST(GroceryAggregatedSegmentFeaturesTest, FilterRover) {
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false, true,
        false, 0);

    ASSERT_EQ(std::nullopt, features.Filter(filters::Rover{true}));
  }
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false,
        false, false, 0);
    ASSERT_EQ(reject::kRoverNotAllowed, features.Filter(filters::Rover{true}));
  }
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false, true,
        true, 0);
    ASSERT_EQ(reject::kRoverCantDeliverBatches,
              features.Filter(filters::Rover{true}));
  }
}

TEST(GroceryAggregatedSegmentFeaturesTest, FilterBatch) {
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false,
        false, false, 0);

    ASSERT_EQ(std::nullopt, features.Filter(filters::BatchDelivery{}));
  }
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), true, false,
        false, 0);

    ASSERT_EQ(std::nullopt, features.Filter(filters::BatchDelivery{}));
  }
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), true, false,
        true, 0);

    ASSERT_EQ(std::nullopt, features.Filter(filters::BatchDelivery{}));
  }
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false,
        false, true, 0);

    ASSERT_EQ(reject::kBatchNotAllowed,
              features.Filter(filters::BatchDelivery{}));
  }
}

TEST(GroceryAggregatedSegmentFeaturesTest, FilterWeightLimit) {
  AggregatedSegmentFeatures features(
      1000.0, 0.25, std::chrono::system_clock::time_point::max(), false, false,
      false, 0);

  ASSERT_EQ(std::nullopt,
            features.Filter(filters::WeightVolumeDistanceLimits{
                1001.0, 1000.0, ::geometry::Distance::from_value(0.0)}));

  ASSERT_EQ(reject::kWeightLimitExceeded,
            features.Filter(filters::WeightVolumeDistanceLimits{
                999.0, 1000.0, ::geometry::Distance::from_value(0.0)}));
}

TEST(GroceryAggregatedSegmentFeaturesTest, FilterVolumeLimit) {
  AggregatedSegmentFeatures features(
      1000.0, 0.25, std::chrono::system_clock::time_point::max(), false, false,
      true, 0);

  ASSERT_EQ(std::nullopt,
            features.Filter(filters::WeightVolumeDistanceLimits{
                1001.0, 0.26, ::geometry::Distance::from_value(0.0)}));

  ASSERT_EQ(reject::kVolumeLimitExceeded,
            features.Filter(filters::WeightVolumeDistanceLimits{
                1001.0, 0.24, ::geometry::Distance::from_value(0.0)}));
}

TEST(GroceryAggregatedSegmentFeaturesTest, FilterMultiplePlaceFirstInBatch) {
  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false,
        false, false, 1);

    ASSERT_EQ(std::nullopt, features.Filter(filters::PlaceFirstInBatch{}));
  }

  {
    AggregatedSegmentFeatures features(
        1000.0, 0.25, std::chrono::system_clock::time_point::max(), false,
        false, false, 2);

    ASSERT_EQ(reject::kMultiplePlaceFirstInBatchSegments,
              features.Filter(filters::PlaceFirstInBatch{}));
  }
}
