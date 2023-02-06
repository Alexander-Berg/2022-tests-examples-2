#include <helpers/convert_feedback.hpp>
#include <userver/utest/utest.hpp>

namespace eats_restapp_communications::types::feedback {
inline bool operator==(const Saving& lhs, const Saving& rhs) {
  return std::tie(lhs.partner_id, lhs.slug, lhs.score, lhs.comment) ==
         std::tie(rhs.partner_id, rhs.slug, rhs.score, rhs.comment);
}
}  // namespace eats_restapp_communications::types::feedback

namespace eats_restapp_communications::helpers {

using types::feedback::FreshConditions;
using types::feedback::Saving;
using types::feedback::Settings;
using types::feedback::Slug;
using types::feedback::Stored;
using types::feedback::StoredOpt;
using PartnerId = types::partner::Id;
using storages::postgres::TimePointTz;

static constexpr int64_t kPartnerId = 42;

Settings MakeSettings() {
  static const Settings settings{{"dashboard", "orders"}, {1, 5}, 6};
  return settings;
}

TEST(MakeSlugTest, should_throw_on_unknown_slug) {
  ASSERT_THROW(MakeSlug("abacaba", MakeSettings()),
               types::feedback::UnknownSlug);
}

using MakeSavingParams = std::pair<::handlers::FeedbackRequest, Saving>;

struct MakeSavingTest : public ::testing::TestWithParam<MakeSavingParams> {};

const std::vector<MakeSavingParams> kMakeSavingData{
    {{"dashboard", 2, std::nullopt},
     {PartnerId(kPartnerId), Slug("dashboard"), 2, std::nullopt}},
    {{"dashboard", 3, "1234"},
     {PartnerId(kPartnerId), Slug("dashboard"), 3, "1234"}},
    {{"dashboard", 4, "12345678"},
     {PartnerId(kPartnerId), Slug("dashboard"), 4, "123456"}},
};

INSTANTIATE_TEST_SUITE_P(MakeSavingParams, MakeSavingTest,
                         ::testing::ValuesIn(kMakeSavingData));

TEST_P(MakeSavingTest, should_return_saving_with_limited_comment) {
  auto [input, expected] = GetParam();
  const auto result =
      MakeSaving(PartnerId(kPartnerId), std::move(input), MakeSettings());
  ASSERT_EQ(result, expected);
}

struct MakeSavingErrorsTest
    : public ::testing::TestWithParam<MakeSavingParams> {};

const std::vector<MakeSavingParams> kMakeSavingErrorsData{
    {{"dashboard", 0, std::nullopt}, {}},
    {{"dashboard", 6, std::nullopt}, {}},
};

INSTANTIATE_TEST_SUITE_P(MakeSavingParams, MakeSavingErrorsTest,
                         ::testing::ValuesIn(kMakeSavingErrorsData));

TEST_P(MakeSavingErrorsTest, should_throw_on_score_over_limit) {
  auto [input, _] = GetParam();
  ASSERT_THROW(
      MakeSaving(PartnerId(kPartnerId), std::move(input), MakeSettings()),
      types::feedback::ScoreOverLimit);
}

using MakeResponseParams =
    std::tuple<StoredOpt, FreshConditions, ::handlers::FeedbackResponse>;

struct MakeResponseTest : public ::testing::TestWithParam<MakeResponseParams> {
};

decltype(auto) GetTimeFromString(const std::string& time_str) {
  return ::utils::datetime::Stringtime(
      time_str, ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
}

const std::vector<MakeResponseParams> kMakeResponseData{
    {std::nullopt,
     FreshConditions{},
     {false, std::nullopt, std::nullopt, std::nullopt}},
    {std::nullopt,
     FreshConditions{GetTimeFromString("2022-01-01")},
     {false, std::nullopt, std::nullopt, std::nullopt}},
    {Stored{2, std::nullopt, TimePointTz{GetTimeFromString("2022-02-01")}},
     FreshConditions{},
     {true, GetTimeFromString("2022-02-01"), 2, std::nullopt}},
    {Stored{4, "comment", TimePointTz{GetTimeFromString("2022-02-01")}},
     FreshConditions{},
     {true, GetTimeFromString("2022-02-01"), 4, "comment"}},
    {Stored{3, "comment", TimePointTz{GetTimeFromString("2022-02-01")}},
     FreshConditions{GetTimeFromString("2022-01-01")},
     {true, GetTimeFromString("2022-02-01"), 3, "comment"}},
    {Stored{5, "comment", TimePointTz{GetTimeFromString("2022-02-01")}},
     FreshConditions{GetTimeFromString("2022-03-01")},
     {false, GetTimeFromString("2022-02-01"), 5, "comment"}},
};

INSTANTIATE_TEST_SUITE_P(MakeResponseParams, MakeResponseTest,
                         ::testing::ValuesIn(kMakeResponseData));

TEST_P(MakeResponseTest, should_return_response_with_is_fresh_flag) {
  auto [input, conditions, expected] = GetParam();
  const auto result = MakeResponse(std::move(input), conditions);
  ASSERT_EQ(result, expected);
}

}  // namespace eats_restapp_communications::helpers
