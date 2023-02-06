#include <gmock/gmock.h>

#include "userver/formats/json.hpp"

#include <defs/all_definitions.hpp>

#include "custom/dependencies.hpp"
#include "suggests/actions/chose_eater_order_performer.hpp"
#include "suggests/actions/show_csat_performer.hpp"
#include "suggests/common.hpp"
#include "suggests/suggests_tree/traverser.hpp"

namespace {
using defs::internal::suggests_tree::AbstractAction;
using defs::internal::suggests_tree::ActionType;
using defs::internal::suggests_tree::ActionWrapper;
using defs::internal::suggests_tree::ChoseEaterOrderAction;
using defs::internal::suggests_tree::SendMessageAction;
using defs::internal::suggests_tree::ShowCsatAction;
using defs::internal::suggests_tree::ShowSuggestsAction;
using eats_messenger::suggests::EaterOrderForChoosing;
using eats_messenger::suggests::kSuggestsTreeRootId;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::actions::DummyChoseEaterOrderSkipResolver;
using eats_messenger::suggests::actions::IShowCsatActionsRetriever;
using eats_messenger::suggests::suggests_tree::SuggestNotFoundException;
using eats_messenger::suggests::suggests_tree::SuggestsTreeRoot;
using eats_messenger::suggests::suggests_tree::Traverser;
using Actions = ::std::vector<
    ::codegen::NonNullPtr<defs::internal::suggests_tree::ActionWrapper>>;
using eats_messenger::suggests::suggests_tree::DummyTraverserMetrics;
}  // namespace

class MockShowCsatActionsRetriever : public IShowCsatActionsRetriever {
 public:
  MOCK_METHOD(Actions, Retrieve,
              (const ShowCsatAction& tree_action,
               const std::optional<::handlers::SuggestPayload>&
                   selected_suggest_payload),
              (const));
};

TEST(Traverser, Root) {
  formats::json::Value json_tree = formats::json::FromString(R"({
    "actions": [
      {
        "wrapped": {
          "type": "send_message",
          "message_key": "Здравствуйте! Чем мы можем вам помочь?"
        }
      }
    ]
  })");

  SendMessageAction expected_send_message_action{
      ActionType::kSendMessage, "Здравствуйте! Чем мы можем вам помочь?"};
  handlers::SuggestPayload selected_suggest_payload{kSuggestsTreeRootId};

  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};
  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});
  ASSERT_EQ(actual_result.previous_node_info, std::nullopt);
  ASSERT_EQ(actual_result.actions.size(), 1);
  ASSERT_EQ(actual_result.actions[0].wrapped.As<SendMessageAction>(),
            expected_send_message_action);
}

TEST(Traverser, GreenFlow) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "Здравствуйте! Чем мы можем вам помочь?"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "payment",
            "title_key": "Оплата",
            "actions": [
              {
                "wrapped": {
                  "type": "send_message",
                  "message_key": "Что именно вас интересует по вопросу оплаты?"
                }
              },
              {
                "wrapped": {
                  "type": "show_suggests",
                  "suggests": [
                    {
                      "id": "payment_did_not_pass",
                      "title_key": "Оплата не прошла",
                      "actions": [
                        {
                          "wrapped": {
                            "type": "send_message",
                            "message_key": "Попробуйте другую карту. Это помогло?"
                          }
                        }
                      ]
                    }
                  ]
                }
              }
            ]
          }
        ]
      }
    }
  ]
})");
  SendMessageAction expected_send_message_action{
      ActionType::kSendMessage, "Попробуйте другую карту. Это помогло?"};
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"payment_did_not_pass"};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};
  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});
  ASSERT_EQ(actual_result.previous_node_info->id, "payment");
  ASSERT_EQ(actual_result.previous_node_info->type,
            PreviousNodeType::kUsualSuggest);
  ASSERT_EQ(actual_result.previous_node_info->need_to_reset_order_nr, false);
  ASSERT_EQ(actual_result.actions.size(), 1);
  ASSERT_EQ(actual_result.actions[0].wrapped.As<SendMessageAction>(),
            expected_send_message_action);
}

TEST(Traverser, NotFoundSuggest) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "send_message",
        "message_key": "Здравствуйте! Чем мы можем вам помочь?"
      }
    },
    {
      "wrapped": {
        "type": "show_suggests",
        "suggests": [
          {
            "id": "payment",
            "title_key": "Оплата",
            "actions": [
              {
                "wrapped": {
                  "type": "send_message",
                  "message_key": "Что именно вас интересует по вопросу оплаты?"
                }
              },
              {
                "wrapped": {
                  "type": "show_suggests",
                  "suggests": [
                    {
                      "id": "payment_did_not_pass",
                      "title_key": "Оплата не прошла",
                      "actions": [
                        {
                          "wrapped": {
                            "type": "send_message",
                            "message_key": "Попробуйте другую карту. Это помогло?"
                          }
                        }
                      ]
                    }
                  ]
                }
              }
            ]
          }
        ]
      }
    }
  ]
})");
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"nonexistent_suggest_id"};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};
  ASSERT_THROW(traverser.RetrieveActions(tree, selected_suggest_payload, {}),
               SuggestNotFoundException);
}

TEST(Traverser, ChoseEaterOrderSelectedSpecifiedOrderSuggest) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "question_about_grocery_order_actions": [],
        "specified_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "payment_problem",
                  "title_key": "payment_problem_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "payment_problem_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "how_to_create_order",
                  "title_key": "how_to_create_order_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "how_to_create_order_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    }
  ]
})");
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"chose_eater_order",
                                                    "order_nr"};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};

  PreviousNodeInfo expected_previous_node_info{
      "root", PreviousNodeType::kChoseEaterOrder, true};
  std::vector<ActionWrapper> expected_actions = {
      *tree.actions[0]
           .wrapped.As<ChoseEaterOrderAction>()
           .specified_order_actions[0]};

  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});

  ASSERT_EQ(actual_result.previous_node_info, expected_previous_node_info);
  ASSERT_EQ(actual_result.actions, expected_actions);
}

