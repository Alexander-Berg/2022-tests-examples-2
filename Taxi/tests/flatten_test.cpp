#include <gtest/gtest.h>

#include <numeric>

#include <boost/range/adaptor/map.hpp>
#include <boost/range/adaptor/transformed.hpp>
#include <boost/range/iterator_range.hpp>

#include <fmt/format.h>

#include <flatten-range/flatten.hpp>

namespace {

boost::iterator_range<std::vector<int>::const_iterator> ToRange(
    const std::vector<int>& vals) {
  return boost::make_iterator_range(vals);
}

}  // namespace

TEST(TestFlatten, SingleRange) {
  std::vector<int> vals{0, 1, 2, 3, 4};
  std::vector<boost::iterator_range<std::vector<int>::iterator>> ranges{
      boost::make_iterator_range(vals)};

  auto concat_range = ranges | flatten_range::Flatten();
  std::vector<int> concat_vals(concat_range.begin(), concat_range.end());

  EXPECT_EQ(concat_vals, vals);
}

TEST(TestFlatten, OverlappedRanges) {
  const int kSize = 10;
  const int kRangeLen = 5;

  std::vector<int> vals(kSize);
  std::vector<int> correct_order_vals;
  std::vector<boost::iterator_range<std::vector<int>::iterator>> ranges;

  std::iota(vals.begin(), vals.end(), 0);
  correct_order_vals.reserve(kSize * kRangeLen);
  ranges.reserve(kSize);
  for (int i = 0; i + kRangeLen <= kSize; ++i) {
    auto range = boost::make_iterator_range_n(vals.begin() + i, kRangeLen);
    correct_order_vals.insert(correct_order_vals.end(), range.begin(),
                              range.end());
    ranges.push_back(std::move(range));
  }

  auto concat_range = ranges | flatten_range::Flatten();
  std::vector<int> concat_vals(concat_range.begin(), concat_range.end());

  EXPECT_EQ(concat_vals, correct_order_vals);
}

TEST(TestFlatten, TableOrder) {
  const int kSize = 10;

  std::vector<std::vector<std::string>> vals(kSize);
  std::vector<std::string> correct_order_vals;

  correct_order_vals.reserve(kSize * kSize);
  for (int row = 0; row < kSize; ++row) {
    auto& row_vals = vals[row];
    row_vals.reserve(kSize);
    for (int col = 0; col < kSize; ++col) {
      auto val = fmt::format("[{}][{}]", row, col);
      row_vals.push_back(val);
      correct_order_vals.push_back(std::move(val));
    }
  }

  auto concat_range = vals  //
                      | boost::adaptors::transformed([](const auto& row_vals) {
                          return boost::make_iterator_range(row_vals);
                        })  //
                      | flatten_range::Flatten();
  std::vector<std::string> concat_vals(concat_range.begin(),
                                       concat_range.end());

  EXPECT_EQ(concat_vals, correct_order_vals);
}

TEST(TestFlatten, BoxOrder) {
  const int kSize = 10;

  std::vector<std::vector<std::vector<int>>> vals(kSize);
  std::vector<int> correct_order_vals;

  correct_order_vals.reserve(kSize * kSize * kSize);
  for (int i = 0; i < kSize; ++i) {
    auto& table_vals = vals[i];
    table_vals.resize(kSize);
    for (int j = 0; j < kSize; ++j) {
      auto& row_vals = table_vals[j];
      row_vals.reserve(kSize);
      for (int k = 0; k < kSize; ++k) {
        int val = i + j + k;
        row_vals.push_back(val);
        correct_order_vals.push_back(val);
      }
    }
  }

  auto concat_range = vals  //
                      | boost::adaptors::transformed([](const auto& layer) {
                          return layer                                    //
                                 | boost::adaptors::transformed(ToRange)  //
                                 | flatten_range::Flatten();
                        })  //
                      | flatten_range::Flatten();
  std::vector<int> concat_vals(concat_range.begin(), concat_range.end());

  EXPECT_EQ(concat_vals, correct_order_vals);
}

TEST(TestFlatten, MapOfMapValues) {
  const int kSize = 10;

  std::map<int, std::map<int, std::string>> vals;
  std::vector<std::string> correct_order_vals;

  correct_order_vals.reserve(kSize * kSize);
  for (int i = 0; i < kSize; ++i) {
    for (int j = 0; j < kSize; ++j) {
      auto val = fmt::format("{} -> {}", i, j);
      vals[i][j] = val;
      correct_order_vals.push_back(std::move(val));
    }
  }

  auto concat_range = vals  //
                      | boost::adaptors::transformed([](const auto& layer) {
                          return layer.second | boost::adaptors::map_values;
                        })  //
                      | flatten_range::Flatten();
  std::vector<std::string> concat_vals(concat_range.begin(),
                                       concat_range.end());

  EXPECT_EQ(concat_vals, correct_order_vals);
}
