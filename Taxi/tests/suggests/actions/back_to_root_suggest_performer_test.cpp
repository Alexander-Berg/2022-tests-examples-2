#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>

#include <custom/dependencies.hpp>
#include <suggests/actions/back_to_root_suggest_performer.hpp>

namespace {
using defs::internal::suggests_tree::ActionType;
using defs::internal::suggests_tree::BackToRootAction;
using eats_messenger::localization::ILocalization;
using eats_messenger::suggests::kSuggestsTreeRootId;
using eats_messenger::suggests::actions::BackToRootSuggestPerformer;
using TranslationContext = std::unordered_map<std::string, std::string>;
}  // namespace

class MockLocalization : public ILocalization {
 public:
  MOCK_METHOD(std::string, GetTranslation,
              (const std::string& key,
               const TranslationContext& translation_context, const int count),
              (const, override));
  MOCK_METHOD(std::string, GetTranslation, (const std::string& key),
              (const, override));
};

TEST(BackToRootSuggestPerformer, GreenFlow) {
  BackToRootAction tree_action{ActionType::kShowSuggestReturnToRoot,
                               "system.suggests.buttons.back_to_root"};

  MockLocalization mock_localization;

  EXPECT_CALL(mock_localization,
              GetTranslation("system.suggests.buttons.back_to_root"))
      .WillOnce(testing::Return("Вернуться в начало"));

  BackToRootSuggestPerformer back_to_root_suggest_button_performer{
      mock_localization};

  handlers::SuggestButtonForResponse expected{"Вернуться в начало",
                                              {kSuggestsTreeRootId}};

  auto actual = back_to_root_suggest_button_performer.Perform(tree_action);
  ASSERT_EQ(actual, expected);
}
