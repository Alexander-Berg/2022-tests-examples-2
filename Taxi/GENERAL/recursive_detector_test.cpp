
#include <set>

#include <userver/utest/utest.hpp>

#include "recursive_detector.hpp"

namespace agl::util::test {

using Param = std::unordered_map<std::string, std::set<std::string>>;

static const Param kPositives[] = {
    {{"a", {"a"}}},
    {{"a", {"b"}}, {"b", {"a"}}},
    {{"a", {"b"}}, {"b", {"c"}}, {"c", {"a"}}},
    {{"a", {"b"}}, {"b", {"c"}}, {"c", {"b"}}},
    {{"a", {"d", "e", "c"}},
     {"c", {"b", "w"}},
     {"w", {"e", "d", "o"}},
     {"o", {"c"}}},
    {{"a", {"b", "c"}}, {"b", {"d"}}, {"c", {"d"}}, {"d", {"a"}}},
};

static const Param kNegatives[] = {
    {},
    {{"a", {}}},
    {{"a", {}}, {"b", {}}},
    {{"a", {"b"}}},
    {{"a", {"b", "c"}}},
    {{"a", {"b"}}, {"b", {"c", "d"}}},
    {{"a", {"b", "d"}}, {"b", {"c", "d"}}, {"c", {"d"}}},
};

class TestRecursivePositiveDetector : public ::testing::TestWithParam<Param> {};
TEST_P(TestRecursivePositiveDetector, Positives) {
  EXPECT_THROW(CheckRecursiveDependecies(GetParam()), std::runtime_error);
}
INSTANTIATE_TEST_SUITE_P(Positives, TestRecursivePositiveDetector,
                         ::testing::ValuesIn(kPositives));

class TestRecursiveNegativeDetector : public ::testing::TestWithParam<Param> {};
TEST_P(TestRecursiveNegativeDetector, Negatives) {
  EXPECT_NO_THROW(CheckRecursiveDependecies(GetParam()));
}
INSTANTIATE_TEST_SUITE_P(Negatives, TestRecursiveNegativeDetector,
                         ::testing::ValuesIn(kNegatives));

}  // namespace agl::util::test
