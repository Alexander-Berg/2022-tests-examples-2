#include <eats-shared/utils/chunk_splitter.hpp>

#include <array>

#include <gtest/gtest.h>

namespace eats_shared::utils {

auto MakeResult(
    std::vector<std::pair<std::vector<int>::const_iterator,
                          std::vector<int>::const_iterator>>&& res) {
  return std::move(res);
}

TEST(SplitIntoChunksAsIterators, EmptyVector) {
  const std::vector<int> vec;
  ASSERT_TRUE(SplitIntoChunksAsIterators(vec, std::nullopt).empty());
  ASSERT_TRUE(SplitIntoChunksAsIterators(vec, 1).empty());
  ASSERT_TRUE(SplitIntoChunksAsIterators(vec, 100).empty());
}

TEST(SplitIntoChunksAsIterators, OneChunk) {
  const std::vector<int> vec(10);
  const auto one_chunk = MakeResult({{vec.cbegin(), vec.cend()}});

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, std::nullopt), one_chunk);
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 10), one_chunk);
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 11), one_chunk);
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 100), one_chunk);
}

TEST(SplitIntoChunksAsIterators, EqualChunks) {
  const std::vector<int> vec(12);
  const auto beg = vec.cbegin();

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 12), MakeResult({{beg, beg + 12}}));

  for (const size_t chunk_size : {11, 10, 9, 8, 7, 6}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg, beg + 6}, {beg + 6, beg + 12}}));
  }

  for (const size_t chunk_size : {5, 4}) {
    ASSERT_EQ(
        SplitIntoChunksAsIterators(vec, chunk_size),
        MakeResult({{beg, beg + 4}, {beg + 4, beg + 8}, {beg + 8, beg + 12}}));
  }

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 3),
            MakeResult({{beg + 0, beg + 3},
                        {beg + 3, beg + 6},
                        {beg + 6, beg + 9},
                        {beg + 9, beg + 12}}));

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 2),
            MakeResult({{beg + 0, beg + 2},
                        {beg + 2, beg + 4},
                        {beg + 4, beg + 6},
                        {beg + 6, beg + 8},
                        {beg + 8, beg + 10},
                        {beg + 10, beg + 12}}));

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 1),
            MakeResult({{beg + 0, beg + 1},
                        {beg + 1, beg + 2},
                        {beg + 2, beg + 3},
                        {beg + 3, beg + 4},
                        {beg + 4, beg + 5},
                        {beg + 5, beg + 6},
                        {beg + 6, beg + 7},
                        {beg + 7, beg + 8},
                        {beg + 8, beg + 9},
                        {beg + 9, beg + 10},
                        {beg + 10, beg + 11},
                        {beg + 11, beg + 12}}));
}

TEST(SplitIntoChunksAsIterators, NonEqualChunks13) {
  const std::vector<int> vec(13);
  const auto beg = vec.cbegin();

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 13), MakeResult({{beg, beg + 13}}));

  for (const size_t chunk_size : {12, 11, 10, 9, 8, 7}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg, beg + 6}, {beg + 6, beg + 13}}));
  }

  for (const size_t chunk_size : {6, 5}) {
    ASSERT_EQ(
        SplitIntoChunksAsIterators(vec, chunk_size),
        MakeResult({{beg, beg + 4}, {beg + 4, beg + 8}, {beg + 8, beg + 13}}));
  }

  // 13 : 4 -> 3 + 3 + 4
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 4),
            MakeResult({{beg + 0, beg + 3},
                        {beg + 3, beg + 6},
                        {beg + 6, beg + 9},
                        {beg + 9, beg + 13}}));

  // 13 : 3 -> 2 + 3 + 2 + 3 + 3
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 3),
            MakeResult({{beg + 0, beg + 2},
                        {beg + 2, beg + 5},
                        {beg + 5, beg + 7},
                        {beg + 7, beg + 10},
                        {beg + 10, beg + 13}}));

  // 13 : 2 -> 1 + 2 + 2 + 2 + 2 + 2 + 2
  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 2),
            MakeResult({{beg + 0, beg + 1},
                        {beg + 1, beg + 3},
                        {beg + 3, beg + 5},
                        {beg + 5, beg + 7},
                        {beg + 7, beg + 9},
                        {beg + 9, beg + 11},
                        {beg + 11, beg + 13}}));
}

