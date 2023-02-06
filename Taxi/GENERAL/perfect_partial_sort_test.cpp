#include <gtest/gtest.h>

#include <vector>

#include "perfect_partial_sort.hpp"

std::vector<int> Slice(const std::vector<int>& v, size_t begin, size_t end) {
  std::vector<int> result;
  for (size_t i = begin; i < end; ++i) {
    result.push_back(v[i]);
  }

  return result;
}

std::vector<int> SortAndSliceSmall(std::vector<int> v, size_t begin,
                                   size_t end) {
  utils::impl::PartialSortForSmallLimit(
      v.begin(), v.begin() + begin, v.begin() + end, v.end(), std::less<int>{});
  return Slice(v, begin, end);
}

std::vector<int> SortAndSliceLarge(std::vector<int> v, size_t begin,
                                   size_t end) {
  utils::impl::PartialSortForLargeLimit(
      v.begin(), v.begin() + begin, v.begin() + end, v.end(), std::less<int>{});
  return Slice(v, begin, end);
}

class PartialSortWithParams
    : public ::testing::TestWithParam<
          std::function<std::vector<int>(std::vector<int>, size_t, size_t)>> {};

TEST_P(PartialSortWithParams, PartialSort) {
  auto sort_func = GetParam();
  // 0 - elems
  EXPECT_EQ(sort_func({}, 0, 0), std::vector<int>{});
  EXPECT_EQ(sort_func({2, 1}, 0, 0), std::vector<int>{});
  EXPECT_EQ(sort_func({2, 1}, 1, 1), std::vector<int>{});
  EXPECT_EQ(sort_func({2, 1}, 2, 2), std::vector<int>{});

  // 1 - elems
  EXPECT_EQ(sort_func({1}, 0, 1), std::vector<int>({1}));
  EXPECT_EQ(sort_func({2, 1}, 0, 1), std::vector<int>({1}));
  EXPECT_EQ(sort_func({2, 1}, 1, 2), std::vector<int>({2}));
  EXPECT_EQ(sort_func({3, 2, 1}, 1, 2), std::vector<int>({2}));

  // 2 - elems
  EXPECT_EQ(sort_func({2, 1}, 0, 2), std::vector<int>({1, 2}));
  EXPECT_EQ(sort_func({2, 1, 0}, 0, 2), std::vector<int>({0, 1}));
  EXPECT_EQ(sort_func({3, 2, 1}, 1, 3), std::vector<int>({2, 3}));
  EXPECT_EQ(sort_func({4, 3, 2, 1}, 1, 3), std::vector<int>({2, 3}));

  // 3 - elems
  EXPECT_EQ(sort_func({2, 1, 0}, 0, 3), std::vector<int>({0, 1, 2}));
  EXPECT_EQ(sort_func({3, 2, 1, 0}, 0, 3), std::vector<int>({0, 1, 2}));
  EXPECT_EQ(sort_func({3, 2, 1, 0}, 1, 4), std::vector<int>({1, 2, 3}));
  EXPECT_EQ(sort_func({4, 3, 2, 1, 0}, 1, 4), std::vector<int>({1, 2, 3}));

  // 4 - elems
  EXPECT_EQ(sort_func({3, 2, 1, 0}, 0, 4), std::vector<int>({0, 1, 2, 3}));
  EXPECT_EQ(sort_func({4, 3, 2, 1, 0}, 0, 4), std::vector<int>({0, 1, 2, 3}));
  EXPECT_EQ(sort_func({4, 3, 2, 1, 0}, 1, 5), std::vector<int>({1, 2, 3, 4}));
  EXPECT_EQ(sort_func({5, 4, 3, 2, 1, 0}, 1, 5),
            std::vector<int>({1, 2, 3, 4}));
}

INSTANTIATE_TEST_CASE_P(SmallAndLarge, PartialSortWithParams,
                        ::testing::Values(SortAndSliceLarge,
                                          SortAndSliceSmall), );
