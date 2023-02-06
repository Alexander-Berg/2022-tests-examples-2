#include <userver/utest/utest.hpp>

#include <userver/utest/parameter_names.hpp>

#include <utils/algorithm.hpp>

namespace order_offers::utils::algo {

struct StringSetTestParams {
  std::unordered_set<std::string> a;
  std::unordered_set<std::string> b;

  std::unordered_set<std::string> intersection;

  std::string test_name;
};

class StringSetTest : public testing::TestWithParam<StringSetTestParams> {};

const std::vector<StringSetTestParams> kStringSetTestValues = {
    {
        {},
        {},
        {},
        "EmptySets",
    },
    {
        {"a"},
        {},
        {},
        "OneEmptySet",
    },
    {
        {"a", "b"},
        {"c"},
        {},
        "NonEmptySets",
    },
    {
        {"a"},
        {"a"},
        {"a"},
        "EqualSingleItemSets",
    },
    {
        {"a", "b"},
        {"b", "a"},
        {"a", "b"},
        "EqualSets",
    },
    {
        {"a", "b", "c"},
        {"c", "b"},
        {"c", "b"},
        "NestedSets",
    },
    {
        {"a", "b", "c"},
        {"c", "d", "e"},
        {"c"},
        "HaveSingleCommonElement",
    },
    {
        {"a", "b", "c"},
        {"b", "c", "d"},
        {"b", "c"},
        "HaveMultipleCommonElements",
    },
};

TEST_P(StringSetTest, Basic) {
  const auto& params = GetParam();

  EXPECT_EQ(SetsIntersection(params.a, params.b), params.intersection);
  EXPECT_EQ(SetsIntersection(params.b, params.a), params.intersection);
}

INSTANTIATE_TEST_SUITE_P(UtilsAlgo, StringSetTest,
                         testing::ValuesIn(kStringSetTestValues),
                         ::utest::PrintTestName());

}  // namespace order_offers::utils::algo
