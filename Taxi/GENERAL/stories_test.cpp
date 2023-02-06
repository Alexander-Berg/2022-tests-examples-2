#include "stories.hpp"

#include <gtest/gtest.h>

#include <sources/eats-communications/eats_communications_source.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <widgets/stories/factory.hpp>

namespace {

using Response = eats_layout_constructor::sources::DataSourceResponses;

// Возвращает тестовый ответ ручки коммуникаций, для тестов виджета.
// NOTE: фyнкция не возвращает ответ, который соответсвуют ограничениям
//  указанным в спецификации сервиса eats-communications.
Response CreateDataSourceResposne(int stories_count) {
  static auto kResponse = Response{};
  using Communications =
      eats_layout_constructor::sources::eats_communications::DataSource;

  auto response = Response{};
  auto communications_response = std::make_shared<Communications::Response>();

  for (int i = 1; i <= stories_count; i++) {
    formats::json::ValueBuilder payload;
    payload["offer"]["shortcut_id"] = std::to_string(i);
    payload["offer"]["title"]["color"] = "000000";
    payload["offer"]["title"]["content"] = "Story " + std::to_string(i);

    eats_layout_constructor::sources::eats_communications::StoryData item;
    item.payload = payload.ExtractValue();

    communications_response->stories.push_back(item);
  }

  response[Communications::kName] = communications_response;

  return response;
}

// Возвращает тестовый ответ ручки коммуникаций, со сторизами содержащими
// метаданные переданные в аргумнете, в том же порядке.
// NOTE: фyнкция не возвращает ответ, который соответсвуют ограничениям
//  указанным в спецификации сервиса eats-communications.
Response CreateDataSourceResposneFromMetas(
    std::vector<
        eats_layout_constructor::sources::eats_communications::StoryMeta>
        metas) {
  static auto kResponse = Response{};
  using Communications =
      eats_layout_constructor::sources::eats_communications::DataSource;

  auto response = Response{};
  auto communications_response =
      std::make_shared<Communications::Response>(Communications::Response{});

  for (size_t i = 1; i <= metas.size(); i++) {
    formats::json::ValueBuilder payload;
    payload["offer"]["shortcut_id"] = std::to_string(i);
    payload["offer"]["title"]["color"] = "000000";
    payload["offer"]["title"]["content"] = "Story " + std::to_string(i);

    eats_layout_constructor::sources::eats_communications::StoryData item;
    item.meta = metas.at(i - 1);
    item.payload = payload.ExtractValue();

    communications_response->stories.push_back(item);
  }

  response[Communications::kName] = communications_response;

  return response;
}

struct WidgetConfig {
  // Идентификатор виджета - произвольная строка.
  std::string id = "";
  // Заголовок виджета передаваемый на фронтенд,
  std::string title = "";
  // Минимальное количество сторизов для отображения виджета.
  std::optional<int> min_count = std::nullopt;
  // Максимальное количество сторизов виджете.
  std::optional<int> limit = std::nullopt;
  // Группы сторизов, которые необходимо поместить в виджет
  std::vector<std::string> groups = {};
};

// Возвращает данные виджет сторизов с требуемыми настройками
std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> CreateWidget(
    const WidgetConfig& config) {
  formats::json::Value widget_data;
  {
    formats::json::ValueBuilder widget_builder;

    widget_builder["id"] = config.id;
    widget_builder["payload"]["title"] = config.title;
    widget_builder["meta"]["min_count"] = config.min_count;
    widget_builder["meta"]["limit"] = config.limit;
    widget_builder["meta"]["groups"] = config.groups;

    widget_data = widget_builder.ExtractValue();
  }
  return eats_layout_constructor::widgets::stories::StoriesFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

}  // namespace

// Тестирует, что в случае получения из источника данных произвольного
// количества сторизов без указания лимита и минимального кличества сторизов в
// ответе будет один элемент в layout, один элемент в data и N элментов в
// data.stories, где N == количеству сторизов, которые вернул источник данных.
TEST(Stories, Simple) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto stories_widget = CreateWidget({widget_id, widget_title});
  // Создаем фейковый ответ eats-communications
  auto source = CreateDataSourceResposne(10);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(stories_widget->HasData());
  stories_widget->FilterSourceResponse(source);
  EXPECT_TRUE(stories_widget->HasData());

  stories_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_FALSE(json_response["layout"].IsMissing());

  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(), "stories");
  EXPECT_EQ(json_response["layout"][0]["payload"]["title"].As<std::string>(),
            widget_title);

  {
    auto stories_data = json_response["data"]["stories"];
    EXPECT_EQ(stories_data.GetSize(), 1);
    EXPECT_EQ(stories_data[0]["payload"]["stories"].GetSize(), 10);
  }
  {
    auto story = json_response["data"]["stories"][0];
    EXPECT_EQ(story["id"].As<std::string>(), widget_id);
  }
}

// Тестирует, что в ответ будут попадать только сторизы с группами переданными в
// настройках виджета.
TEST(Stories, FilterByGroup) {
  using Meta = eats_layout_constructor::sources::eats_communications::StoryMeta;
  using Group = eats_layout_constructor::sources::eats_communications::Group;

  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";

  namespace widgets = eats_layout_constructor::widgets;
  WidgetConfig config;
  config.id = widget_id;
  config.title = widget_title;
  config.groups = {"group2"};
  config.limit = 2;
  // Создаем виджет
  auto stories_widget = CreateWidget(config);
  // Создаем фейковый ответ eats-communications
  auto source = CreateDataSourceResposneFromMetas({
      // Story 1 - должен попасть в ответ.
      Meta{
          {Group("group1"), Group("group2"), Group("group3")},  // groups
      },
      // Story 2 - должен быть отфильтрован по группе.
      Meta{
          {Group("group4")},  // groups
      },
      // Story 3 - должен попасть в ответ.
      Meta{
          {Group("group1"), Group("group2")},  // groups
      },
      // Story 4 - должен быть отфильтрован лимитом.
      Meta{
          {Group("group2")},  // groups
      },
  });

  formats::json::ValueBuilder response;

  EXPECT_FALSE(stories_widget->HasData());
  stories_widget->FilterSourceResponse(source);
  EXPECT_TRUE(stories_widget->HasData());

  stories_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_FALSE(json_response["layout"].IsMissing());

  ASSERT_EQ(json_response["layout"].GetSize(), 1);
  ASSERT_EQ(json_response["layout"][0]["type"].As<std::string>(), "stories");
  EXPECT_EQ(json_response["layout"][0]["payload"]["title"].As<std::string>(),
            widget_title);

  {
    auto stories_data = json_response["data"]["stories"];
    EXPECT_EQ(stories_data.GetSize(), 1);
    ASSERT_EQ(stories_data[0]["payload"]["stories"].GetSize(), 2);

    auto expected_titles = std::vector<std::string>{"Story 1", "Story 3"};
    for (size_t i = 0; i < expected_titles.size(); i++) {
      auto story_offer = stories_data[0]["payload"]["stories"][i]["offer"];

      ASSERT_FALSE(story_offer.IsMissing());
      ASSERT_TRUE(story_offer.IsObject());
      EXPECT_EQ(story_offer["title"]["content"].As<std::string>(),
                expected_titles.at(i));
    }
  }
}
