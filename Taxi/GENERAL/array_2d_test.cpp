#include <narray/array_2d.hpp>

#include <vector>

#include <userver/utest/utest.hpp>

namespace narray {

TEST(Array2D, Basic) {
  const std::vector data{1, 2, 3, 4, 5, 6};

  const auto arr1 = Array2D(std::vector<int>{data}, 3);

  ASSERT_EQ(3, arr1.ColumnCount());
  ASSERT_EQ(2, arr1.RowCount());
  EXPECT_EQ(5, arr1[1][1]);
  EXPECT_EQ(3, arr1[0][2]);

  auto arr2 = Array2D(std::vector<int>{data}, 2);

  EXPECT_EQ(4, arr2[1][1]);
  EXPECT_EQ(2, arr2[0][1]);

  // assign
  arr2[1][1] = 7;
  EXPECT_EQ(7, arr2[1][1]);
}

TEST(Array2D, Error) {
  const std::vector data{1, 2, 3, 4, 5, 6};

  EXPECT_ANY_THROW(Array2D(std::vector<int>{data}, 12));
  EXPECT_ANY_THROW(Array2D(std::vector<int>{data}, 5));
}

}  // namespace narray
