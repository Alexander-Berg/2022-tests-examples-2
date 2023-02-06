#include <gtest/gtest.h>

#include "batch.hpp"

using eats_full_text_search::utils::batch::SplitOnBatches;

TEST(SplitOnBatches, Empty) {
  std::vector<int> data;
  const auto result = SplitOnBatches(std::move(data), 10);
  ASSERT_TRUE(result.empty());
}

TEST(SplitOnBatches, OneElementBatchSizeOne) {
  std::vector<int> data{42};
  const auto result = SplitOnBatches(std::move(data), 1);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.front().size(), 1);
  ASSERT_EQ(result.front().front(), 42);
}

TEST(SplitOnBatches, OneElementBatchSizeTwo) {
  std::vector<int> data{42};
  const auto result = SplitOnBatches(std::move(data), 2);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.front().size(), 1);
  ASSERT_EQ(result.front().front(), 42);
}

TEST(SplitOnBatches, TenElementsBatchSizeFour) {
  std::vector<int> data{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
  const auto result = SplitOnBatches(std::move(data), 4);
  ASSERT_EQ(result.size(), 3);
  ASSERT_EQ(result[0], (std::vector<int>{1, 2, 3, 4}));
  ASSERT_EQ(result[1], (std::vector<int>{5, 6, 7, 8}));
  ASSERT_EQ(result[2], (std::vector<int>{9, 10}));
}
