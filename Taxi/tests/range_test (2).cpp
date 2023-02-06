
#include <fmt/format.h>

#include <userver/utest/utest.hpp>
#include <utils/utils.hpp>

struct RangeTestData {
  std::vector<int> points;
  std::vector<std::pair<int, int>> ranges;
};

class RangeTest : public testing::Test,
                  public testing::WithParamInterface<RangeTestData> {};

TEST_P(RangeTest, Test) {
  const auto& param = GetParam();

  ASSERT_EQ(utils::GetRanges(param.points), param.ranges);
}

INSTANTIATE_TEST_SUITE_P(RangeTestBase, RangeTest,
                         testing::Values(                                 //
                             RangeTestData{{1, 2}, {{1, 2}}},             //
                             RangeTestData{{1, 2, 3}, {{1, 3}}},          //
                             RangeTestData{{1, 3, 4}, {{1, 1}, {3, 4}}},  //
                             RangeTestData{{1, 2, 4}, {{1, 2}, {4, 4}}},  //
                             RangeTestData{{1, 3}, {{1, 1}, {3, 3}}}      //
                             ));

struct RangeLocalizeData {
  std::vector<int> points;
  std::string ranges;
};

class FormatRangesTest : public testing::Test,
                         public testing::WithParamInterface<RangeLocalizeData> {
};

TEST_P(FormatRangesTest, TestLocalization) {
  const auto& param = GetParam();

  ASSERT_EQ(utils::FormatRanges(
                utils::GetRanges(param.points),
                [](const auto& value) { return std::to_string(value); },
                [](const auto& lhs, const auto& rhs) {
                  return fmt::format("{} - {}", std::to_string(lhs),
                                     std::to_string(rhs));
                }),
            param.ranges);
}

INSTANTIATE_TEST_SUITE_P(FormatRangesTestBase, FormatRangesTest,
                         testing::Values(                               //
                             RangeLocalizeData{{1, 2}, "1 - 2"},        //
                             RangeLocalizeData{{1, 2, 3}, "1 - 3"},     //
                             RangeLocalizeData{{1, 3, 4}, "1, 3 - 4"},  //
                             RangeLocalizeData{{1, 2, 4}, "1 - 2, 4"},  //
                             RangeLocalizeData{{1, 3}, "1, 3"}          //
                             ));
