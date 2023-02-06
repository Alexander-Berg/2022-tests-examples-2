#include "utils.hpp"

#include <gtest/gtest.h>

namespace handlers::internal_v1_catalog_for_layout::post {

namespace {

template <typename OutT, typename InT>
struct SplitTestCase {
  std::vector<InT> input;
  int max_chunk_size;
  std::vector<std::vector<OutT>> expected;
};

template <typename OutT, typename InT>
void TestSplitIntoChunks(const SplitTestCase<OutT, InT>& tc) {
  const auto& result = SplitIntoChunks<OutT, InT>(tc.input, tc.max_chunk_size);
  EXPECT_EQ(tc.expected, result);
}

}  // namespace

TEST(SplitIntoChunks, MultipleChunks) {
  SplitTestCase<int, int> tc{
      {0, 1, 2, 3, 4, 5, 6},       // input
      3,                           // max_chunk_size
      {{0, 1, 2}, {3, 4, 5}, {6}}  // expected
  };
  TestSplitIntoChunks(tc);
}

TEST(SplitIntoChunks, EmptyInput) {
  SplitTestCase<int, int> tc{
      {},  // input
      3,   // max_chunk_size
      {}   // expected
  };
  TestSplitIntoChunks(tc);
}

TEST(SplitIntoChunks, MaxChunkSizeOne) {
  SplitTestCase<int, int> tc{
      {0, 1, 2, 3},         // input
      1,                    // max_chunk_size
      {{0}, {1}, {2}, {3}}  // expected
  };
  TestSplitIntoChunks(tc);
}

TEST(SplitIntoChunks, MaxChunkSizeEqualsInputSize) {
  SplitTestCase<int, int> tc{
      {0, 1, 2, 3, 4, 5, 6},   // input
      7,                       // max_chunk_size
      {{0, 1, 2, 3, 4, 5, 6}}  // expected
  };
  TestSplitIntoChunks(tc);
}

TEST(SplitIntoChunks, MaxChunkSizeExceedsInputSize) {
  SplitTestCase<int, int> tc{
      {0, 1, 2, 3, 4, 5, 6},   // input
      100,                     // max_chunk_size
      {{0, 1, 2, 3, 4, 5, 6}}  // expected
  };
  TestSplitIntoChunks(tc);
}

}  // namespace handlers::internal_v1_catalog_for_layout::post
