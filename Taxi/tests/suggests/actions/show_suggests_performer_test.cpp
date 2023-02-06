#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <defs/all_definitions.hpp>

#include "suggests/actions/show_suggests_performer.hpp"
#include "suggests/common.hpp"
#include "suggests/predicate_interpreter.hpp"
#include "suggests/tools/previous_suggest_button_builder.hpp"

namespace {
using defs::internal::suggests_tree::ShowSuggestsAction;
using defs::internal::suggests_tree::Suggest;
using eats_messenger::suggests::actions::ShowSuggestsPerformer;
using TranslationContext = std::unordered_map<std::string, std::string>;
using eats_messenger::localization::ILocalization;
using eats_messenger::suggests::IPredicateInterpreter;
using eats_messenger::suggests::kBackSuggestTextTankerKey;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::actions::IRangeLevelCalculator;
using eats_messenger::suggests::actions::KwargsMap;
using eats_messenger::suggests::tools::IPreviousSuggestButtonBuilder;
using RangeLevelOverrides = ::std::optional<
    ::std::vector<defs::internal::suggests_tree::SuggestRangeleveloverridesA>>;
using defs::internal::suggests_tree::ActionType;
using defs::internal::suggests_tree::Predicate;
using handlers::SuggestButtonForResponse;
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

class MockCalculator : public IRangeLevelCalculator {
 public:
  MOCK_METHOD(int, Calculate,
              (const RangeLevelOverrides& range_level_overrides,
               const KwargsMap& predicate_kwargs),
              (const));
};

class MockPredicateInterpreter : public IPredicateInterpreter {
 public:
  MOCK_METHOD(bool, Interprete,
              (const Predicate& predicate, const KwargsMap& predicate_kwargs),
              (const));
};

class MockPreviousSuggestButtonBuilder : public IPreviousSuggestButtonBuilder {
 public:
  MOCK_METHOD(
      SuggestButtonForResponse, Build,
      (const PreviousNodeInfo& previous_node_info,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload),
      (const));
};

TEST(ShowSuggestsPerformer, WithoutBackButton) {
  Suggest suggest;
  suggest.id = "random_id";
  suggest.title_key = "random_title_key";
  suggest.enabling_predicate.emplace();
  suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kTrue;

  ShowSuggestsAction payload;
  payload.type = ActionType::kShowSuggests;
  payload.suggests.push_back(std::make_unique<Suggest>(suggest));

  KwargsMap predicate_kwargs;
  TranslationContext translation_context;
  MockLocalization localization;
  MockCalculator calculator;
  MockPredicateInterpreter interpreter;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;

  ShowSuggestsPerformer show_suggests_performer{
      localization, interpreter, calculator, previous_suggest_button_builder};

  EXPECT_CALL(interpreter, Interprete(suggest.enabling_predicate.value(),
                                      testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(true));
  EXPECT_CALL(calculator, Calculate(suggest.range_level_overrides,
                                    testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(true));
  EXPECT_CALL(localization,
              GetTranslation(suggest.title_key, translation_context, 1))
      .WillOnce(testing::Return("Привет, как дела?"));
  auto actual_result = show_suggests_performer.Perform(
      payload, predicate_kwargs, translation_context, {}, std::nullopt);

  ASSERT_EQ(actual_result.suggest_buttons.size(), 1);
  ASSERT_EQ(actual_result.suggest_buttons[0].text, "Привет, как дела?");
  ASSERT_EQ(actual_result.suggest_buttons[0].payload.suggest_id, "random_id");
}

TEST(ShowSuggestsPerformer, DisabledByPredicateSuggest) {
  Suggest enabled_suggest;
  enabled_suggest.id = "random_id";
  enabled_suggest.title_key = "random_title_key";
  enabled_suggest.enabling_predicate.emplace();
  enabled_suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kTrue;

  Suggest disabled_suggest;
  disabled_suggest.id = "random_id2";
  disabled_suggest.title_key = "random_title_key2";
  disabled_suggest.enabling_predicate.emplace();
  disabled_suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kFalse;

  ShowSuggestsAction payload;
  payload.type = ActionType::kShowSuggests;
  payload.suggests.push_back(std::make_unique<Suggest>(enabled_suggest));
  payload.suggests.push_back(std::make_unique<Suggest>(disabled_suggest));

  KwargsMap predicate_kwargs;
  TranslationContext translation_context;
  MockLocalization localization;
  MockCalculator calculator;
  MockPredicateInterpreter interpreter;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;

  ShowSuggestsPerformer show_suggests_performer{
      localization, interpreter, calculator, previous_suggest_button_builder};

  EXPECT_CALL(interpreter,
              Interprete(enabled_suggest.enabling_predicate.value(),
                         testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(true));
  EXPECT_CALL(interpreter,
              Interprete(disabled_suggest.enabling_predicate.value(),
                         testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(false));
  EXPECT_CALL(calculator, Calculate(enabled_suggest.range_level_overrides,
                                    testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(500));
  EXPECT_CALL(localization,
              GetTranslation(enabled_suggest.title_key, translation_context, 1))
      .WillOnce(testing::Return("Привет, как дела?"));

  auto actual_result = show_suggests_performer.Perform(
      payload, predicate_kwargs, translation_context, {}, std::nullopt);

  ASSERT_EQ(actual_result.suggest_buttons.size(), 1);
  ASSERT_EQ(actual_result.suggest_buttons[0].text, "Привет, как дела?");

  ASSERT_EQ(actual_result.suggest_buttons[0].payload.suggest_id, "random_id");
}

TEST(ShowSuggestsPerformer, BackSuggest) {
  Suggest suggest;
  suggest.id = "random_id";
  suggest.title_key = "random_title_key";
  suggest.enabling_predicate.emplace();
  suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kTrue;

  ShowSuggestsAction payload;
  payload.type = ActionType::kShowSuggests;
  payload.suggests.push_back(std::make_unique<Suggest>(suggest));

  KwargsMap predicate_kwargs;
  TranslationContext translation_context;
  MockLocalization localization;
  MockCalculator calculator;
  MockPredicateInterpreter interpreter;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;

  SuggestButtonForResponse previous_suggest_button{"Назад",
                                                   {"previous_suggest_id"}};
  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, false};
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id"}};

  ShowSuggestsPerformer show_suggests_performer{
      localization, interpreter, calculator, previous_suggest_button_builder};

  EXPECT_CALL(interpreter, Interprete(suggest.enabling_predicate.value(),
                                      testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(true));
  EXPECT_CALL(calculator, Calculate(suggest.range_level_overrides,
                                    testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(500));
  EXPECT_CALL(localization,
              GetTranslation(suggest.title_key, translation_context, 1))
      .WillOnce(testing::Return("Привет, как дела?"));
  EXPECT_CALL(previous_suggest_button_builder,
              Build(previous_node_info, selected_suggest_payload))
      .WillOnce(testing::Return(previous_suggest_button));
  auto actual_result = show_suggests_performer.Perform(
      payload, predicate_kwargs, translation_context, selected_suggest_payload,
      previous_node_info);

  ASSERT_EQ(actual_result.suggest_buttons.size(), 2);
  ASSERT_EQ(actual_result.suggest_buttons[0].text, "Привет, как дела?");
  ASSERT_EQ(actual_result.suggest_buttons[1].text, "Назад");

  ASSERT_EQ(actual_result.suggest_buttons[0].payload.suggest_id, "random_id");
  ASSERT_EQ(actual_result.suggest_buttons[1].payload.suggest_id,
            "previous_suggest_id");
}

TEST(ShowSuggestsPerformer, SortByLevel) {
  Suggest low_level_suggest;
  low_level_suggest.id = "random_id";
  low_level_suggest.title_key = "random_title_key";
  low_level_suggest.enabling_predicate.emplace();
  low_level_suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kTrue;
  low_level_suggest.range_level_overrides.emplace();
  low_level_suggest.range_level_overrides->push_back({1, std::nullopt});

  Suggest high_level_suggest;
  high_level_suggest.id = "random_id2";
  high_level_suggest.title_key = "random_title_key2";
  high_level_suggest.enabling_predicate.emplace();
  high_level_suggest.enabling_predicate->type =
      defs::internal::suggests_tree::PredicateType::kTrue;
  low_level_suggest.range_level_overrides.emplace();
  low_level_suggest.range_level_overrides->push_back({1000, std::nullopt});

  ShowSuggestsAction payload;
  payload.type = ActionType::kShowSuggests;
  payload.suggests.push_back(std::make_unique<Suggest>(low_level_suggest));
  payload.suggests.push_back(std::make_unique<Suggest>(high_level_suggest));

  KwargsMap predicate_kwargs;
  TranslationContext translation_context;
  MockLocalization localization;
  MockCalculator calculator;
  MockPredicateInterpreter interpreter;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;

  ShowSuggestsPerformer show_suggests_performer{
      localization, interpreter, calculator, previous_suggest_button_builder};

  EXPECT_CALL(
      interpreter,
      Interprete(testing::AnyOf(high_level_suggest.enabling_predicate.value(),
                                low_level_suggest.enabling_predicate.value()),
                 testing::Ref(predicate_kwargs)))
      .Times(2)
      .WillRepeatedly(testing::Return(true));
  EXPECT_CALL(calculator, Calculate(high_level_suggest.range_level_overrides,
                                    testing::Ref(predicate_kwargs)))
      .WillRepeatedly(testing::Return(1000));
  EXPECT_CALL(calculator, Calculate(low_level_suggest.range_level_overrides,
                                    testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(1));
  EXPECT_CALL(localization, GetTranslation(low_level_suggest.title_key,
                                           translation_context, 1))
      .WillOnce(testing::Return("Чо делаешь?"));
  EXPECT_CALL(localization, GetTranslation(high_level_suggest.title_key,
                                           translation_context, 1))
      .WillOnce(testing::Return("Привет, как дела?"));
  auto actual_result = show_suggests_performer.Perform(
      payload, predicate_kwargs, translation_context, {}, std::nullopt);

  ASSERT_EQ(actual_result.suggest_buttons.size(), 2);
  ASSERT_EQ(actual_result.suggest_buttons[0].text, "Привет, как дела?");
  ASSERT_EQ(actual_result.suggest_buttons[1].text, "Чо делаешь?");

  ASSERT_EQ(actual_result.suggest_buttons[0].payload.suggest_id, "random_id2");
  ASSERT_EQ(actual_result.suggest_buttons[1].payload.suggest_id, "random_id");
}
