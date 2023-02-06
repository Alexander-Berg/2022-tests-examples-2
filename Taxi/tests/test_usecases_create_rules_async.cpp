#include <gmock/gmock.h>

#include <chrono>
#include <string_view>
#include <utility>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/datetime.hpp>

#include "smart_rules/draft/actions.hpp"
#include "smart_rules/draft/repository.hpp"
#include "smart_rules/usecases/create_rules_async.hpp"

#include "stub_drafts.hpp"

namespace {

namespace draft = billing_subventions_x::smart_rules::draft;
namespace usecase =
    billing_subventions_x::smart_rules::usecases::create_rules_async;

constexpr auto kInternalDraftId = "some_draft_id";
constexpr auto kAuthor = "me";
constexpr auto kDefaultStartsAt = "2021-05-01T00:00:00+0300";
constexpr auto kMaxErrorRate = 5;
static auto kMockNow = utils::datetime::Stringtime("2021-04-30T19:00:00+0300");
static auto kTooLate = utils::datetime::Stringtime("2021-04-30T22:30:00+0300");
static auto kRulesStartThreshold = std::chrono::hours{2};

class GenerateStrategy final : public draft::actions::GenerateStrategy {
 public:
  MOCK_METHOD(void, GenerateRules, (const draft::Draft&), (final));
};

class Output final : public usecase::Output {
 public:
  usecase::Response response;
  void SetResponse(usecase::Response&& r) final { response = std::move(r); }
};

formats::json::Value MakeSpec() {
  formats::json::ValueBuilder spec;
  spec["currency"] = "RUB";
  spec["start"] = kDefaultStartsAt;
  formats::json::ValueBuilder budget;
  budget["weekly"] = "10.0000";
  spec["budget"] = budget.ExtractValue();
  return spec.ExtractValue();
}

class PersonalGoalBulkCreateUseCase : public testing::Test {
  void SetUp() override {
    std::vector<std::string> old_rules;
    request_ = usecase::Request{
        kInternalDraftId, MakeSpec(),           kAuthor,      old_rules,
        kMockNow,         kRulesStartThreshold, kMaxErrorRate};
  }

 protected:
  void ExecuteWith(StubDraftRepository* repo) {
    repo->WithStartsAt(kDefaultStartsAt);
    auto actions = draft::actions::Actions{repo};
    actions.SetGenerateStrategyTo(&generator_);
    auto drafts_ = draft::repository::Drafts{repo, &actions};
    usecase::UseCase(&drafts_, &output_).Execute(std::move(request_));
  }

  usecase::Request request_;
  GenerateStrategy generator_{};
  Output output_{};
};

TEST_F(PersonalGoalBulkCreateUseCase, CreatesDraftSpecForNewDraft) {
  auto repo = NewDraftRepository();
  EXPECT_CALL(
      repo, CreateDraftSpec(std::string_view{request_.internal_draft_id},
                            *request_.spec, std::string_view{request_.author}))
      .Times(1);
  EXPECT_CALL(generator_, GenerateRules(testing::_)).Times(1);
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.is_generated, testing::IsFalse());
}

TEST_F(PersonalGoalBulkCreateUseCase, ResultsInvalidWhenNewDraftIsTooLate) {
  request_.now = kTooLate;
  constexpr auto error =
      "Rules' start '2021-04-30T21:00:00+0000' must be "
      "greater than '2021-04-30T19:30:00+0000' + 2 hours";
  auto repo = NewDraftRepository();
  EXPECT_CALL(repo, UpdateState(std::string_view{request_.internal_draft_id},
                                "INVALID", std::string_view{error}));
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.invalid_reason, testing::Eq(error));
}

TEST_F(PersonalGoalBulkCreateUseCase, ResultsProcessingIfNotCompletedYet) {
  auto repo = GeneratingDraftRepository();
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.invalid_reason, testing::Eq(""));
  ASSERT_THAT(output_.response.is_generated, testing::IsFalse());
}

TEST_F(PersonalGoalBulkCreateUseCase, FillsStatsWhenCompleted) {
  auto repo = GeneratedDraftRepository();
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.internal_draft_id,
              testing::Eq(request_.internal_draft_id));
  ASSERT_THAT(output_.response.is_generated, testing::IsTrue());
  ASSERT_THAT(output_.response.spec, testing::Eq(request_.spec));
  ASSERT_THAT(output_.response.rule_count_per_geonode["geonode"],
              testing::Eq(10));
  ASSERT_THAT(output_.response.total_specs_count, 1000);
  ASSERT_THAT(output_.response.failed_specs_count, 50);
  ASSERT_THAT(output_.response.clashing_draft_ids, testing::IsEmpty());
  ASSERT_THAT(output_.response.errors,
              testing::ElementsAre("Error 1", "Error 2"));
}

TEST_F(PersonalGoalBulkCreateUseCase, ResultInvalidWhenClashingSpecsInDraft) {
  auto repo = DraftWithSelfClashingSpecsRepository();
  constexpr auto error = "Draft has clashing specs";
  EXPECT_CALL(repo, UpdateState(std::string_view{request_.internal_draft_id},
                                "INVALID", std::string_view{error}));
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.invalid_reason, testing::Eq(error));
}

TEST_F(PersonalGoalBulkCreateUseCase, ResultInvalidWhenErrorRateTooHigh) {
  auto repo = GeneratedWithManyErrorsDraftRepository();
  constexpr auto error = "Broken specs rate too high: 5.10%. Must be <= 5%";
  EXPECT_CALL(repo, UpdateState(std::string_view{request_.internal_draft_id},
                                "INVALID", std::string_view{error}));
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.invalid_reason, testing::Eq(error));
}

TEST_F(PersonalGoalBulkCreateUseCase, ResultInvalidWhenSpecIsNotAvailable) {
  auto repo = FailedGeneratingDraftRepository();
  constexpr auto error = "Spec is unavailable for whatever reason";
  EXPECT_CALL(repo, UpdateState(std::string_view{request_.internal_draft_id},
                                "INVALID", std::string_view{error}));
  ExecuteWith(&repo);
  ASSERT_THAT(output_.response.invalid_reason, testing::Eq(error));
}

}  // namespace
