#include <narray/span.hpp>

#include <userver/utest/utest.hpp>

namespace narray {

TEST(Span, Basic) {
  std::vector data{1, 2, 3, 4, 5};

  auto data_view = Span{data};

  EXPECT_EQ(2, data_view[1]);

  data_view[0] = 7;
  EXPECT_EQ(7, data_view[0]);
  EXPECT_EQ(7, data[0]);
}

#ifdef ARCADIA_ROOT
// In current taxi environ those tests run aground on
// bug in compiler.
// With clang and C++20 it works like a charm
TEST(Span, BasicConst) {
  std::vector data{1, 2, 3, 4, 5};

  auto data_view = Span<const int>{data.data(), data.size()};

  EXPECT_EQ(2, data_view[1]);

  EXPECT_EQ(1, data_view[0]);
  EXPECT_EQ(1, data[0]);
}

TEST(Span, BasicConstOperations) {
  std::vector data{1, 2, 3, 4, 5};

  using ConstIntSpan = Span<const int>;

  auto data_view = ConstIntSpan{data.data(), data.size()};

  ConstIntSpan t1;

  ConstIntSpan t2;
  t2 = data_view;

  t1 = t2;

  t2 = std::move(t1);
  t1 = data_view;

  EXPECT_TRUE(std::is_copy_assignable_v<ConstIntSpan>);
  EXPECT_TRUE(std::is_move_assignable_v<ConstIntSpan>);
  EXPECT_TRUE(std::is_nothrow_move_assignable_v<ConstIntSpan>);
  EXPECT_TRUE(std::is_nothrow_move_constructible_v<ConstIntSpan>);
}

TEST(Span, VectorOfConstSpans) {
  using MySpan = Span<const int>;
  std::vector<MySpan> test_vector;
  test_vector.reserve(10);
  test_vector.resize(5);
}

#endif

TEST(Span, BasicWithRange) {
  std::vector data{1, 2, 3, 4, 5};

  // let's start at index 1
  auto data_view = Span{data, 1};

  EXPECT_EQ(3, data_view[1]);

  data_view[0] = 7;
  EXPECT_EQ(7, data_view[0]);
  EXPECT_EQ(7, data[1]);
}

TEST(Span, Subspan) {
  std::vector data{1, 2, 3, 4, 5};

  // let's start at index 1
  auto data_view = Span{data};

  auto subspan_view = data_view.subspan(1);

  EXPECT_EQ(3, subspan_view[1]);

  subspan_view[0] = 7;
  EXPECT_EQ(7, subspan_view[0]);
  EXPECT_EQ(7, data[1]);
  EXPECT_EQ(4, subspan_view.size());

  auto subspan_view_2 = data_view.subspan(1, 2);  // should be 7, 3
  EXPECT_EQ(7, subspan_view_2[0]);
  EXPECT_EQ(3, subspan_view_2[1]);
  EXPECT_EQ(2, subspan_view_2.size());
}

TEST(Span, VectorOfSpans) {
  using MySpan = Span<int>;
  std::vector<MySpan> test_vector;
  test_vector.reserve(10);
  test_vector.resize(5);
}

}  // namespace narray
