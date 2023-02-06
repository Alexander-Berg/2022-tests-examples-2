#include <iostream>
#include <userver/utest/utest.hpp>

#include "reuse_from_sequence_algo.hpp"

namespace driver_route_watcher::internal::fsm {

using namespace std::string_literals;

// This is pretty much why algorithm was written as template. We can now
// test it using ordinary strings
struct TestData {
  using NormalizedResultElem =
      std::pair<std::string, std::optional<std::string>>;
  using NormalizedResult = std::vector<NormalizedResultElem>;
  std::vector<std::string> first;
  std::vector<std::string> second;

  NormalizedResult reference_result;
};

void PrintTo(const TestData& data, std::ostream* o) {
  if (o == nullptr) {
    return;
  }
  *o << "[";
  for (const auto& x : data.first) {
    *o << x << ",";
  }
  *o << "],[";
  for (const auto& x : data.second) {
    *o << x << ",";
  }
  *o << "]";
}

struct ReuseFromSequenceTestFixture : public testing::TestWithParam<TestData> {
  using NormalizedResult = TestData::NormalizedResult;
  using NormalizedResultElem = TestData::NormalizedResultElem;
  static bool FirstHasSuffix(const std::string& first,
                             const std::string& suffix) {
    return first.size() >= suffix.size() &&
           (first.compare(first.size() - suffix.size(), suffix.size(),
                          suffix) == 0);
  }

  // These are invariants that must always be true, no matter specific
  // realization we try

  // clang-format off
  inline static std::vector<TestData> kCardinalInvariants = {
      // find suffix
      {
        {"bc"s},
        {"abc"s},
        {{"bc"s, "abc"s}}
      },
      // find suffix somewhere
      {
        {"bc"s},
        {"xzy"s, "abc"s, "tuv"s},
        {{"bc"s, "abc"s}}
      },
      // error in suffix 1
      {
        {"bc"s},
        {"xzy"s, "abce"s, "tuv"s},
        // "bc" is not a suffix of "abce"
        {{"bc"s, std::nullopt}}
      },
      // only second element can use suffix-search
      {
        {"bc"s, "uv"s},
        {"xyz"s, "abc"s, "tuv"s},
        // "bc" is not a suffix of "abce"
        {{"bc"s, "abc"s}, {"uv"s, std::nullopt}}
      },
      // no possible reuse
      {
        {"xyz"s},
        {"abc"s},
        {{"xyz"s, std::nullopt}}
      },
      // first empty
      {
        {},
        {"abc"s}, {}
      },
      // second empty
      {
        {"abc"s, "xyz"s},
        {},
        {{"abc"s, std::nullopt}, {"xyz"s, std::nullopt}}
      },
      // both empty
      {{}, {}, {}},
  };
  // clang-format on

  // This test cases are not required for our purpose - reuse data from second
  // sequence. Theese are implementation-defined. If we change implemenation,
  // then we may require to change these as well
  inline static std::vector<TestData> kImplementationDefinedInvariants = {
      // reverse-order - can't find [1] element
      {{"bc"s, "uv"s}, {"uv"s, "bc"s}, {{"bc"s, "bc"s}, {"uv"s, std::nullopt}}},
  };
};

TEST_P(ReuseFromSequenceTestFixture, CheckAlgorithm) {
  const auto& testData = GetParam();

  const auto& first = testData.first;
  const auto& second = testData.second;

  auto result = ReuseFromSequence(
      first.begin(), first.end(), second.begin(), second.end(),
      // equality
      [](const std::string& first, const std::string& second) {
        return first == second;
      },
      // suffix
      [](const std::string& first, const std::string& second) {
        return FirstHasSuffix(first, second);
      });

  NormalizedResult normalized_result;
  for (const auto& elem : result) {
    ASSERT_NE(first.end(), elem.first_elem_it);
    NormalizedResultElem normalized_elem;
    normalized_elem.first = *(elem.first_elem_it);
    if (elem.second_elem_it != second.end()) {
      normalized_elem.second = *(elem.second_elem_it);
    }
    normalized_result.emplace_back(std::move(normalized_elem));
  }

  const NormalizedResult& reference_result = testData.reference_result;
  // Now, compare normalized_result and reference_result
  ASSERT_EQ(reference_result.size(), normalized_result.size());

  for (size_t i = 0; i < reference_result.size(); ++i) {
    EXPECT_EQ(reference_result[i], normalized_result[i])
        << "failure when comparing at index" << i;
  }
}

INSTANTIATE_TEST_SUITE_P(
    CardinalInvariants, ReuseFromSequenceTestFixture,
    testing::ValuesIn(ReuseFromSequenceTestFixture::kCardinalInvariants));
INSTANTIATE_TEST_SUITE_P(
    ImplementationDefinedInvariants, ReuseFromSequenceTestFixture,
    testing::ValuesIn(
        ReuseFromSequenceTestFixture::kImplementationDefinedInvariants));

}  // namespace driver_route_watcher::internal::fsm
