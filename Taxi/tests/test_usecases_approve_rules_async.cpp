#include <string>
#include <string_view>
#include <utility>

#include <gmock/gmock.h>

#include <userver/utils/datetime.hpp>

#include "smart_rules/draft/draft.hpp"
#include "smart_rules/types/base_types.hpp"
#include "smart_rules/usecases/approve_rules_async.hpp"

#include "stub_drafts.hpp"

namespace {

namespace usecase =
    billing_subventions_x::smart_rules::usecases::approve_rules_async;
namespace types = billing_subventions_x::types;
namespace draft = billing_subventions_x::smart_rules::draft;
using Type = draft::state::StateType;

static auto kNow =
    types::TimePoint{utils::datetime::Stringtime("2021-06-20T18:11:15+0300")};
constexpr auto kApplicable = "2021-06-21T00:00:00+0300";
constexpr auto kTooLate = "2021-06-20T00:00:00+0300";

class ApproveStrategy final : public draft::actions::ApproveStrategy {
 public:
  MOCK_METHOD(void, ApproveRules, (const draft::Draft&), (final));
};

class Limits final : public draft::actions::BudgetBuilder {
 public:
  MOCK_METHOD(std::string, Create,
              (const types::Budget&, const types::TimePoint, const std::string&,
               const std::string&, const std::string&, const std::string&),
              (final));
};

class Output final : public usecase::Output {
 public:
  void SetResponse(usecase::Response&& response) final {
    response_ = std::move(response);
  }

  usecase::Response GetResponse() const { return response_; }

 private:
  usecase::Response response_;
};

class PersonalGoalBulkApproveUseCase : public testing::Test {
 public:
  void SetUp() override {
    request_ = usecase::Request{"some_draft_id", "draft_id", "me,you",
                                "TICKET-1,TICKET-2", kNow};
  }

 protected:
  void ExecuteWith(StubDraftRepository* repo) {
    auto actions = draft::actions::Actions(repo, &limits_, &approver_);
    auto drafts = draft::repository::Drafts{repo, &actions};
    usecase::UseCase(&drafts, &output_).Execute(std::move(request_));
  }

  Output output_{};
  Limits limits_{};
  ApproveStrategy approver_{};
  usecase::Request request_;
};

TEST_F(PersonalGoalBulkApproveUseCase, FailsWhenDraftNotFound) {
  auto repo = NewDraftRepository();
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsFalse());
  ASSERT_THAT(output_.GetResponse().error,
              testing::Eq("Draft \"some_draft_id\" not found"));
}

TEST_F(PersonalGoalBulkApproveUseCase,
       ReturnsApplyingWhenDraftIsStillApplying) {
  auto repo = ApplyingDraftRepository();
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsTrue());
  ASSERT_THAT(output_.GetResponse().is_approved, testing::IsFalse());
}

TEST_F(PersonalGoalBulkApproveUseCase, DoNothingWhenDraftAlreadyApproved) {
  auto repo = ApprovedDraftRepository();
  EXPECT_CALL(repo, SetApprovedAt(testing::_, testing::_)).Times(0);
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsTrue());
  ASSERT_THAT(output_.GetResponse().is_approved, testing::IsTrue());
}

TEST_F(PersonalGoalBulkApproveUseCase, ReturnsErrorWhenTooLateToApprove) {
  auto repo = GeneratedDraftRepository();
  repo.WithStartsAt(kTooLate);
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsFalse());
  ASSERT_THAT(output_.GetResponse().error,
              testing::Eq("Rules' start '2021-06-19T21:00:00+0000' must be "
                          "greater than '2021-06-20T15:11:15+0000'"));
}

TEST_F(PersonalGoalBulkApproveUseCase,
       ReturnsErrorWhenNewRulesClashWithExisted) {
  auto repo = ClashingDraftRepository();
  repo.WithStartsAt(kApplicable);
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsFalse());
  ASSERT_THAT(
      output_.GetResponse().error,
      testing::Eq("New rules conflict with rules for drafts: 12345, 54321"));
}

TEST_F(PersonalGoalBulkApproveUseCase,
       StartsRulesApprovingWhenDraftIsGenerated) {
  const auto budget_id = "budget_id";
  auto repo = GeneratedDraftRepository();
  repo.WithStartsAt(kApplicable);
  EXPECT_CALL(limits_,
              Create(testing::_,
                     types::TimePoint{utils::datetime::Stringtime(kApplicable)},
                     "Bulk smart subventions TICKET-1,TICKET-2", "RUB",
                     request_.approvers, request_.tickets))
      .Times(1)
      .WillOnce(testing::Return(budget_id));
  EXPECT_CALL(repo,
              UpdateDraftSpec(std::string_view{request_.internal_draft_id},
                              std::string_view{request_.draft_id},
                              std::string_view{request_.tickets},
                              std::string_view{request_.approvers},
                              std::string_view{budget_id}))
      .Times(1);
  EXPECT_CALL(approver_, ApproveRules(testing::_)).Times(1);
  ExecuteWith(&repo);
  ASSERT_THAT(output_.GetResponse().is_valid, testing::IsTrue());
  ASSERT_THAT(output_.GetResponse().is_approved, testing::IsFalse());
}

}  // namespace
