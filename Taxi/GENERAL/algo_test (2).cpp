#include <eats-adverts-places/utils/algo.hpp>

#include <gtest/gtest.h>

#include <eats-adverts-places/utils/test.hpp>

namespace eats_adverts_places::utils::algo {

namespace {

struct AlgoFindYandexuidTestCase {
  std::string name{};
  std::string cookie_in_request{};
  std::optional<std::string> expected{};
};

class AlgoFindYandexuidTest
    : public ::testing::TestWithParam<AlgoFindYandexuidTestCase> {};

struct RotateTestCase {
  std::string name{};
  std::vector<int> source{};
  size_t old_idx{};
  size_t new_idx{};
  std::vector<int> expected{};
};

class RotateTest : public ::testing::TestWithParam<RotateTestCase> {};

std::vector<RotateTestCase> MakeRotateTestCases() {
  return {
      {
          "empty source",  // name
          {},              // source
          0,               // old_idx
          0,               // new_idx
          {},              // expected
      },
      {
          "left rotate",    // name
          {1, 2, 3, 4, 5},  // source
          4,                // old_idx
          0,                // new_idx
          {5, 1, 2, 3, 4},  // expected
      },
      {
          "right rotate",   // name
          {1, 2, 3, 4, 5},  // source
          0,                // old_idx
          4,                // new_idx
          {2, 3, 4, 5, 1},  // expected
      },
      {
          "self swap",      // name
          {1, 2, 3, 4, 5},  // source
          0,                // old_idx
          0,                // new_idx
          {1, 2, 3, 4, 5},  // expected
      },
      {
          "swap left rotate",  // name
          {1, 2, 3, 4, 5},     // source
          0,                   // old_idx
          1,                   // new_idx
          {2, 1, 3, 4, 5},     // expected
      },
      {
          "swap right rotate",  // name
          {1, 2, 3, 4, 5},      // source
          1,                    // old_idx
          0,                    // new_idx
          {2, 1, 3, 4, 5},      // expected
      },
      {
          "self swap out of range",  // name
          {1, 2, 3, 4, 5},           // source
          10,                        // old_idx
          10,                        // new_idx
          {1, 2, 3, 4, 5},           // expected
      },
      {
          "out of range left rotate",  // name
          {1, 2, 3, 4, 5},             // source
          10,                          // old_idx
          0,                           // new_idx
          {1, 2, 3, 4, 5},             // expected
      },
      {
          "out of range right rotate",  // name
          {1, 2, 3, 4, 5},              // source
          0,                            // old_idx
          10,                           // new_idx
          {1, 2, 3, 4, 5},              // expected
      },
  };
}

}  // namespace

TEST_P(AlgoFindYandexuidTest, GetPlaces) {
  auto param = GetParam();

  const auto actual = FindYandexUid(std::move(param.cookie_in_request));

  ASSERT_EQ(param.expected, actual) << param.name;
}

std::vector<AlgoFindYandexuidTestCase> MakeAlgoTestFindYandexuidCases();

INSTANTIATE_TEST_SUITE_P(AlgoFindYandexUId, AlgoFindYandexuidTest,
                         ::testing::ValuesIn(MakeAlgoTestFindYandexuidCases()),
                         [](const auto& test_case) {
                           return utils::test::GetName(test_case.param);
                         });

std::vector<AlgoFindYandexuidTestCase> MakeAlgoTestFindYandexuidCases() {
  return {
      {
          "only yandexuid",  // name
          "yandexuid=42",    // cookie_in_request
          "42"               // expected
      },
      {
          "yandexuid in string",  // name
          "userid=1; time=13:13; "
          "yandexuid=1917; latitude=90",  // cookie_in_request
          "1917"                          // expected
      },
      {
          "yandexuid in the end",  // name
          "yandex=12; time=13:13; "
          "yandexuid=1380",  // cookie_in_request
          "1380"             // expected
      },
      {
          "no yandexuid",  // name
          "userid=5",      // cookie_in_request
          std::nullopt     // expected
      },
      {
          "empty string",  // name
          "",              // cookie_in_request
          std::nullopt     // expected
      },
      {
          "empty yandexuid in the end of string",  // name
          "exp=2.7; yandexuid=",                   // cookie_in_request
          std::nullopt                             // expected
      },
      {
          "empty yandexuid",                 // name
          "exp=2.7; yandexuid=; pi=3.1415",  // cookie_in_request
          std::nullopt                       // expected
      },
      {
          "smth like fuzzing",  // name
          "yand$@$@$;;;;;;;"
          "04204pjrjgjgepaj421oj",  // cookie_in_request
          std::nullopt              // expected
      },
  };
}

TEST_P(RotateTest, Test) {
  const auto test_param = GetParam();
  auto actual = test_param.source;

  Rotate(actual, test_param.old_idx, test_param.new_idx);
  ASSERT_EQ(test_param.expected, actual);
}

INSTANTIATE_TEST_SUITE_P(Rotate, RotateTest,
                         ::testing::ValuesIn(MakeRotateTestCases()),
                         [](const auto& test_case) {
                           return utils::test::GetName(test_case.param);
                         });

}  // namespace eats_adverts_places::utils::algo
