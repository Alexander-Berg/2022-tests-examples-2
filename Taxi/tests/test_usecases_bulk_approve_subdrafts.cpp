#include <utility>

#include <gmock/gmock.h>

#include "smart_rules/usecases/bulk_approve_subdrafts.hpp"

#include "stub_drafts.hpp"

namespace {

namespace draft = billing_subventions_x::smart_rules::draft;
namespace usecase =
    billing_subventions_x::smart_rules::usecases::bulk_approve_subdrafts;

class BulkApproveSubdrafts : public testing::Test {
 protected:
  void ExecuteWith(StubDraftRepository* repo, usecase::Request&& request) {
    auto actions = draft::actions::Actions(repo);
    auto drafts = draft::repository::Drafts(repo, &actions);
    auto uc = usecase::UseCase(&drafts);
    uc.Execute(std::move(request));
  }
};

TEST_F(BulkApproveSubdrafts, ApprovesRulesForSubdrafts) {
  constexpr auto draft_id = "draft_id";
  constexpr auto budget_id = "budget_id";
  constexpr auto internal_draft_id = "some_draft_id";
  constexpr auto subdrafts_from = "1";
  constexpr auto subdrafts_to = "2";
  const auto schedule_refs = std::vector<std::string>{"s1", "s2"};

  auto repo = ApplyingDraftRepository();
  repo.WithDraftId(draft_id);
  repo.WithBudgetId(budget_id);
  EXPECT_CALL(repo,
              GetScheduleRefsForSubdrafts(std::string_view{internal_draft_id},
                                          std::string_view{subdrafts_from},
                                          std::string_view{subdrafts_to}))
      .Times(1)
      .WillOnce(testing::Return(schedule_refs));
  EXPECT_CALL(repo, ApproveRules(std::string_view{internal_draft_id},
                                 std::string_view{draft_id},
                                 std::string_view{budget_id},
                                 testing::Optional(schedule_refs)))
      .Times(1);
  EXPECT_CALL(repo,
              GenerateScheduleForMatching(std::string_view{internal_draft_id},
                                          testing::Optional(schedule_refs)))
      .Times(1);

  auto request =
      usecase::Request{internal_draft_id, subdrafts_from, subdrafts_to};
  ExecuteWith(&repo, std::move(request));
}

}  // namespace
