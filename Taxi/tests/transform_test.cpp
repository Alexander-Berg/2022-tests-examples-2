#include <gtest/gtest.h>

#include "common.hpp"

#include <helpers/transform.hpp>

using namespace helpers;

struct MergeContainerData {
  std::vector<int> data;
  std::vector<int> expected;
};

struct MergeContainerTestParametrized
    : public BaseTestWithParam<MergeContainerData> {};

TEST_P(MergeContainerTestParametrized, Test) {
  const auto& params = GetParam();
  auto data = params.data;
  ASSERT_EQ(MergeContainer(
                std::move(data),
                [](const int& lhs, const int& rhs) { return lhs == rhs; },
                [](int&, const int&) {}),
            params.expected);
}

INSTANTIATE_TEST_SUITE_P(MergeContainerTestParametrized,
                         MergeContainerTestParametrized,
                         ::testing::ValuesIn({
                             MergeContainerData{
                                 {1},
                                 {1},
                             },
                             MergeContainerData{
                                 {},
                                 {},
                             },
                             MergeContainerData{
                                 {1, 2, 3},
                                 {1, 2, 3},
                             },
                             MergeContainerData{
                                 {1, 2, 3, 3},
                                 {1, 2, 3},
                             },
                             MergeContainerData{
                                 {1, 2, 2, 3},
                                 {1, 2, 3},
                             },
                             MergeContainerData{
                                 {1, 1, 2, 3},
                                 {1, 2, 3},
                             },
                             MergeContainerData{
                                 {1, 1, 2, 2, 3, 3},
                                 {1, 2, 3},
                             },
                         }));
