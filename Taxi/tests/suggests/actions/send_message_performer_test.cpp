#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include "userver/formats/json.hpp"

#include <defs/all_definitions.hpp>

#include "custom/dependencies.hpp"
#include "suggests/actions/send_message_performer.hpp"

namespace {
using defs::internal::suggests_tree::SendMessageAction;
using eats_messenger::localization::ILocalization;
using eats_messenger::suggests::actions::SendMessagePerformer;
using eats_messenger::suggests::actions::TranslationContext;
using TranslationContext = std::unordered_map<std::string, std::string>;
using defs::internal::suggests_tree::ActionType;
using defs::internal::suggests_tree::Predicate;
using eats_messenger::suggests::IPredicateInterpreter;
using eats_messenger::suggests::actions::KwargsMap;
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

class MockPredicateInterpreter : public IPredicateInterpreter {
 public:
  MOCK_METHOD(bool, Interprete,
              (const Predicate& predicate, const KwargsMap& predicate_kwargs),
              (const));
};

TEST(SendMessagePerformer, MessageKey) {
  SendMessageAction send_message{ActionType::kSendMessage,
                                 "suggests.user_greeting"};
  TranslationContext context{};
  KwargsMap predicate_kwargs;
  MockLocalization localization;
  MockPredicateInterpreter interpreter;

  EXPECT_CALL(localization,
              GetTranslation("suggests.user_greeting", context, 1))
      .WillOnce(testing::Return("Привет, дорогой пользователь!"));

  SendMessagePerformer performer{localization, interpreter};
  auto actual_result =
      performer.Perform(send_message, context, predicate_kwargs);
  ASSERT_EQ(actual_result.message, "Привет, дорогой пользователь!");
}

TEST(SendMessagePerformer, DisabledMessageKey) {
  SendMessageAction disabled_send_message{
      ActionType::kSendMessage,
      "suggests.user_greeting",
      {{defs::internal::suggests_tree::PredicateType::kFalse}}};
  TranslationContext context{};
  KwargsMap predicate_kwargs;
  MockLocalization localization;
  MockPredicateInterpreter interpreter;

  EXPECT_CALL(interpreter,
              Interprete(disabled_send_message.enabling_predicate.value(),
                         testing::Ref(predicate_kwargs)))
      .WillOnce(testing::Return(false));

  SendMessagePerformer performer{localization, interpreter};
  auto actual_result =
      performer.Perform(disabled_send_message, context, predicate_kwargs);
  ASSERT_EQ(actual_result.message, std::nullopt);
}
