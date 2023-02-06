#include "utils/passport.hpp"

#include <gtest/gtest.h>
namespace {
namespace utils = eats_restapp_marketing::utils;
using PassportId = eats_restapp_marketing::models::PassportIdString;

struct PassportGenerateAvatarLinkSuccessTest
    : ::testing::TestWithParam<
          std::tuple<std::string, std::string, std::string>> {};

struct PassportGenerateAvatarLinkExceptionTest
    : ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

struct ConvertPassportIdsSuccessTest
    : ::testing::TestWithParam<
          std::tuple<std::vector<PassportId>, std::vector<int64_t>>> {};

struct ConvertPassportIdsToIntSuccessTest
    : ::testing::TestWithParam<
          std::tuple<std::vector<int64_t>, std::vector<PassportId>>> {};

INSTANTIATE_TEST_SUITE_P(
    results, PassportGenerateAvatarLinkSuccessTest,
    ::testing::Values(
        std::make_tuple("{avatar_id}", "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1",
                        "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1"),
        std::make_tuple("link{avatar_id}", "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1",
                        "link40841/osIZVAEahAC2kAeCBPh5lgIhTs-1"),
        std::make_tuple(
            "https://avatars.mds.yandex.net/get-yapic/{avatar_id}/40x40",
            "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1",
            "https://avatars.mds.yandex.net/get-yapic/40841/"
            "osIZVAEahAC2kAeCBPh5lgIhTs-1/40x40"),
        std::make_tuple("", "osIZVAEahAC2kAeCBPh5lgIhTs-1/40x40", ""),
        std::make_tuple("avatar_id", "osIZVAEahAC2kAeCBPh5lgIhTs-1/40x40",
                        "avatar_id")));

INSTANTIATE_TEST_SUITE_P(
    results, PassportGenerateAvatarLinkExceptionTest,
    ::testing::Values(
        std::make_tuple("avatar_id}", "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1"),
        std::make_tuple("{avatar_id", "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1"),
        std::make_tuple("{avatar}", "40841/osIZVAEahAC2kAeCBPh5lgIhTs-1")));

TEST_P(PassportGenerateAvatarLinkSuccessTest, shouldReturnExpectedString) {
  const auto [tmpl, avatar_id, expected] = GetParam();
  ASSERT_EQ(utils::passport::GenerateAvatarLink(tmpl, avatar_id), expected);
}

TEST_P(PassportGenerateAvatarLinkExceptionTest, shouldCallThrow) {
  const auto [tmpl, avatar_id] = GetParam();
  ASSERT_THROW(utils::passport::GenerateAvatarLink(tmpl, avatar_id),
               utils::passport::GenerateAvatarLinkError);
}

INSTANTIATE_TEST_SUITE_P(
    results, ConvertPassportIdsSuccessTest,
    ::testing::Values(
        std::make_tuple(std::vector<PassportId>{}, std::vector<int64_t>{}),
        std::make_tuple(std::vector<PassportId>{PassportId{"123"}},
                        std::vector<int64_t>{123}),
        std::make_tuple(std::vector<PassportId>{PassportId{"q123"}},
                        std::vector<int64_t>{}),
        std::make_tuple(std::vector<PassportId>{PassportId{"123"},
                                                PassportId{"234"}},
                        std::vector<int64_t>{123, 234}),
        std::make_tuple(std::vector<PassportId>{PassportId{"w123"},
                                                PassportId{"234"}},
                        std::vector<int64_t>{234})));

TEST_P(ConvertPassportIdsSuccessTest, shouldWork) {
  const auto [passport_ids, ints] = GetParam();
  ASSERT_EQ(utils::passport::ConvertPassportIds(passport_ids), ints);
}

INSTANTIATE_TEST_SUITE_P(
    results, ConvertPassportIdsToIntSuccessTest,
    ::testing::Values(
        std::make_tuple(std::vector<int64_t>{}, std::vector<PassportId>{}),
        std::make_tuple(std::vector<int64_t>{123},
                        std::vector<PassportId>{PassportId{"123"}}),
        std::make_tuple(std::vector<int64_t>{123, 4343},
                        std::vector<PassportId>{PassportId{"123"},
                                                PassportId{"4343"}})));

TEST_P(ConvertPassportIdsToIntSuccessTest, shouldWork) {
  const auto [ints, passport_ids] = GetParam();
  ASSERT_EQ(utils::passport::ConvertPassportIds(ints), passport_ids);
}

}  // namespace
