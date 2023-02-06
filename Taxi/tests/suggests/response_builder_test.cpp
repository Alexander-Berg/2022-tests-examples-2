#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>

#include <suggests/response_builder.hpp>

namespace {
using eats_messenger::suggests::NotEnoughDataToBuildResponseException;
using eats_messenger::suggests::ResponseBuilder;
using eats_messenger::suggests::ResponseBuildingData;
using Response = std::variant<handlers::SuccessSuggestsEventResponse,
                              handlers::UnprocessableSuggestsEventResponse>;
using eats_messenger::suggests::DummyResponseBuilderMetrics;
}  // namespace

TEST(ResponseBuilder, EmptyInputNotEnoughData) {
  ResponseBuildingData response_building_data;

  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;

  ResponseBuilder response_builder{metrics_};
  ASSERT_THROW(response_builder.BuildResponse(response_building_data,
                                              callback_data, std::nullopt),
               NotEnoughDataToBuildResponseException);
}

TEST(ResponseBuilder, OnlyMessageNotEnoughData) {
  ResponseBuildingData response_building_data{"Сообщение", std::nullopt, false,
                                              false};

  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuilder response_builder{metrics_};
  ASSERT_THROW(response_builder.BuildResponse(response_building_data,
                                              callback_data, std::nullopt),
               NotEnoughDataToBuildResponseException);
}

TEST(ResponseBuilder, MessageWithSuggests) {
  std::string message = "Сообщение";
  std::vector<handlers::SuggestButtonForResponse> suggest_buttons{
      handlers::SuggestButtonForResponse{"Саджест 1", {"suggest_1", "order_1"}},
      handlers::SuggestButtonForResponse{"Саджест 2", {"suggest_2", "order_2"}},
  };
  ResponseBuildingData response_building_data{message, suggest_buttons, false,
                                              false};

  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuilder response_builder{metrics_};
  auto actual = response_builder.BuildResponse(response_building_data,
                                               callback_data, std::nullopt);
  EXPECT_EQ(message,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).text);
  EXPECT_EQ(
      suggest_buttons,
      std::get<handlers::SuccessSuggestsEventResponse>(actual).suggest_buttons);
  EXPECT_EQ(false,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).terminal);
}

TEST(ResponseBuilder, MessageWithTerminate) {
  std::string message = "Сообщение";
  ResponseBuildingData response_building_data{message, std::nullopt, true,
                                              false};

  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuilder response_builder{metrics_};
  auto actual = response_builder.BuildResponse(response_building_data,
                                               callback_data, std::nullopt);
  EXPECT_EQ(message,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).text);
  EXPECT_EQ(
      std::nullopt,
      std::get<handlers::SuccessSuggestsEventResponse>(actual).suggest_buttons);
  EXPECT_EQ(true,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).terminal);
}

TEST(ResponseBuilder, SwitchChatToChatterbox) {
  ResponseBuildingData response_building_data{std::nullopt, std::nullopt, false,
                                              true};
  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuilder response_builder{metrics_};
  auto actual = response_builder.BuildResponse(response_building_data,
                                               callback_data, std::nullopt);
  // todo заполнить актуальной метой
  handlers::UnprocessableSuggestsEventResponseChatterboxMeta
      expected_chatterbox_meta{{}};
  EXPECT_EQ(expected_chatterbox_meta,
            std::get<handlers::UnprocessableSuggestsEventResponse>(actual)
                .chatterbox_meta);
}

TEST(ResponseBuilder, PrioritySwitchChatToChatterbox) {
  std::string message = "Сообщение";
  std::vector<handlers::SuggestButtonForResponse> suggest_buttons{
      handlers::SuggestButtonForResponse{"Саджест 1", {"suggest_1", "order_1"}},
      handlers::SuggestButtonForResponse{"Саджест 2", {"suggest_2", "order_2"}},
  };
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuildingData response_building_data{message, suggest_buttons, true,
                                              true};

  DummyResponseBuilderMetrics metrics_;
  ResponseBuilder response_builder{metrics_};
  auto actual = response_builder.BuildResponse(response_building_data,
                                               callback_data, std::nullopt);
  // todo заполнить актуальной метой
  handlers::UnprocessableSuggestsEventResponseChatterboxMeta
      expected_chatterbox_meta{{}};
  EXPECT_EQ(expected_chatterbox_meta,
            std::get<handlers::UnprocessableSuggestsEventResponse>(actual)
                .chatterbox_meta);
}

TEST(ResponseBuilder, PriorityMessageWithSuggests) {
  std::string message = "Сообщение";
  std::vector<handlers::SuggestButtonForResponse> suggest_buttons{
      handlers::SuggestButtonForResponse{"Саджест 1", {"suggest_1", "order_1"}},
      handlers::SuggestButtonForResponse{"Саджест 2", {"suggest_2", "order_2"}},
  };
  ResponseBuildingData response_building_data{message, suggest_buttons, true,
                                              false};

  DummyResponseBuilderMetrics metrics_;
  std::optional<::handlers::SuggestPayload> callback_data;
  ResponseBuilder response_builder{metrics_};
  auto actual = response_builder.BuildResponse(response_building_data,
                                               callback_data, std::nullopt);
  EXPECT_EQ(message,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).text);
  EXPECT_EQ(
      suggest_buttons,
      std::get<handlers::SuccessSuggestsEventResponse>(actual).suggest_buttons);
  EXPECT_EQ(false,
            std::get<handlers::SuccessSuggestsEventResponse>(actual).terminal);
}
