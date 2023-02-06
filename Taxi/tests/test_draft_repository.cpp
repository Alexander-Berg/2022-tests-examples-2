#include <gmock/gmock.h>

#include <memory>
#include <string>

#include <userver/formats/json/value.hpp>

#include "smart_rules/draft/actions.hpp"
#include "smart_rules/draft/draft.hpp"
#include "smart_rules/draft/repository.hpp"
#include "smart_rules/draft/state.hpp"

#include "stub_drafts.hpp"

namespace {

namespace draft = billing_subventions_x::smart_rules::draft;
using Type = draft::state::StateType;

constexpr auto kInternalDraftId = "some_draft_id";
constexpr auto kAuthor = "author";
static const formats::json::Value kSpec = {};

static const auto _ = testing::_;

class DraftsRepository : public testing::Test {
 protected:
  draft::DraftPtr GetDraftFrom(StubDraftRepository* repo,
                               draft::ActionsPtr actions) {
    draft::repository::Drafts drafts_{repo, actions};
    return drafts_.Get(kInternalDraftId);
  }

  draft::DraftPtr GetOrCreateDraftFrom(StubDraftRepository* repo,
                                       draft::ActionsPtr actions) {
    draft::repository::Drafts drafts_{repo, actions};
    return drafts_.GetOrCreate(kInternalDraftId, kSpec, kAuthor);
  }
};

TEST_F(DraftsRepository, GetOrCreateCreatesDraftWhenDoesNotExist) {
  auto repo = NewDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  EXPECT_CALL(repo, CreateDraftSpec(std::string_view{kInternalDraftId}, kSpec,
                                    std::string_view{kAuthor}));
  const auto draft = GetOrCreateDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kNew));
}

TEST_F(DraftsRepository, ReturnsInvalidDraftWhenDraftDoesNotExist) {
  auto repo = NewDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  EXPECT_CALL(repo, UpdateState(_, _, _)).Times(0);
  const auto draft = GetDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kInvalid));
  ASSERT_THAT(draft->GetInvalidReason(),
              testing::Eq("Draft \"some_draft_id\" not found"));
}

TEST_F(DraftsRepository,
       ReturnsDraftInGeneratingWhenNotAllRuleDraftsGenerated) {
  auto repo = GeneratingDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  const auto draft = GetDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kGenerating));
}

TEST_F(DraftsRepository, ReturnsDraftInGeneratedWhenDraftExists) {
  auto repo = GeneratedDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  const auto draft = GetDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kGenerated));
}

TEST_F(DraftsRepository,
       ReturnsDraftInApplyingStateWhenHasDraftIdButNotApprovedAt) {
  auto repo = ApplyingDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  const auto draft = GetDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kApplying));
}

TEST_F(DraftsRepository, ReturnsDraftInApprovedStateWhenApproved) {
  auto repo = ApprovedDraftRepository();
  auto actions = draft::actions::Actions{&repo};
  const auto draft = GetDraftFrom(&repo, &actions);
  ASSERT_THAT(draft->GetCurrentState().Type(), testing::Eq(Type::kApproved));
}

}  // namespace
