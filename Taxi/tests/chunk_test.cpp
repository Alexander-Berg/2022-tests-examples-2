#include <userver/utest/utest.hpp>

#include <utils/chunk.hpp>

TEST(Chunks, Empty) {
  {
    std::vector<int> empty;

    const auto& chunks = utils::SplitToChunks(std::move(empty), 10);
    EXPECT_TRUE(chunks.empty());
  }
  {
    std::vector<int> empty;
    EXPECT_ANY_THROW(utils::SplitToChunks(std::move(empty), 0));
  }
}

TEST(Chunks, Equal) {
  {
    std::vector<int> data{0, 1, 2, 3, 4};
    auto chunks = utils::SplitToChunks(std::move(data), 2);
    EXPECT_EQ(chunks.size(), 3u);
    EXPECT_EQ(chunks[0], std::vector({0, 1}));
    EXPECT_EQ(chunks[1], std::vector({2, 3}));
    EXPECT_EQ(chunks[2], std::vector({4}));
  }

  {
    std::vector<int> data{0, 1, 2, 3, 4};
    auto chunks = utils::SplitToChunks(std::move(data), 3);
    EXPECT_EQ(chunks.size(), 2u);
    EXPECT_EQ(chunks[0], std::vector({0, 1, 2}));
    EXPECT_EQ(chunks[1], std::vector({3, 4}));
  }

  {
    std::vector<int> data{0, 1, 2, 3, 4};
    auto chunks = utils::SplitToChunks(std::move(data), 5);
    EXPECT_EQ(chunks.size(), 1u);
    EXPECT_EQ(chunks.front(), data);
  }

  {
    std::vector<int> data{0, 1, 2, 3, 4};
    auto chunks = utils::SplitToChunks(std::move(data), 10);
    EXPECT_EQ(chunks.size(), 1u);
    EXPECT_EQ(chunks.front(), data);
  }
}
