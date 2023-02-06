#include "flatten.hpp"

#include <gtest/gtest.h>
#include <boost/noncopyable.hpp>
#include <boost/range/adaptors.hpp>

#include <list>
#include <numeric>
#include <unordered_set>
#include <vector>

#include "as.hpp"

namespace {

using VecVecInt = std::vector<std::vector<int>>;
using FlattenIt =
    detail::FlattenIterator<VecVecInt::iterator, std::vector<int>::iterator>;
using FlattenCIt = detail::FlattenIterator<VecVecInt::const_iterator,
                                           std::vector<int>::const_iterator>;

int Increment(const int& value) { return value + 1; }

struct NonCopyable : public boost::noncopyable {
  NonCopyable() = default;
  NonCopyable(NonCopyable&&) noexcept {}
  NonCopyable& operator=(NonCopyable&&) noexcept { return *this; }
};

struct NonMovable {
  NonMovable() = default;
  NonMovable(const NonMovable&) = default;
  NonMovable& operator=(const NonMovable&) = default;

 private:
  NonMovable(NonMovable&&) = delete;
  NonMovable& operator=(NonMovable&&) = delete;
};

}  // namespace

TEST(TestFlatten, EmptyContainersIterator) {
  VecVecInt vec_vec{{}, {}, {}};

  FlattenIt begin(vec_vec.begin(), vec_vec.end());
  ASSERT_TRUE(begin.Empty());

  FlattenIt end(vec_vec.end(), vec_vec.end());

  ASSERT_EQ(begin, end);
  ASSERT_THROW(*begin, std::out_of_range);
  ASSERT_THROW(++end, std::out_of_range);

  [[maybe_unused]] auto mutable_range =
      detail::FlattenRange<VecVecInt::iterator, std::vector<int>::iterator>(
          vec_vec);
  [[maybe_unused]] auto range =
      detail::FlattenRange<VecVecInt::const_iterator,
                           std::vector<int>::const_iterator>(vec_vec);
}

TEST(TestFlatten, FilledContainers) {
  VecVecInt vec_vec{{1, 2, 3}, {}, {100}, {}};

  FlattenIt begin(vec_vec.begin(), vec_vec.end());
  FlattenIt end(vec_vec.end(), vec_vec.end());
  ASSERT_TRUE(begin != end);

  // Check two passes
  ASSERT_EQ(std::accumulate(begin, end, 0), 106);
  ASSERT_EQ(std::accumulate(begin, end, 0), 106);

  for (auto it = begin; it != end; ++it) {
    ASSERT_FALSE(it.Empty());
    ASSERT_NO_THROW(*it);
  }
}

TEST(TestFlatten, TransformedContainers) {
  using boost::adaptors::transformed;
  VecVecInt vec_vec{{1, 2, 3}, {}, {100}, {}};

  const auto& range = vec_vec | transformed([](const std::vector<int>& v) {
                        return std::list<int>(v.begin(), v.end());
                      }) |
                      Flatten();

  const auto& begin = range.begin();
  const auto& end = range.end();

  ASSERT_TRUE(begin != end);

  // Check two passes
  ASSERT_EQ(std::accumulate(begin, end, 0), 106);
  ASSERT_EQ(std::accumulate(begin, end, 0), 106);

  for (auto it = begin; it != end; ++it) {
    ASSERT_FALSE(it.Empty());
    ASSERT_NO_THROW(*it);
  }
}

TEST(TestFlatten, Mutate) {
  VecVecInt vec_vec{{1, 2}, {}, {3, 4}};
  auto range = detail::FlattenMutable(vec_vec);
  ASSERT_EQ(std::accumulate(range.begin(), range.end(), 0), 10);

  for (int& i : range) {
    ++i;
  }

  ASSERT_EQ(std::accumulate(range.begin(), range.end(), 0), 14);
}

TEST(TestFlatten, FlattenOperator) {
  VecVecInt vec_vec{{}, {1, 2}, {}};
  auto range = vec_vec | Flatten();
  ASSERT_EQ(std::accumulate(range.begin(), range.end(), 0), 3);

  for (int& i : range) {
    ++i;
  }
  ASSERT_EQ(std::accumulate(range.begin(), range.end(), 0), 5);

  const VecVecInt c_vec_vec{{}, {3, 4}};
  auto c_range = c_vec_vec | Flatten();
  ASSERT_EQ(std::accumulate(c_range.begin(), c_range.end(), 0), 7);
}

TEST(TestFlatten, Transformed) {
  const std::vector<std::set<int>> vec_set{{10}, {4, 6, 1}};
  const std::vector<int> expected{11, 2, 5, 7};

  {
    const auto incremented =
        Eval(vec_set | Flatten() | boost::adaptors::transformed(Increment));
    ASSERT_TRUE(expected == incremented);
  }

  {
    const auto incremented =
        boost::adaptors::transform(vec_set | Flatten(), Increment);
    ASSERT_TRUE(expected == incremented);
  }
}

TEST(TestFlatten, NonCopyable) {
  std::list<std::list<NonCopyable>> data;
  data.emplace_back(std::list<NonCopyable>(5));
  data.emplace_back(std::list<NonCopyable>());
  data.emplace_back(std::list<NonCopyable>(10));

  const auto range = data | Flatten();
  ASSERT_EQ(std::distance(range.begin(), range.end()), 15u);
}

TEST(TestFlatten, NonMovable) {
  std::list<std::list<NonMovable>> data;
  data.push_back(std::list<NonMovable>(0));
  data.push_back(std::list<NonMovable>(5));
  data.push_back(std::list<NonMovable>(10));

  const auto range = data | Flatten();
  ASSERT_EQ(std::distance(range.begin(), range.end()), 15u);

  const auto& vector = Eval(range);
  ASSERT_EQ(vector.size(), 15u);
}
