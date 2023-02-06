#include <userver/utest/utest.hpp>

#include <vector>

#include <views/driver.hpp>

namespace views::impl {

auto pred = [](const int& i) { return i == 5; };

TEST(TestEraseIfSingle, TestRemoved) {
  std::vector<int> vec = {1, 2, 3, 4, 5, 6, 7, 8};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{1, 2, 3, 4, 8, 6, 7}));

  vec = {1, 2, 3, 4, 5, 6};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{1, 2, 3, 4, 6}));

  vec = {1, 2, 3, 4, 5};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{1, 2, 3, 4}));

  vec = {5};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{}));

  vec = {5, 5};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{5}));

  vec = {1, 2, 3, 4, 5, 6, 5};
  EXPECT_EQ(std::count_if(std::begin(vec), std::end(vec), pred), 2);
  EraseIfSingle(vec, pred);
  EXPECT_EQ(std::count_if(std::begin(vec), std::end(vec), pred), 1);
}

TEST(TestEraseIfSingle, TestNotRemoved) {
  std::vector<int> vec = {1, 2, 3, 4, 6};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{1, 2, 3, 4, 6}));

  vec = {1};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{1}));

  vec = {};
  EraseIfSingle(vec, pred);
  EXPECT_EQ(vec, (std::vector<int>{}));
}

}  // namespace views::impl
