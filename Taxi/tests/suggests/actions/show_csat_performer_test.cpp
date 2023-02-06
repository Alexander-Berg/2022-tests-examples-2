#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <defs/all_definitions.hpp>

#include "suggests/actions/show_csat_performer.hpp"
#include "suggests/common.hpp"
#include "suggests/tools/previous_suggest_button_builder.hpp"

namespace {
using eats_messenger::suggests::actions::ShowCsatPerformer;
using TranslationContext = std::unordered_map<std::string, std::string>;
using eats_messenger::localization::ILocalization;
using eats_messenger::suggests::kBackSuggestTextTankerKey;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::tools::IPreviousSuggestButtonBuilder;
using RangeLevelOverrides = ::std::optional<
    ::std::vector<defs::internal::suggests_tree::SuggestRangeleveloverridesA>>;
using defs::internal::suggests_tree::AbstractAction;
using defs::internal::suggests_tree::ActionType;
using defs::internal::suggests_tree::ActionWrapper;
using defs::internal::suggests_tree::SendMessageAction;
using defs::internal::suggests_tree::ShowCsatAction;
using defs::internal::suggests_tree::TerminateChatAction;
using eats_messenger::suggests::actions::ShowCsatActionsRetriever;
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

class MockPreviousSuggestButtonBuilder : public IPreviousSuggestButtonBuilder {
 public:
  MOCK_METHOD(
      SuggestButtonForResponse, Build,
      (const PreviousNodeInfo& previous_node_info,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload),
      (const));
};

TEST(CsatSuggestsPerformer, WithoutBackButton) {
  MockLocalization localization;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;
  ShowCsatPerformer csat_suggests_performer{localization,
                                            previous_suggest_button_builder};
  TranslationContext translation_context;

  ShowCsatAction tree_action;
  tree_action.id = "csat_suggests_id";
  tree_action.type = defs::internal::suggests_tree::ActionType::kShowCsat;
  ActionWrapper action{
      AbstractAction{TerminateChatAction{ActionType::kTerminateChat}}};
  tree_action.actions.emplace_back(
      std::make_unique<defs::internal::suggests_tree::ActionWrapper>(action));

  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id"}};

  std::vector<SuggestButtonForResponse> expected_buttons{
      {"1", {"csat_suggests_id", std::nullopt, std::nullopt, 1}},
      {"2", {"csat_suggests_id", std::nullopt, std::nullopt, 2}},
      {"3", {"csat_suggests_id", std::nullopt, std::nullopt, 3}},
      {"4", {"csat_suggests_id", std::nullopt, std::nullopt, 4}},
      {"5", {"csat_suggests_id", std::nullopt, std::nullopt, 5}}};

  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.one",
                                           translation_context, 1))
      .WillOnce(testing::Return("1"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.two",
                                           translation_context, 1))
      .WillOnce(testing::Return("2"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.three",
                                           translation_context, 1))
      .WillOnce(testing::Return("3"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.four",
                                           translation_context, 1))
      .WillOnce(testing::Return("4"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.five",
                                           translation_context, 1))
      .WillOnce(testing::Return("5"));
  EXPECT_CALL(localization,
              GetTranslation("system.suggests.message.csat.request_to_rate",
                             translation_context, 1))
      .WillOnce(testing::Return("Оцените качество обслуживания"));
  auto actual_result = csat_suggests_performer.Perform(
      tree_action, translation_context, selected_suggest_payload, std::nullopt);
  ASSERT_EQ(actual_result.text_message, "Оцените качество обслуживания");
  ASSERT_EQ(actual_result.suggest_buttons, expected_buttons);
}

TEST(CsatSuggestsPerformer, BackButton) {
  MockLocalization localization;
  MockPreviousSuggestButtonBuilder previous_suggest_button_builder;
  ShowCsatPerformer csat_suggests_performer{localization,
                                            previous_suggest_button_builder};
  TranslationContext translation_context;

  ShowCsatAction tree_action;
  tree_action.id = "csat_suggests_id";
  tree_action.type = defs::internal::suggests_tree::ActionType::kShowCsat;
  ActionWrapper action{
      AbstractAction{TerminateChatAction{ActionType::kTerminateChat}}};
  tree_action.actions.emplace_back(
      std::make_unique<defs::internal::suggests_tree::ActionWrapper>(action));

  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, false};
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id"}};
  SuggestButtonForResponse previous_suggest_button{"Назад",
                                                   {"previous_suggest_id"}};

  std::vector<SuggestButtonForResponse> expected_buttons{
      {"1", {"csat_suggests_id", std::nullopt, std::nullopt, 1}},
      {"2", {"csat_suggests_id", std::nullopt, std::nullopt, 2}},
      {"3", {"csat_suggests_id", std::nullopt, std::nullopt, 3}},
      {"4", {"csat_suggests_id", std::nullopt, std::nullopt, 4}},
      {"5", {"csat_suggests_id", std::nullopt, std::nullopt, 5}},
      previous_suggest_button};

  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.one",
                                           translation_context, 1))
      .WillOnce(testing::Return("1"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.two",
                                           translation_context, 1))
      .WillOnce(testing::Return("2"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.three",
                                           translation_context, 1))
      .WillOnce(testing::Return("3"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.four",
                                           translation_context, 1))
      .WillOnce(testing::Return("4"));
  EXPECT_CALL(localization, GetTranslation("system.suggests.buttons.csat.five",
                                           translation_context, 1))
      .WillOnce(testing::Return("5"));
  EXPECT_CALL(localization,
              GetTranslation("system.suggests.message.csat.request_to_rate",
                             translation_context, 1))
      .WillOnce(testing::Return("Оцените качество обслуживания"));
  EXPECT_CALL(previous_suggest_button_builder,
              Build(previous_node_info, selected_suggest_payload))
      .WillOnce(testing::Return(previous_suggest_button));

  auto actual_result = csat_suggests_performer.Perform(
      tree_action, translation_context, selected_suggest_payload,
      previous_node_info);
  ASSERT_EQ(actual_result.text_message, "Оцените качество обслуживания");
  ASSERT_EQ(actual_result.suggest_buttons, expected_buttons);
}

TEST(ShowCsatActionsRetriever, Retrieve) {
  formats::json::Value csat_action = formats::json::FromString(R"({
      "type": "show_csat",
      "id": "csat_suggests_id",
      "actions": [
        {
          "wrapped": {
            "type": "terminate_chat"
          }
        }
      ]
})");
  ShowCsatAction action = defs::internal::suggests_tree::Parse(
      csat_action, formats::parse::To<ShowCsatAction>());

  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"csat_suggests_id", std::nullopt, std::nullopt, 4}};
  ActionWrapper csat_rate_send_message_action{AbstractAction{
      SendMessageAction{ActionType::kSendMessage,
                        "system.suggests.message.csat.rate_four_response"}}};
  std::vector<ActionWrapper> expected_actions = {csat_rate_send_message_action,
                                                 *action.actions[0]};

  ShowCsatActionsRetriever actions_retriever_;
  auto actual_actions =
      actions_retriever_.Retrieve(action, selected_suggest_payload);

  ASSERT_EQ(actual_actions.size(), expected_actions.size());
  ASSERT_EQ(*actual_actions[0], expected_actions[0]);
}
