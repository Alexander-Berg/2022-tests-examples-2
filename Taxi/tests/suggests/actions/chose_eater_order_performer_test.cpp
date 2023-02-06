#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>

#include <custom/dependencies.hpp>
#include <suggests/actions/chose_eater_order_performer.hpp>
#include <suggests/common.hpp>
#include <suggests/tools/previous_suggest_button_builder.hpp>

#include <taxi_config/taxi_config.hpp>
#include <testing/taxi_config.hpp>

namespace {
using eats_messenger::localization::ILocalization;
using eats_messenger::suggests::EaterOrderForChoosing;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::actions::ChoseEaterOrderPerformer;
using eats_messenger::suggests::actions::ChoseEaterOrderResult;
using eats_messenger::suggests::actions::ChoseEaterOrderResultWithActions;
using eats_messenger::suggests::actions::ChoseEaterOrderResultWithSuggests;
using eats_messenger::suggests::actions::ChoseEaterOrderSkipResolver;
using eats_messenger::suggests::tools::IPreviousSuggestButtonBuilder;
using TranslationContext = std::unordered_map<std::string, std::string>;
using defs::internal::suggests_tree::ActionWrapper;
using defs::internal::suggests_tree::ChoseEaterOrderAction;
using defs::internal::suggests_tree::SendMessageAction;
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

class MockPreviousSuggestButtonBuilder : public IPreviousSuggestButtonBuilder {
 public:
  MOCK_METHOD(
      handlers::SuggestButtonForResponse, Build,
      (const PreviousNodeInfo& previous_node_info,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload),
      (const));
};

dynamic_config::StorageMock CreateConfig() {
  auto json_value = formats::json::FromString(R"({
    "is_not_about_order_skip_allowed": true,
    "is_specified_order_skip_allowed": true
  })");
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_MESSENGER_CHOSE_EATER_ORDER_ACTION_SETTINGS,
        json_value}});
}

TEST(ChoseEaterOrderPerformer, NothingToChose) {
  formats::json::Value json_tree = formats::json::FromString(R"({
    "type": "chose_eater_order",
    "id": "id",
    "specified_order_suggest_tanker_key": "specified_order_suggest_tanker_key",
    "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest_tanker_key",
    "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
    "question_about_grocery_order_actions": [],
    "specified_order_actions": [
      {
        "wrapped": {
          "type": "send_message",
          "message_key": "specified_orders_answer"
        }
      }
    ],
    "question_not_about_order_actions": [
      {
        "wrapped": {
          "type": "send_message",
          "message_key": "question_not_about_answer"
        }
      }
    ]
  })");
  ChoseEaterOrderAction tree_action = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<ChoseEaterOrderAction>());
  handlers::SuggestPayload selected_suggest_payload{"selected_suggest_id"};
  TranslationContext translation_context{{"placeholder", "substitution"}};

  MockLocalization mock_localization;
  MockPreviousSuggestButtonBuilder mock_previous_button_builder;
  auto config = CreateConfig();
  auto taxi_config = config.GetSource();
  ChoseEaterOrderSkipResolver chose_eater_order_skip_resolver{taxi_config};

  ChoseEaterOrderPerformer chose_eater_order_performer{
      mock_localization, mock_previous_button_builder,
      chose_eater_order_skip_resolver};

  ChoseEaterOrderResult expected{ChoseEaterOrderResultWithActions{
      {*tree_action.question_not_about_order_actions[0]},
      std::nullopt,
      std::nullopt}};

  auto actual = chose_eater_order_performer.Perform(
      tree_action, selected_suggest_payload, std::nullopt, translation_context,
      std::nullopt, std::nullopt);

  ASSERT_EQ(std::get<ChoseEaterOrderResultWithActions>(expected).actions,
            std::get<ChoseEaterOrderResultWithActions>(actual).actions);
}

