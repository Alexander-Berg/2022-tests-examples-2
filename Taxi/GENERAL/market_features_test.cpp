#include <models/grocery/matching_features/market_features.hpp>

#include <fmt/format.h>

#include <gtest/gtest.h>

using namespace ::models::grocery::matching_features;
using namespace ::models::grocery;

TEST(GroceryMarketFeaturesTest, RejectMarketCombination) {
  MarketFeatures features(0, 3, false);
  ASSERT_EQ(reject::kMarketOrdersWithoutGroceryOrdersForbidden,
            features.Filter(filters::MarketCombination{}));
}

TEST(GroceryMarketFeaturesTest, RejectMarketCombinationWithSingleSegment) {
  MarketFeatures features(0, 1, true);
  ASSERT_EQ(reject::kMarketOrdersShouldBeDeliveredInBatch,
            features.Filter(filters::MarketCombination{}));
}

TEST(GroceryMarketFeaturesTest, AllowMarketCombination) {
  MarketFeatures features(0, 3, true);
  ASSERT_EQ(std::nullopt, features.Filter(filters::MarketCombination{}));
}

TEST(GroceryMarketFeaturesTest, AllowMixedCombination) {
  MarketFeatures features(1, 3, false);
  ASSERT_EQ(std::nullopt, features.Filter(filters::MarketCombination{}));
}

TEST(GroceryMarketFeaturesTest, SegmentCountLimits) {
  MarketFeatures features(2, 2, false);
  ASSERT_EQ(std::nullopt, features.Filter(filters::SegmentCountLimits{3, 3}));
  ASSERT_EQ(reject::kGrocerySegmentCountLimitExceeded,
            features.Filter(filters::SegmentCountLimits{1, 3}));
  ASSERT_EQ(reject::kMarketSegmentCountLimitExceeded,
            features.Filter(filters::SegmentCountLimits{3, 1}));
}
