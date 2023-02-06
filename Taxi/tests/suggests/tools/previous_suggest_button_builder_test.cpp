#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>

#include <custom/dependencies.hpp>
#include <suggests/tools/previous_suggest_button_builder.hpp>

namespace {
using eats_messenger::localization::ILocalization;
using TranslationContext = std::unordered_map<std::string, std::string>;
using defs::internal::suggests_tree::ActionType;
using eats_messenger::suggests::kBackSuggestTextTankerKey;
using eats_messenger::suggests::kChoseAnotherOrderSuggestTextTankerKey;
using eats_messenger::suggests::PreviousNodeInfo;
using eats_messenger::suggests::PreviousNodeType;
using eats_messenger::suggests::tools::PreviousSuggestButtonBuilder;
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

TEST(PreviousSuggestButtonBuilder, UsualSuggest) {
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id", "order_nr"}};
  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, false};

  MockLocalization mock_localization;

  EXPECT_CALL(mock_localization, GetTranslation(kBackSuggestTextTankerKey))
      .WillOnce(testing::Return("Назад"));

  PreviousSuggestButtonBuilder previous_suggest_button_builder{
      mock_localization};

  handlers::SuggestButtonForResponse expected{
      "Назад", {"previous_suggest_id", "order_nr"}};
  auto actual = previous_suggest_button_builder.Build(previous_node_info,
                                                      selected_suggest_payload);
  ASSERT_EQ(expected, actual);
}

TEST(PreviousSuggestButtonBuilder, ChoseEaterOrder) {
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id", "order_nr"}};
  PreviousNodeInfo previous_node_info{
      "previous_suggest_id", PreviousNodeType::kChoseEaterOrder, false};

  MockLocalization mock_localization;

  EXPECT_CALL(mock_localization,
              GetTranslation(kChoseAnotherOrderSuggestTextTankerKey))
      .WillOnce(testing::Return("Выбрать другой заказ"));

  PreviousSuggestButtonBuilder previous_suggest_button_builder{
      mock_localization};

  handlers::SuggestButtonForResponse expected{
      "Выбрать другой заказ", {"previous_suggest_id", "order_nr"}};
  auto actual = previous_suggest_button_builder.Build(previous_node_info,
                                                      selected_suggest_payload);
  ASSERT_EQ(expected, actual);
}

TEST(PreviousSuggestButtonBuilder, NeedToResetOrderNr) {
  std::optional<handlers::SuggestPayload> selected_suggest_payload{
      {"selected_suggest_id", "order_nr"}};
  PreviousNodeInfo previous_node_info{"previous_suggest_id",
                                      PreviousNodeType::kUsualSuggest, true};

  MockLocalization mock_localization;

  EXPECT_CALL(mock_localization, GetTranslation(kBackSuggestTextTankerKey))
      .WillOnce(testing::Return("Назад"));

  PreviousSuggestButtonBuilder previous_suggest_button_builder{
      mock_localization};

  handlers::SuggestButtonForResponse expected{"Назад", {"previous_suggest_id"}};
  auto actual = previous_suggest_button_builder.Build(previous_node_info,
                                                      selected_suggest_payload);
  ASSERT_EQ(expected, actual);
}
