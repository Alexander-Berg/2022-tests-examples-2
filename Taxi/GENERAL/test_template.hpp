#pragma once

#include <userver/utest/utest.hpp>

#include <iterator>
#include <list>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

#include <itertools-cpp/chunker.hpp>

namespace {

using VectorType = std::vector<std::string>;
using IteratorType = typename VectorType::iterator;
using ConstIteratorType = typename VectorType::const_iterator;
using MoveIteratorType =
    decltype(std::make_move_iterator(std::declval<IteratorType>()));

template <class ChunksType>
size_t RemainderSize(ChunksType&& chunks) {
  auto chunk_it = chunks.begin();
  for (size_t i = 0; i < chunks.size() - 1; ++i, ++chunk_it) {
  }
  return chunk_it->size();
}

TEST(TEST_NAME, CopyAndMove) {
  {
    std::vector<std::string> vec{"very_long_string_to_allocate_in_heap_1",
                                 "very_long_string_to_allocate_in_heap_2",
                                 "very_long_string_to_allocate_in_heap_3"};
    auto chunks = MakeChunksClosure(vec, 1);
    ASSERT_EQ(chunks.size(), 3);

    // only auto& or const auto&
    for (const auto& chunk : chunks) {
      ASSERT_EQ(chunk.size(), 1);
      ASSERT_EQ(chunk.begin()->size(), 38);
      auto v = chunk.As<std::vector<std::string>>();
      ASSERT_EQ(v.size(), 1);
      ASSERT_EQ(v.begin()->size(), 38);
      ASSERT_EQ(chunk.size(), 1);
      ASSERT_EQ(chunk.begin()->size(), 38);
    }
  }

  {
    std::vector<std::string> vec{"very_long_string_to_allocate_in_heap_1",
                                 "very_long_string_to_allocate_in_heap_2",
                                 "very_long_string_to_allocate_in_heap_3"};
    auto chunks = MakeChunksClosure(std::move(vec), 1);
    ASSERT_EQ(chunks.size(), 3);

    // only auto&& and std::move(chunk).As<std::vector<std::string>>()
    for (auto&& chunk : chunks) {
      ASSERT_EQ(chunk.size(), 1);
      ASSERT_EQ(chunk.begin()->size(), 38);
      auto v = std::move(chunk).As<std::vector<std::string>>();
      ASSERT_EQ(v.size(), 1);
      ASSERT_EQ(v.begin()->size(), 38);
      ASSERT_EQ(chunk.size(), 1);
      ASSERT_NE(chunk.begin()->size(), 38);  // moved away
    }
  }
}

TEST(TEST_NAME, Remainder) {
  {
    std::vector<int> vec(120);
    for (size_t chunk_size : {1, 2, 3, 4, 5, 6}) {
      auto chunks = MakeChunksClosure(vec, chunk_size);
      ASSERT_EQ(chunks.size(), vec.size() / chunk_size);
      ASSERT_EQ(RemainderSize(chunks), chunk_size);
    }
  }

  {
    std::vector<int> vec(17);  // size is prime, guarantees remainder != 0
    for (size_t chunk_size : {2, 3, 4, 5, 6, 7, 8}) {
      auto num_chunks = std::ceil(vec.size() / double(chunk_size));
      auto remainder = vec.size() % chunk_size;

      auto chunks = MakeChunksClosure(vec, chunk_size);
      ASSERT_EQ(chunks.size(), num_chunks);
      ASSERT_EQ(RemainderSize(chunks), remainder);
    }
  }
}

struct CopyAndMoveCounter {
  // kinda global variables
  inline static size_t num_copies = 0;
  inline static size_t num_moves = 0;
  static void Reset() {
    num_copies = 0;
    num_moves = 0;
  }

  CopyAndMoveCounter() = default;

  CopyAndMoveCounter(const CopyAndMoveCounter&) { ++num_copies; }
  CopyAndMoveCounter& operator=(const CopyAndMoveCounter&) {
    ++num_copies;
    return *this;
  }

