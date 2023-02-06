#include <gtest/gtest.h>

#include <unordered_set>

#include <models/chunk.hpp>

#include <set>

namespace {

template <typename Container, typename ChunkFunction>
void TestEmpty(ChunkFunction get_chunks) {
  const Container empty;

  const auto& chunks = get_chunks(empty, 10);
  EXPECT_TRUE(chunks.empty());

  EXPECT_ANY_THROW(get_chunks(empty, 0));
}

template <typename Container, typename ChunkFunction>
void TestBasic(ChunkFunction get_chunks) {
  const Container data{0, 1, 2, 3, 4};

  auto chunks = get_chunks(data, 2);
  EXPECT_EQ(chunks.size(), 3u);
  EXPECT_EQ(chunks[0], std::vector({0, 1}));
  EXPECT_EQ(chunks[1], std::vector({2, 3}));
  EXPECT_EQ(chunks[2], std::vector({4}));

  chunks = get_chunks(data, 3);
  EXPECT_EQ(chunks.size(), 2u);
  EXPECT_EQ(chunks[0], std::vector({0, 1, 2}));
  EXPECT_EQ(chunks[1], std::vector({3, 4}));

  chunks = get_chunks(data, 5);
  EXPECT_EQ(chunks.size(), 1u);
  EXPECT_EQ(chunks.front(), data);

  chunks = get_chunks(data, 10);
  EXPECT_EQ(chunks.size(), 1u);
  EXPECT_EQ(chunks.front(), data);
}

void TestUnordered() {
  const std::unordered_set<int> data{0, 1, 2, 3, 4};

  auto chunks = models::ChunkViews(data, 2);
  std::unordered_set<int> result;
  for (const auto& chunk : chunks) {
    for (auto elem : chunk) {
      result.insert(elem);
    }
  }
  EXPECT_EQ(result, data);
}

}  // namespace

TEST(Chunks, Empty) {
  TestEmpty<std::vector<int>>(models::Chunks<int>);
  TestEmpty<std::vector<int>>(models::ChunkViews<std::vector, int>);
  TestEmpty<std::set<int>>(models::ChunkViews<std::set, int>);
}

TEST(Chunks, Equal) {
  TestBasic<std::vector<int>>(models::Chunks<int>);
  TestBasic<std::vector<int>>(models::ChunkViews<std::vector, int>);
  TestBasic<std::set<int>>(models::ChunkViews<std::set, int>);
  TestUnordered();
}
