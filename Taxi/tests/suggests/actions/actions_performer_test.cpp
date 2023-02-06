#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>

#include <suggests/actions/actions_performer.hpp>
#include <suggests/common.hpp>

namespace {
using defs::internal::suggests_tree::AbstractAction;
using defs::internal::suggests_tree::ActionWrapper;
using defs::internal::suggests_tree::BackToRootAction;
using defs::internal::suggests_tree::ChoseEaterOrderAction;
using defs::internal::suggests_tree::SendMessageAction;
using defs::internal::suggests_tree::ShowCsatAction;
using defs::internal::suggests_tree::ShowSuggestsAction;
using defs::internal::suggests_tree::SuggestsTreeRoot;
using defs::internal::suggests_tree::SwitchChatToChatterboxAction;
using defs::internal::suggests_tree::TerminateChatAction;
using eats_messenger::suggests::BusinessLogicData;
using eats_messenger::suggests::EaterOrderForChoosing;
using eats_messenger::suggests::kSuggestsTreeRootId;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::actions::ActionsPerformer;
using eats_messenger::suggests::actions::ChoseEaterOrderResult;
using eats_messenger::suggests::actions::ChoseEaterOrderResultWithActions;
using eats_messenger::suggests::actions::ChoseEaterOrderResultWithSuggests;
using eats_messenger::suggests::actions::IAllowedActionTypesProvider;
using eats_messenger::suggests::actions::IBackToRootSuggestPerformer;
using eats_messenger::suggests::actions::IChoseEaterOrderPerformer;
using eats_messenger::suggests::actions::ISendMessagePerformer;
using eats_messenger::suggests::actions::IShowCsatPerformer;
using eats_messenger::suggests::actions::IShowSuggestsPerformer;
using eats_messenger::suggests::actions::SendMessageResult;
using eats_messenger::suggests::actions::ShowCsatResult;
using eats_messenger::suggests::actions::ShowSuggestsResult;
using eats_messenger::suggests::suggests_tree::TraverseResult;
using handlers::SuccessSuggestsEventResponse;
using handlers::UnprocessableSuggestsEventResponse;
using TranslationContext = std::unordered_map<std::string, std::string>;
using experiments3::models::KwargsMap;
using testing::_;
using PerformingResult = std::variant<SuccessSuggestsEventResponse,
                                      UnprocessableSuggestsEventResponse>;
using defs::internal::suggests_tree::ActionType;
using eats_messenger::suggests::actions::ActionsPerformingResult;
using eats_messenger::suggests::actions::DummyActionsPerformerMetrics;
using handlers::SuggestButtonForResponse;

const std::set<ActionType>& kNoActionsAllowed{};
const std::set<ActionType>& kAllActionsAllowed{
    ActionType::kChoseEaterOrder,
    ActionType::kSendMessage,
    ActionType::kShowSuggests,
    ActionType::kTerminateChat,
    ActionType::kSwitchChatToChatterbox,
    ActionType::kShowSuggestReturnToRoot,
    ActionType::kShowCsat};
}  // namespace

class MockBackToRootPerformer : public IBackToRootSuggestPerformer {
 public:
  MOCK_METHOD(SuggestButtonForResponse, Perform,
              (const BackToRootAction& tree_action), (const));
};

class MockSendMessagePerformer : public ISendMessagePerformer {
 public:
  MOCK_METHOD(SendMessageResult, Perform,
              (const SendMessageAction& payload,
               const TranslationContext& translation_context,
               const KwargsMap& predicate_kwargs),
              (const));
};

class MockShowSuggestsPerformer : public IShowSuggestsPerformer {
 public:
  MOCK_METHOD(
      ShowSuggestsResult, Perform,
      (const ShowSuggestsAction& payload, const KwargsMap& predicate_kwargs,
       const TranslationContext& translation_context,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload,
       const std::optional<PreviousNodeInfo>& previous_node_info),
      (const));
};

class MockChoseEaterOrderPerformer : public IChoseEaterOrderPerformer {
 public:
  MOCK_METHOD(
      ChoseEaterOrderResult, Perform,
      (const ChoseEaterOrderAction& tree_action,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload,
       const std::optional<handlers::SuggestsEventContext>& context,
       const TranslationContext& translation_context,
       const std::optional<std::vector<EaterOrderForChoosing>>&
           eater_orders_for_choosing,
       const std::optional<PreviousNodeInfo>& previous_node_info),
      (const));
};