TEST(ChoseEaterOrderPerformer, WithoutBackButton) {
  formats::json::Value json_tree = formats::json::FromString(R"({
    "type": "chose_eater_order",
    "id": "id",
    "specified_order_suggest_tanker_key": "specified_order_suggest_tanker_key",
    "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest_tanker_key",
    "specified_order_actions": [],
    "question_not_about_order_actions": [],
    "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
    "question_about_grocery_order_actions": []
  })");
  ChoseEaterOrderAction tree_action = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<ChoseEaterOrderAction>());
  handlers::SuggestPayload selected_suggest_payload{"selected_suggest_id"};
  TranslationContext translation_context{{"placeholder", "substitution"}};
  TranslationContext translation_context_order_1{{"order_nr", "order_1"}};
  TranslationContext translation_context_order_2{{"order_nr", "order_2"}};
  std::vector<EaterOrderForChoosing> orders_for_choosing{
      {"order_1", translation_context_order_1, false},
      {"order_2", translation_context_order_2, false}};

  MockLocalization mock_localization;
  MockPreviousSuggestButtonBuilder mock_previous_button_builder;

  auto config = CreateConfig();
  auto taxi_config = config.GetSource();
  ChoseEaterOrderSkipResolver chose_eater_order_skip_resolver{taxi_config};

  EXPECT_CALL(mock_localization,
              GetTranslation("specified_order_suggest_tanker_key",
                             translation_context_order_1, 1))
      .WillOnce(testing::Return("Заказ order_1"));
  EXPECT_CALL(mock_localization,
              GetTranslation("specified_order_suggest_tanker_key",
                             translation_context_order_2, 1))
      .WillOnce(testing::Return("Заказ order_2"));
  EXPECT_CALL(mock_localization,
              GetTranslation("question_not_about_order_suggest_tanker_key",
                             translation_context, 1))
      .WillOnce(testing::Return("Вопрос не по заказу"));

  ChoseEaterOrderPerformer chose_eater_order_performer{
      mock_localization, mock_previous_button_builder,
      chose_eater_order_skip_resolver};

  ChoseEaterOrderResult expected{ChoseEaterOrderResultWithSuggests{{
      handlers::SuggestButtonForResponse{"Заказ order_1", {"id", "order_1"}},
      handlers::SuggestButtonForResponse{"Заказ order_2", {"id", "order_2"}},
      handlers::SuggestButtonForResponse{"Вопрос не по заказу", {"id"}},
  }}};
  auto actual = chose_eater_order_performer.Perform(
      tree_action, selected_suggest_payload, std::nullopt, translation_context,
      orders_for_choosing, std::nullopt);
  ASSERT_EQ(
      std::get<ChoseEaterOrderResultWithSuggests>(expected).suggest_buttons,
      std::get<ChoseEaterOrderResultWithSuggests>(actual).suggest_buttons);
}

TEST(ChoseEaterOrderPerformer, WithBackButton) {
  formats::json::Value json_tree = formats::json::FromString(R"({
    "type": "chose_eater_order",
    "id": "id",
    "specified_order_suggest_tanker_key": "specified_order_suggest_tanker_key",
    "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest_tanker_key",
    "specified_order_actions": [],
    "question_not_about_order_actions": [],
    "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
    "question_about_grocery_order_actions": []
  })");
  ChoseEaterOrderAction tree_action = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<ChoseEaterOrderAction>());
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id"}};
  TranslationContext translation_context{{"placeholder", "substitution"}};
  TranslationContext translation_context_order_1{{"order_nr", "order_1"}};
  TranslationContext translation_context_order_2{{"order_nr", "order_2"}};
  std::vector<EaterOrderForChoosing> orders_for_choosing{
      {"order_1", translation_context_order_1, false},
      {"order_2", translation_context_order_2, false}};
  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, false};
  handlers::SuggestButtonForResponse previous_suggest_button{
      "Назад", {"previous_suggest_id"}};

  MockLocalization mock_localization;
  MockPreviousSuggestButtonBuilder mock_previous_button_builder;

  auto config = CreateConfig();
  auto taxi_config = config.GetSource();
  ChoseEaterOrderSkipResolver chose_eater_order_skip_resolver{taxi_config};

  EXPECT_CALL(mock_localization,
              GetTranslation("specified_order_suggest_tanker_key",
                             translation_context_order_1, 1))
      .WillOnce(testing::Return("Заказ order_1"));
  EXPECT_CALL(mock_localization,
              GetTranslation("specified_order_suggest_tanker_key",
                             translation_context_order_2, 1))
      .WillOnce(testing::Return("Заказ order_2"));
  EXPECT_CALL(mock_localization,
              GetTranslation("question_not_about_order_suggest_tanker_key",
                             translation_context, 1))
      .WillOnce(testing::Return("Вопрос не по заказу"));
  EXPECT_CALL(mock_previous_button_builder,
              Build(previous_node_info, selected_suggest_payload))
      .WillOnce(testing::Return(previous_suggest_button));

  ChoseEaterOrderPerformer chose_eater_order_performer{
      mock_localization, mock_previous_button_builder,
      chose_eater_order_skip_resolver};

  ChoseEaterOrderResult expected{ChoseEaterOrderResultWithSuggests{{
      handlers::SuggestButtonForResponse{"Заказ order_1", {"id", "order_1"}},
      handlers::SuggestButtonForResponse{"Заказ order_2", {"id", "order_2"}},
      handlers::SuggestButtonForResponse{"Вопрос не по заказу", {"id"}},
      previous_suggest_button,
  }}};
  auto actual = chose_eater_order_performer.Perform(
      tree_action, selected_suggest_payload, std::nullopt, translation_context,
      orders_for_choosing, previous_node_info);

  ASSERT_EQ(
      std::get<ChoseEaterOrderResultWithSuggests>(expected).suggest_buttons,
      std::get<ChoseEaterOrderResultWithSuggests>(actual).suggest_buttons);
}