  CopyAndMoveCounter(CopyAndMoveCounter&&) { ++num_moves; }
  CopyAndMoveCounter& operator=(CopyAndMoveCounter&&) {
    ++num_moves;
    return *this;
  }
};

TEST(TEST_NAME, NumCopiesMoves) {
  for (size_t chunk_size = 1; chunk_size < 10; ++chunk_size) {
    std::vector<CopyAndMoveCounter> vec(9);
    auto chunks = MakeChunksClosure(vec, chunk_size);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    for (const auto& chunk : chunks) {
      auto v = chunk.As<std::vector<CopyAndMoveCounter>>();
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 9);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    CopyAndMoveCounter::Reset();
  }

  for (size_t chunk_size = 1; chunk_size < 10; ++chunk_size) {
    std::vector<CopyAndMoveCounter> vec(9);
    auto chunks = MakeChunksClosure(std::move(vec), chunk_size);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    for (auto&& chunk : chunks) {
      auto v = std::move(chunk).As<std::vector<CopyAndMoveCounter>>();
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 9);
    CopyAndMoveCounter::Reset();
  }
}

TEST(TEST_NAME, View) {
  const size_t chunk_size = 4;
  {
    std::vector<CopyAndMoveCounter> vec(9);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    auto chunks = MakeChunksClosure(vec, chunk_size);
    for (const auto& chunk : chunks) {
      for (const auto& item : chunk) {
        static_assert(
            std::is_same_v<decltype(item), const CopyAndMoveCounter&>);
      }
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    CopyAndMoveCounter::Reset();
  }

  {
    std::vector<CopyAndMoveCounter> vec(9);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    auto chunks = MakeChunksClosure(std::move(vec), chunk_size);
    for (auto&& chunk : chunks) {
      for (auto&& item : chunk) {
        static_assert(std::is_same_v<decltype(item), CopyAndMoveCounter&&>);
      }
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    CopyAndMoveCounter::Reset();
  }

  {
    std::vector<CopyAndMoveCounter> vec(9);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    auto chunks = MakeChunksClosure(vec, chunk_size);
    for (const auto& chunk : chunks) {
      for (const auto& item : chunk) {
        auto i = item;
      }
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 9);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    CopyAndMoveCounter::Reset();
  }

  {
    std::vector<CopyAndMoveCounter> vec(9);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    auto chunks = MakeChunksClosure(std::move(vec), chunk_size);
    for (auto&& chunk : chunks) {
      for (auto&& item : chunk) {
        auto i = item;  // copy constructor
      }
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 9);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    CopyAndMoveCounter::Reset();
  }

  {
    std::vector<CopyAndMoveCounter> vec(9);
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 0);
    auto chunks = MakeChunksClosure(std::move(vec), chunk_size);
    for (auto&& chunk : chunks) {
      for (auto&& item : chunk) {
        auto i = std::move(item);  // move constructor
      }
    }
    ASSERT_EQ(CopyAndMoveCounter::num_copies, 0);
    ASSERT_EQ(CopyAndMoveCounter::num_moves, 9);
    CopyAndMoveCounter::Reset();
  }
}

TEST(TEST_NAME, As) {
  std::vector<std::string> vec{"1", "2", "3", "4"};

  auto chunks = MakeChunksClosure(vec, 3);
  const auto& first = *chunks.begin();

  auto v = first.As<std::vector<std::string>>();
  auto v_exp = std::vector<std::string>{"1", "2", "3"};
  ASSERT_EQ(v, v_exp);

  auto l = first.As<std::list<std::string>>();
  auto l_exp = std::list<std::string>{"1", "2", "3"};
  ASSERT_EQ(l, l_exp);

  auto s = first.As<std::set<std::string>>();
  auto s_exp = std::set<std::string>{"1", "2", "3"};
  ASSERT_EQ(s, s_exp);

  auto u = first.As<std::unordered_set<std::string>>();
  auto u_exp = std::unordered_set<std::string>{"1", "2", "3"};
  ASSERT_EQ(u, u_exp);
}

TEST(TEST_NAME, From) {
  const std::list<std::string> lst{"1", "2", "3", "4"};
  const std::set<std::string> tree{"1", "2", "3", "4"};
  // unordered_set is unordered, so the contents of the chunks may differ

  const std::vector<std::string> expected_vec{"1", "2", "3"};
  const std::list<std::string> expected_lst{"1", "2", "3"};
  const std::set<std::string> expected_tree{"1", "2", "3"};

  {
    auto chunks = MakeChunksClosure(lst, 3);
    const auto& first = *chunks.begin();

    auto v = first.As<std::vector<std::string>>();
    ASSERT_EQ(v, expected_vec);

    auto l = first.As<std::list<std::string>>();
    ASSERT_EQ(l, expected_lst);

    auto s = first.As<std::set<std::string>>();
    ASSERT_EQ(s, expected_tree);
  }

  {
    auto chunks = MakeChunksClosure(tree, 3);
    const auto& first = *chunks.begin();

    auto v = first.As<std::vector<std::string>>();
    ASSERT_EQ(v, expected_vec);

    auto l = first.As<std::list<std::string>>();
    ASSERT_EQ(l, expected_lst);

    auto s = first.As<std::set<std::string>>();
    ASSERT_EQ(s, expected_tree);
  }
}

}  // namespace