TEST(SplitIntoChunksAsIterators, NonEqualChunks1001) {
  const std::vector<int> vec(1001);
  const auto beg = vec.cbegin();

  // 1001 : 1000 -> 500 + 501
  for (const size_t chunk_size : {1000, 950, 678, 501}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg, beg + 500}, {beg + 500, beg + 1001}}));
  }

  // 1001 : 500 -> 333 + 334 + 334
  for (const size_t chunk_size : {500, 334}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg, beg + 333},
                          {beg + 333, beg + 667},
                          {beg + 667, beg + 1001}}));
  }
}

TEST(SplitIntoChunksAsIterators, NonEqualChunks1321) {
  const std::vector<int> vec(1321);
  const auto beg = vec.cbegin();

  // 1321 : 500 -> 440 + 440 + 441
  for (const size_t chunk_size : {660, 500, 441}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg + 0, beg + 440},
                          {beg + 440, beg + 880},
                          {beg + 880, beg + 1321}}));
  }

  // 1321 : 100 ->
  // 94 + 94 + 95 + 94 + 94 + 95 + 94 + 94 + 95 + 94 + 94 + 95 + 94 + 95
  for (const size_t chunk_size : {101, 100, 95}) {
    ASSERT_EQ(SplitIntoChunksAsIterators(vec, chunk_size),
              MakeResult({{beg + 0, beg + 94},
                          {beg + 94, beg + 188},
                          {beg + 188, beg + 283},
                          {beg + 283, beg + 377},
                          {beg + 377, beg + 471},
                          {beg + 471, beg + 566},
                          {beg + 566, beg + 660},
                          {beg + 660, beg + 754},
                          {beg + 754, beg + 849},
                          {beg + 849, beg + 943},
                          {beg + 943, beg + 1037},
                          {beg + 1037, beg + 1132},
                          {beg + 1132, beg + 1226},
                          {beg + 1226, beg + 1321}}));
  }
}

TEST(SplitIntoChunksAsIterators, MutableVector) {
  std::vector<int> vec(13);
  using Iterator = decltype(vec)::iterator;
  using Result = std::vector<std::pair<Iterator, Iterator>>;
  const auto beg = vec.begin();

  ASSERT_EQ(SplitIntoChunksAsIterators(vec, 8),
            (Result{{beg, beg + 6}, {beg + 6, beg + 13}}));
}

TEST(SplitIntoChunksAsIterators, ConstArray) {
  const std::array<int, 13> arr{};
  using Iterator = decltype(arr)::const_iterator;
  using Result = std::vector<std::pair<Iterator, Iterator>>;
  const auto beg = arr.cbegin();

  ASSERT_EQ(SplitIntoChunksAsIterators(arr, 8),
            (Result{{beg, beg + 6}, {beg + 6, beg + 13}}));
}

TEST(SplitIntoChunksAsIterators, MutableArray) {
  std::array<int, 13> arr{};
  using Iterator = decltype(arr)::iterator;
  using Result = std::vector<std::pair<Iterator, Iterator>>;
  const auto beg = arr.begin();

  ASSERT_EQ(SplitIntoChunksAsIterators(arr, 8),
            (Result{{beg, beg + 6}, {beg + 6, beg + 13}}));
}

TEST(SplitIntoChunksAsIterators, MutableCStyleArray) {
  int arr[13];
  using Result = std::vector<std::pair<int*, int*>>;

  ASSERT_EQ(SplitIntoChunksAsIterators(arr, 8),
            (Result{{arr, arr + 6}, {arr + 6, arr + 13}}));
}

}  // namespace eats_shared::utils