TEST(Traverser, ChoseEaterOrderFindInSpecifiedOrderActions) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "question_about_grocery_order_actions": [],
        "specified_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "payment_problem",
                  "title_key": "payment_problem_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "payment_problem_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "how_to_create_order",
                  "title_key": "how_to_create_order_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "how_to_create_order_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    }
  ]
})");
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"payment_problem",
                                                    "order_nr"};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};

  PreviousNodeInfo expected_previous_node_info{
      "chose_eater_order", PreviousNodeType::kUsualSuggest, false};
  std::vector<ActionWrapper> expected_actions = {
      tree.actions[0]
          .wrapped.As<ChoseEaterOrderAction>()
          .specified_order_actions[0]
          ->wrapped.As<ShowSuggestsAction>()
          .suggests[0]
          ->actions};

  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});

  ASSERT_EQ(actual_result.previous_node_info, expected_previous_node_info);
  ASSERT_EQ(actual_result.actions, expected_actions);
}

TEST(Traverser, ChoseEaterOrderFindInQuestionNotAboutOrderActions) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "question_about_grocery_order_actions": [],
        "specified_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "payment_problem",
                  "title_key": "payment_problem_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "payment_problem_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ],
        "question_not_about_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "how_to_create_order",
                  "title_key": "how_to_create_order_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "how_to_create_order_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    }
  ]
})");
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"how_to_create_order",
                                                    "order_nr"};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;

  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};

  PreviousNodeInfo expected_previous_node_info{
      "chose_eater_order", PreviousNodeType::kUsualSuggest, false};
  std::vector<ActionWrapper> expected_actions = {
      tree.actions[0]
          .wrapped.As<ChoseEaterOrderAction>()
          .question_not_about_order_actions[0]
          ->wrapped.As<ShowSuggestsAction>()
          .suggests[0]
          ->actions};

  std::vector<EaterOrderForChoosing> orders_for_choosing{
      {"order_1", {}, false}};
  auto actual_result = traverser.RetrieveActions(tree, selected_suggest_payload,
                                                 {orders_for_choosing});

  ASSERT_EQ(actual_result.previous_node_info, expected_previous_node_info);
  ASSERT_EQ(actual_result.actions, expected_actions);
}

TEST(Traverser, ChoseEaterOrderFindInQuestionAboutGroceryOrderActions) {
  formats::json::Value json_tree = formats::json::FromString(R"({
  "actions": [
    {
      "wrapped": {
        "type": "chose_eater_order",
        "id": "chose_eater_order",
        "specified_order_suggest_tanker_key": "specified_order_suggest",
        "question_not_about_order_suggest_tanker_key": "question_not_about_order_suggest",
        "question_about_grocery_order_actions_tanker_key": "question_about_grocery_order_suggest",
        "question_not_about_order_actions": [],
        "specified_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "payment_problem",
                  "title_key": "payment_problem_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "payment_problem_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ],
        "question_about_grocery_order_actions": [
          {
            "wrapped": {
              "type": "show_suggests",
              "suggests": [
                {
                  "id": "how_to_create_order",
                  "title_key": "how_to_create_order_suggest",
                  "actions": [
                    {
                      "wrapped": {
                        "type": "send_message",
                        "message_key": "how_to_create_order_answer"
                      }
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    }
  ]
})");
  SuggestsTreeRoot tree = defs::internal::suggests_tree::Parse(
      json_tree, formats::parse::To<SuggestsTreeRoot>());
  handlers::SuggestPayload selected_suggest_payload{"how_to_create_order",
                                                    "order_nr", true};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};

  PreviousNodeInfo expected_previous_node_info{
      "chose_eater_order", PreviousNodeType::kUsualSuggest, false};
  std::vector<ActionWrapper> expected_actions = {
      tree.actions[0]
          .wrapped.As<ChoseEaterOrderAction>()
          .question_about_grocery_order_actions[0]
          ->wrapped.As<ShowSuggestsAction>()
          .suggests[0]
          ->actions};

  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});

  ASSERT_EQ(actual_result.previous_node_info, expected_previous_node_info);
  ASSERT_EQ(actual_result.actions, expected_actions);
}

TEST(Traverser, ShowCsat) {
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
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"csat_suggests_id", std::nullopt, std::nullopt, 4}};
  PreviousNodeInfo expected_previous_node_info{
      "root", PreviousNodeType::kShowCsat, false};

  MockShowCsatActionsRetriever actions_retriever_;
  DummyTraverserMetrics stats_;
  DummyChoseEaterOrderSkipResolver chose_eater_order_skip_resolver_;
  Traverser traverser{actions_retriever_, chose_eater_order_skip_resolver_,
                      stats_};

  std::vector<ActionWrapper> expected_actions = {
      *tree.actions[0].wrapped.As<ShowCsatAction>().actions[0]};

  Actions expected_mock_actions{
      tree.actions[0].wrapped.As<ShowCsatAction>().actions[0]};
  EXPECT_CALL(actions_retriever_,
              Retrieve(tree.actions[0].wrapped.As<ShowCsatAction>(),
                       selected_suggest_payload))
      .WillOnce(testing::Return(expected_mock_actions));

  auto actual_result =
      traverser.RetrieveActions(tree, selected_suggest_payload, {});
  ASSERT_EQ(actual_result.previous_node_info, expected_previous_node_info);
  ASSERT_EQ(actual_result.actions, expected_actions);
}
