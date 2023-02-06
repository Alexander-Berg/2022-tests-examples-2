#include "chunks.hpp"

#include <userver/utest/utest.hpp>

namespace utils {

TEST(ChunksTest, ChunkCount) {
  EXPECT_EQ(GetChunkCount(10, 2), 5);
  EXPECT_EQ(GetChunkCount(10, 3), 4);
  EXPECT_EQ(GetChunkCount(10, 1000), 1);
  EXPECT_EQ(GetChunkCount(10, 1000), 1);
  EXPECT_THROW(GetChunkCount(10, 0), std::invalid_argument);
  EXPECT_THROW(GetChunkCount(0, 10), std::invalid_argument);
}

TEST(ChunksTest, SplitByChunks) {
  auto result1 =
      SplitByChunks({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"}, 3);
  EXPECT_EQ(result1.size(), 4);
  EXPECT_EQ(result1[0].size(), 3);
  EXPECT_EQ(result1[3].size(), 1);
  EXPECT_EQ(result1[0].front(), "a");
  EXPECT_EQ(result1[0].back(), "c");
  EXPECT_EQ(result1[2].front(), "g");
  EXPECT_EQ(result1[2].back(), "i");
  EXPECT_EQ(result1[3].front(), "j");
  EXPECT_EQ(result1[3].back(), "j");

  auto result2 =
      SplitByChunks({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"}, 1000);
  EXPECT_EQ(result2.size(), 1);
  EXPECT_EQ(result2[0].size(), 10);
  EXPECT_EQ(result2[0].front(), "a");
  EXPECT_EQ(result2[0].back(), "j");

  EXPECT_THROW(SplitByChunks({}, 3), std::invalid_argument);
  EXPECT_THROW(
      SplitByChunks({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"}, 0),
      std::invalid_argument);
}

}  // namespace utils
