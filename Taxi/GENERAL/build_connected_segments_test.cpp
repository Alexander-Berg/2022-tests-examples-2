#include <iostream>
#include <userver/utest/utest.hpp>

#include "build_connected_segments.hpp"

namespace driver_route_watcher::internal {

using namespace std::string_literals;

namespace {

struct TestPoint {
  // Letters are 'connected'
  // Numbers are 'not connected'
  std::string state{"c"};

  bool IsConnected() const { return !(state[0] >= '0' && state[0] <= '9'); }
};

struct TestConnectedSegment {
  std::string elems;

  TestConnectedSegment(const TestPoint* first, const TestPoint* end) {
    while (first != end) {
      elems.push_back(first->state[0]);
      first++;
    }
  }
};

// This is pretty much why algorithm was written as template. We can now
// test it using ordinary strings
struct TestData {
  using NormalizedResultElem = std::string;
  using NormalizedResult = std::vector<NormalizedResultElem>;
  std::string points;
  NormalizedResult reference_result;
};

void PrintTo(const TestData& data, std::ostream* o) {
  if (o == nullptr) {
    return;
  }
  *o << "[" << data.points << "]";
}

}  // namespace

struct BuildConnectedSegmentsTestFixture
    : public testing::TestWithParam<TestData> {
  using NormalizedResult = TestData::NormalizedResult;
  using NormalizedResultElem = TestData::NormalizedResultElem;

  // These are invariants that must always be true, no matter specific
  // realization we try

  // clang-format off
  inline static std::vector<TestData> kCardinalInvariants = {{
    // letters are 'connected'
    // numbers are 'not connected'

    // one element
    TestData{
      { "a"s },
      { "a"s, }
    },
    {
      { "1"s },
      { "1"s }
    },

    // two elements
    {
      { "aa"s },
      { "aa"s }
    },
    {
      { "01"s },
      { "0"s, "01"s }
    },
    {
      { "a0"s },
      { "a"s, "a0"s }
    },
    {
      { "0a"s },
      { "0a"s }
    },
    // some other cases
    {
      { "0aaa1aaaa23"s },
      { "0aaa"s, "a1aaaa"s, "a2"s, "23"s }
    },
    {
      { "01aa23aaaa45"s },
      { "0"s, "01aa"s, "a2"s, "23aaaa"s, "a4"s, "45"s }
    },
    {
      { "01aa23aaaa"s },
      { "0"s, "01aa"s, "a2"s, "23aaaa"s}
    },
    {
      { "aa23aaaa"s },
      {  "aa"s, "a2"s, "23aaaa"s }
    },
    {
      { "abcde"s },
      { "abcde"s }
    },
    {
      { "012a3"s },
      { "0"s, "01"s, "12a"s, "a3"s }
    },
    {
      { "0ab12"s },
      { "0ab"s, "b1"s, "12"s}
    },
    // corner cases
    { {}, {} }

  }};
  // clang-format on

  // This test cases are not required for our purpose - reuse data from second
  // sequence. Theese are implementation-defined. If we change implemenation,
  // then we may require to change these as well
  inline static std::vector<TestData> kImplementationDefinedInvariants = {};
};

TEST_F(BuildConnectedSegmentsTestFixture, TestTestItself) {
  TestPoint x;
  x.state = "a";
  EXPECT_TRUE(x.IsConnected());

  x.state = "0";
  EXPECT_FALSE(x.IsConnected());
}

TEST_P(BuildConnectedSegmentsTestFixture, CheckAlgorithm) {
  const auto& testData = GetParam();

  std::vector<TestPoint> points;
  points.reserve(testData.points.size());
  for (const auto& x : testData.points) {
    std::string as_string;
    as_string.push_back(x);
    points.emplace_back(TestPoint{as_string});
  }

  std::vector<TestConnectedSegment> result;

  BuildConnectedSegments(points.begin(), points.end(), result);

  NormalizedResult normalized_result;
  normalized_result.reserve(result.size());
  for (const auto& x : result) {
    normalized_result.push_back(x.elems);
  }

  const NormalizedResult& reference_result = testData.reference_result;
  EXPECT_EQ(reference_result, normalized_result);
}

INSTANTIATE_TEST_SUITE_P(
    CardinalInvariants, BuildConnectedSegmentsTestFixture,
    testing::ValuesIn(BuildConnectedSegmentsTestFixture::kCardinalInvariants));
INSTANTIATE_TEST_SUITE_P(
    ImplementationDefinedInvariants, BuildConnectedSegmentsTestFixture,
    testing::ValuesIn(
        BuildConnectedSegmentsTestFixture::kImplementationDefinedInvariants));

}  // namespace driver_route_watcher::internal