class MockShowCsatPerformer : public IShowCsatPerformer {
 public:
  MOCK_METHOD(
      ShowCsatResult, Perform,
      (const ShowCsatAction& tree_action,
       const TranslationContext& translation_context,
       const std::optional<handlers::SuggestPayload>& selected_suggest_payload,
       const std::optional<PreviousNodeInfo>& previous_node_info),
      (const));
};

class MockAllowedActionTypesProvider : public IAllowedActionTypesProvider {
 public:
  MOCK_METHOD(std::set<ActionType>, Provide, (), (const));
};

TEST(ActionsPerformer, NoActionsAllowed) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "how_to_create_order_answer"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "payment_problem",
            "title_key": "payment_problem_suggest",
            "actions": []
          }
        ]
      }
    },
    {
      "wrapped": {
        "type": "terminate_chat"
      }
    },
    {
      "wrapped": {
        "type": "switch_chat_to_chatterbox"
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key" : "question_about_grocery_order_suggest",
        "specified_order_actions": [],
        "question_not_about_order_actions": [],
        "question_about_grocery_order_actions": []
      }
    },
    {
      "wrapped": {
        "type": "show_csat",
        "id": "csat_suggests_id",
        "actions": []
      }
    },
    {
      "wrapped": {
        "type": "show_suggest_return_to_root",
        "suggest_tanker_key": "system.suggests.buttons.back_to_root"
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer, Perform(_, _, _)).Times(0);
  EXPECT_CALL(mock_show_suggests_performer, Perform(_, _, _, _, _)).Times(0);
  EXPECT_CALL(mock_chose_eater_order_performer, Perform(_, _, _, _, _, _))
      .Times(0);
  EXPECT_CALL(mock_show_csat_performer, Perform(_, _, _, _)).Times(0);
  EXPECT_CALL(mock_back_to_root_performer, Perform(_)).Times(0);
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kNoActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  TraverseResult traverse_result{tree.actions, std::nullopt};
  BusinessLogicData business_logic_data{std::nullopt};
  ActionsPerformingResult expected{{},
                                   traverse_result.actions,
                                   std::nullopt,
                                   traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(traverse_result, {}, {}, std::nullopt,
                                          std::nullopt, business_logic_data);
  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, MessageWithSuggests) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "how_to_create_order_answer"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "payment_problem",
            "title_key": "payment_problem_suggest",
            "actions": []
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Ответ на вопрос"};
  ShowSuggestsResult show_suggests_result{{handlers::SuggestButtonForResponse{
      "Проблема с оплатой", {"payment_problem", "order_nr"}}}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(mock_show_suggests_performer,
              Perform(tree.actions[1].wrapped.As<ShowSuggestsAction>(),
                      testing::Ref(predicate_kwargs), translation_context,
                      selected_suggest_payload, previous_node_info))
      .WillOnce(testing::Return(show_suggests_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Ответ на вопрос", show_suggests_result.suggest_buttons, false, false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, MessageWithTerminateChat) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "how_to_create_order_answer"
      }
    },
    {
      "wrapped": {
        "type": "terminate_chat"
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Ответ на вопрос"};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Ответ на вопрос", std::nullopt, true, false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, SwitchChatToChatterbox) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "switch_chat_to_chatterbox"
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{{std::nullopt, std::nullopt, false, true},
                                   traverse_result.actions,
                                   selected_suggest_payload,
                                   traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, MessageWithChoseEaterOrderSuggests) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "hello"
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "specified_order_actions": [],
        "question_about_grocery_order_actions": [],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "send_message",
              "message_key": "how_to_create_order_answer"
            }
          },
          {
            "wrapped": {
              "type": "terminate_chat"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Здравствуйте!"};
  ChoseEaterOrderResult chose_eater_order_result{
      ChoseEaterOrderResultWithSuggests{
          {handlers::SuggestButtonForResponse{
               "Заказ такой-то", {"chose_eater_order", "order_nr"}},
           handlers::SuggestButtonForResponse{"Вопрос не по заказу",
                                              {"chose_eater_order"}}}}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  TranslationContext translation_context_order{{"order_nr", "000000-000001"}};
  std::optional<std::vector<EaterOrderForChoosing>> orders_for_choosing{
      {{"000000-000001", translation_context_order, false}}};
  BusinessLogicData business_logic_data{orders_for_choosing};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(
      mock_chose_eater_order_performer,
      Perform(tree.actions[1].wrapped.As<ChoseEaterOrderAction>(),
              selected_suggest_payload,
              std::optional<handlers::SuggestsEventContext>{std::nullopt},
              translation_context, orders_for_choosing, previous_node_info))
      .WillOnce(testing::Return(chose_eater_order_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Здравствуйте!",
       std::get<ChoseEaterOrderResultWithSuggests>(chose_eater_order_result)
           .suggest_buttons,
       false, false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, MessageWithChoseEaterOrderOverridenActions) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "hello"
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "specified_order_actions": [],
        "question_about_grocery_order_actions": [],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "send_message",
              "message_key": "how_to_create_order_answer"
            }
          },
          {
            "wrapped": {
              "type": "terminate_chat"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Здравствуйте!"};
  SendMessageResult send_message_second_result{"Ответ на вопрос"};
  ChoseEaterOrderResult chose_eater_order_result{
      ChoseEaterOrderResultWithActions{
          {*tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_not_about_order_actions[0],
           *tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_not_about_order_actions[1]},
          selected_suggest_payload,
          previous_node_info}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  TranslationContext translation_context_order{{"order_nr", "000000-000001"}};
  std::optional<std::vector<EaterOrderForChoosing>> orders_for_choosing{
      {{"000000-000001", translation_context_order, false}}};
  BusinessLogicData business_logic_data{orders_for_choosing};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(
      mock_chose_eater_order_performer,
      Perform(tree.actions[1].wrapped.As<ChoseEaterOrderAction>(),
              selected_suggest_payload,
              std::optional<handlers::SuggestsEventContext>{std::nullopt},
              translation_context, orders_for_choosing, previous_node_info))
      .WillOnce(testing::Return(chose_eater_order_result));
  EXPECT_CALL(mock_send_message_performer,
              Perform(std::get<ChoseEaterOrderResultWithActions>(
                          chose_eater_order_result)
                          .actions[0]
                          .wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_second_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Ответ на вопрос", std::nullopt, true, false},
      std::get<ChoseEaterOrderResultWithActions>(chose_eater_order_result)
          .actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, MessageWithChoseEaterOrderGrocerySuggests) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "hello"
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "specified_order_actions": [],
        "question_not_about_order_actions": [],
        "question_about_grocery_order_actions": [
          {
            "wrapped": {
              "type": "send_message",
              "message_key": "operator_switching_text"
            }
          },
          {
            "wrapped": {
              "type": "switch_chat_to_chatterbox"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context;
  KwargsMap predicate_kwargs;
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr", true}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Здравствуйте!"};
  SendMessageResult send_message_second_result{"Перевожу на оператора"};
  ChoseEaterOrderResult chose_eater_order_result{
      ChoseEaterOrderResultWithActions{
          {*tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_about_grocery_order_actions[0],
           *tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_about_grocery_order_actions[1]},
          selected_suggest_payload,
          previous_node_info}};

  TraverseResult traverse_result{tree.actions, previous_node_info};
  TranslationContext translation_context_order;
  std::optional<std::vector<EaterOrderForChoosing>> orders_for_choosing;
  BusinessLogicData business_logic_data{orders_for_choosing};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;
  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(
      mock_chose_eater_order_performer,
      Perform(tree.actions[1].wrapped.As<ChoseEaterOrderAction>(),
              selected_suggest_payload,
              std::optional<handlers::SuggestsEventContext>{std::nullopt},
              translation_context, orders_for_choosing, previous_node_info))
      .WillOnce(testing::Return(chose_eater_order_result));
  EXPECT_CALL(mock_send_message_performer,
              Perform(std::get<ChoseEaterOrderResultWithActions>(
                          chose_eater_order_result)
                          .actions[0]
                          .wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_second_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Перевожу на оператора", std::nullopt, false, true},
      std::get<ChoseEaterOrderResultWithActions>(chose_eater_order_result)
          .actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, OnlyFirstMessageAndSuggests) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "first_answer"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "first_suggests_action",
            "title_key": "first_suggest_key",
            "actions": []
          }
        ]
      }
    },
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "second_answer"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "second_suggests_action",
            "title_key": "second_suggest_key",
            "actions": []
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Ответ на первый вопрос"};
  SendMessageResult second_send_message_result{"Неиспользуемый текст"};
  ShowSuggestsResult show_suggests_result{{handlers::SuggestButtonForResponse{
      "Первый саджест", {"first_suggests_action", "order_nr"}}}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[2].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(second_send_message_result));
  EXPECT_CALL(mock_show_suggests_performer,
              Perform(tree.actions[1].wrapped.As<ShowSuggestsAction>(),
                      testing::Ref(predicate_kwargs), translation_context,
                      selected_suggest_payload, previous_node_info))
      .WillOnce(testing::Return(show_suggests_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));
  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Ответ на первый вопрос", show_suggests_result.suggest_buttons, false,
       false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, OnlyFirstPackOfOverridenActions) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "hello"
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "question_about_grocery_order_actions": [],
        "specified_order_actions": [],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "send_message",
              "message_key": "how_to_create_order_answer"
            }
          },
          {
            "wrapped": {
              "type": "terminate_chat"
            }
          }
        ]
      }
    },
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "second_chose_eater_order",
        "specified_order_suggest_tanker_key": "second_specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "second_question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "specified_order_actions": [],
        "question_about_grocery_order_actions": [],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "switch_chat_to_chatterbox"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context{{"placeholder", "substitution"}};
  KwargsMap predicate_kwargs;
  predicate_kwargs.Update("key", "value");
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"suggest_id", "order_nr"}};
  std::optional<PreviousNodeInfo> previous_node_info{
      {"previous_suggest_id", PreviousNodeType::kUsualSuggest, false}};
  SendMessageResult send_message_result{"Здравствуйте!"};
  SendMessageResult send_message_second_result{"Ответ на вопрос"};
  ChoseEaterOrderResult chose_eater_order_result{
      ChoseEaterOrderResultWithActions{
          {*tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_not_about_order_actions[0],
           *tree.actions[1]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_not_about_order_actions[1]},
          selected_suggest_payload,
          previous_node_info}};
  ChoseEaterOrderResult second_chose_eater_order_result{
      ChoseEaterOrderResultWithActions{
          {*tree.actions[2]
                .wrapped.As<ChoseEaterOrderAction>()
                .question_not_about_order_actions[0]},
          selected_suggest_payload,
          previous_node_info}};
  TraverseResult traverse_result{tree.actions, previous_node_info};
  TranslationContext translation_context_order{{"order_nr", "000000-000001"}};
  std::optional<std::vector<EaterOrderForChoosing>> orders_for_choosing{
      {{"000000-000001", translation_context_order, false}}};
  BusinessLogicData business_logic_data{orders_for_choosing};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_send_message_performer,
              Perform(tree.actions[0].wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_result));
  EXPECT_CALL(
      mock_chose_eater_order_performer,
      Perform(tree.actions[1].wrapped.As<ChoseEaterOrderAction>(),
              selected_suggest_payload,
              std::optional<handlers::SuggestsEventContext>{std::nullopt},
              translation_context, orders_for_choosing, previous_node_info))
      .WillOnce(testing::Return(chose_eater_order_result));
  EXPECT_CALL(
      mock_chose_eater_order_performer,
      Perform(tree.actions[2].wrapped.As<ChoseEaterOrderAction>(),
              selected_suggest_payload,
              std::optional<handlers::SuggestsEventContext>{std::nullopt},
              translation_context, orders_for_choosing, previous_node_info))
      .WillOnce(testing::Return(second_chose_eater_order_result));
  EXPECT_CALL(mock_send_message_performer,
              Perform(std::get<ChoseEaterOrderResultWithActions>(
                          chose_eater_order_result)
                          .actions[0]
                          .wrapped.As<SendMessageAction>(),
                      translation_context, testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(send_message_second_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));
  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Ответ на вопрос", std::nullopt, true, false},
      std::get<ChoseEaterOrderResultWithActions>(chose_eater_order_result)
          .actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, BackToRootAction) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "show_suggest_return_to_root",
        "suggest_tanker_key": "system.suggests.buttons.back_to_root"
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context;
  KwargsMap predicate_kwargs;
  TraverseResult traverse_result{tree.actions, std::nullopt};
  BackToRootAction tree_action{ActionType::kShowSuggestReturnToRoot,
                               "system.suggests.buttons.back_to_root"};
  SuggestButtonForResponse suggest_button{"Вернуться в начало",
                                          {kSuggestsTreeRootId}};
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  EXPECT_CALL(mock_back_to_root_performer, Perform(tree_action))
      .WillOnce(testing::Return(suggest_button));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {std::nullopt, {{suggest_button}}, false, false},
      traverse_result.actions,
      std::nullopt,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(traverse_result, predicate_kwargs,
                                          translation_context, std::nullopt,
                                          std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, CsatSuggestsAction) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "show_csat",
        "id": "csat_suggests_id",
        "actions": [
          {
            "wrapped": {
              "type": "terminate_chat"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context;
  KwargsMap predicate_kwargs;

  TraverseResult traverse_result{tree.actions, std::nullopt};

  std::optional<handlers::SuggestPayload> selected_suggest_payload;
  std::optional<PreviousNodeInfo> previous_node_info;
  BusinessLogicData business_logic_data{std::nullopt};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  ShowCsatResult csat_performer_result{
      {{"1", {"csat_suggests_id", std::nullopt, std::nullopt, 1}},
       {"2", {"csat_suggests_id", std::nullopt, std::nullopt, 2}},
       {"3", {"csat_suggests_id", std::nullopt, std::nullopt, 3}},
       {"4", {"csat_suggests_id", std::nullopt, std::nullopt, 4}},
       {"5", {"csat_suggests_id", std::nullopt, std::nullopt, 5}}},
      "Оцените качество обслуживания"};

  EXPECT_CALL(
      mock_show_csat_performer,
      Perform(tree.actions[0].wrapped.As<ShowCsatAction>(), translation_context,
              selected_suggest_payload, previous_node_info))
      .WillOnce(testing::Return(csat_performer_result));
  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Оцените качество обслуживания", csat_performer_result.suggest_buttons,
       false, false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(traverse_result, predicate_kwargs,
                                          translation_context, std::nullopt,
                                          std::nullopt, business_logic_data);

  ASSERT_EQ(expected, actual);
}

TEST(ActionsPerformer, CsatSuggestSelected) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "show_csat",
        "id": "csat_suggests_id",
        "actions": [
          {
            "wrapped": {
              "type": "terminate_chat"
            }
          }
        ]
      }
    }
  ]
})");

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  TranslationContext translation_context;
  KwargsMap predicate_kwargs;
  PreviousNodeInfo previous_node_info{"root", PreviousNodeType::kShowCsat,
                                      false};

  ActionWrapper csat_rate_send_message_action{AbstractAction{
      SendMessageAction{ActionType::kSendMessage,
                        "system.suggests.message.csat.rate_four_response"}}};
  std::vector<ActionWrapper> actions = {
      csat_rate_send_message_action,
      *tree.actions[0].wrapped.As<ShowCsatAction>().actions[0]};
  BusinessLogicData business_logic_data{std::nullopt};

  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"csat_suggests_id", std::nullopt, std::nullopt, 4}};
  TraverseResult traverse_result{actions, previous_node_info};

  MockSendMessagePerformer mock_send_message_performer;
  MockShowSuggestsPerformer mock_show_suggests_performer;
  MockChoseEaterOrderPerformer mock_chose_eater_order_performer;
  MockShowCsatPerformer mock_show_csat_performer;
  MockAllowedActionTypesProvider mock_allowed_action_types_provider;
  MockBackToRootPerformer mock_back_to_root_performer;
  DummyActionsPerformerMetrics stats_;

  SendMessageAction csat_rate_response{
      defs::internal::suggests_tree::ActionType::kSendMessage,
      "system.suggests.message.csat.rate_four_response"};

  EXPECT_CALL(mock_allowed_action_types_provider, Provide())
      .WillRepeatedly(testing::Return(kAllActionsAllowed));
  EXPECT_CALL(mock_send_message_performer,
              Perform(csat_rate_response, translation_context,
                      testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(
          SendMessageResult{"Спасибо за отзыв, крепкая четвёрочка"}));

  ActionsPerformer actions_performer(
      mock_send_message_performer, mock_show_suggests_performer,
      mock_chose_eater_order_performer, mock_back_to_root_performer,
      mock_show_csat_performer, mock_allowed_action_types_provider, stats_);

  ActionsPerformingResult expected{
      {"Спасибо за отзыв, крепкая четвёрочка", std::nullopt, true, false},
      traverse_result.actions,
      selected_suggest_payload,
      traverse_result.previous_node_info};
  auto actual = actions_performer.Perform(
      traverse_result, predicate_kwargs, translation_context,
      selected_suggest_payload, std::nullopt, business_logic_data);

  ASSERT_EQ(actual, expected);
}