TEST(ChoseEaterOrderPerformer, Grocery) {
  formats::json::Value json_tree = formats::json::FromString(R"({
    "type": "chose_eater_order",
    "id": "id",
    "specified_order_suggest_tanker_key": "specified_order_suggest_tanker_key",
    "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest_tanker_key",
    "specified_order_actions": [],
    "question_not_about_order_actions": [],
    "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
    "question_about_grocery_order_actions": []
  })");
  ChoseEaterOrderAction tree_action = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<ChoseEaterOrderAction>());
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id"}};
  TranslationContext translation_context{{"placeholder", "substitution"}};
  TranslationContext translation_context_order_1{{"order_nr", "order_1"}};
  TranslationContext translation_context_order_2{{"order_nr", "order_2"}};
  std::vector<EaterOrderForChoosing> orders_for_choosing{
      {"order_1", translation_context_order_1, true},
      {"order_2", translation_context_order_2, true}};
  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, false};
  handlers::SuggestButtonForResponse previous_suggest_button{
      "Назад", {"previous_suggest_id"}};

  MockLocalization mock_localization;
  MockPreviousSuggestButtonBuilder mock_previous_button_builder;

  auto config = CreateConfig();
  auto taxi_config = config.GetSource();
  ChoseEaterOrderSkipResolver chose_eater_order_skip_resolver{taxi_config};

  EXPECT_CALL(mock_localization,
              GetTranslation("question_about_grocery_order_suggest",
                             translation_context_order_1, 1))
      .WillOnce(testing::Return("Вопрос по заказу из Лавки"));
  EXPECT_CALL(mock_localization,
              GetTranslation("question_about_grocery_order_suggest",
                             translation_context_order_2, 1))
      .WillOnce(testing::Return("Вопрос по заказу из Лавки"));
  EXPECT_CALL(mock_localization,
              GetTranslation("question_not_about_order_suggest_tanker_key",
                             translation_context, 1))
      .WillOnce(testing::Return("Вопрос не по заказу"));
  EXPECT_CALL(mock_previous_button_builder,
              Build(previous_node_info, selected_suggest_payload))
      .WillOnce(testing::Return(previous_suggest_button));

  ChoseEaterOrderPerformer chose_eater_order_performer{
      mock_localization, mock_previous_button_builder,
      chose_eater_order_skip_resolver};

  ChoseEaterOrderResult expected{ChoseEaterOrderResultWithSuggests{{
      handlers::SuggestButtonForResponse{"Вопрос по заказу из Лавки",
                                         {"id", "order_1", true}},
      handlers::SuggestButtonForResponse{"Вопрос по заказу из Лавки",
                                         {"id", "order_2", true}},
      handlers::SuggestButtonForResponse{"Вопрос не по заказу", {"id"}},
      previous_suggest_button,
  }}};
  auto actual = chose_eater_order_performer.Perform(
      tree_action, selected_suggest_payload, std::nullopt, translation_context,
      orders_for_choosing, previous_node_info);

  ASSERT_EQ(
      std::get<ChoseEaterOrderResultWithSuggests>(expected).suggest_buttons,
      std::get<ChoseEaterOrderResultWithSuggests>(actual).suggest_buttons);
}
