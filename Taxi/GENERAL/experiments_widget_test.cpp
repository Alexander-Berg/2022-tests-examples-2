#include "experiments_widget.hpp"

#include <gtest/gtest.h>

#include <userver/formats/json/value_builder.hpp>
#include <widgets/experiments_widget/factory.hpp>

namespace {

using DataSourceResponses =
    eats_layout_constructor::sources::DataSourceResponses;
using ExperimentResult = experiments3::models::ExperimentResult;
using Experiments = std::vector<ExperimentResult>;

struct WidgetConfig {
  // Идентификатор виджета - произвольная строка.
  std::string id = "";
  // Заголовок виджета передаваемый на фронтенд,
  std::string title = "";
  // Уникальное id эксперимента (название).
  std::string exp_name = "";
};

ExperimentResult CreateExpResult(const std::string exp_name,
                                 const std::string type = "some_type",
                                 bool add_payload = true,
                                 bool object_payload = true) {
  ExperimentResult result;
  result.name = exp_name;
  formats::json::ValueBuilder value;
  value["id"] = "some_id";
  value["title"] = "some_title";
  if (type == "inv-type")
    value["type"] = 1;
  else if (type != "non-type")
    value["type"] = type;
  if (add_payload) {
    if (object_payload) {
      value["payload"]["smth"] = "smth";
    } else {
      value["payload"] = "some string, not object";
    }
  }
  result.value = value.ExtractValue();
  return result;
}

// Возвращает данные виджетов с требуемыми настройками
std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> CreateWidget(
    const WidgetConfig& config) {
  formats::json::Value widget_data;
  {
    formats::json::ValueBuilder widget_builder;

    widget_builder["id"] = config.id;
    widget_builder["payload"]["title"] = config.title;
    widget_builder["meta"]["exp_name"] = config.exp_name;

    widget_data = widget_builder.ExtractValue();
  }
  return eats_layout_constructor::widgets::experiments_widget::
      ExperimentsWidgetFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          eats_layout_constructor::models::constructor::Meta{
              widget_data["meta"]},
          eats_layout_constructor::models::constructor::Payload{
              widget_data["payload"]},
          {}, widget_data["id"].As<std::string>());
}

}  // namespace

// Тестирует, что виджет берет нужные данные из даты всех экспериментов
TEST(Experiments_widget, Simple) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult(exp_name);
  auto exp_result2 = CreateExpResult("not_our_widget_id");

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_FALSE(json_response.IsEmpty());

  ASSERT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["payload"]["title"].As<std::string>(),
            widget_title);
  ASSERT_EQ(json_response["layout"][0]["type"].As<std::string>(), "some_type");
}

// Тестирует, что виджет ничего не берет, если нет нужныого эксперимента
TEST(Experiments_widget, NotExperiment) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult("not_our_widget_id2");

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}

// Тестирует, что виджет ничего не берет, если нет "type" в результате
// эксперимента
TEST(Experiments_widget, NoType) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult(exp_name, "non-type");

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}

// Тестирует, что виджет ничего не берет, если поле "type" в результате
// эксперимента не является строкой
TEST(Experiments_widget, TypeIsNotString) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult(exp_name, "inv-type");

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}

// Тестирует, что виджет ничего не берет, если "type" пустой в результате
// эксперимента
TEST(Experiments_widget, EmptyType) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult(exp_name, "");

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}

// Тестирует, что виджет ничего не берет, если нет поля "payload" в результате
// эксперимента
TEST(Experiments_widget, NoPayload) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult(exp_name, "type", false, true);

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);
  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}

// Тестирует, что виджет ничего не берет, если полe "payload" не является
// объектом
TEST(Experiments_widget, PayloadIsNotObject) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";
  const std::string exp_name = "exp_fake_id";

  namespace widgets = eats_layout_constructor::widgets;
  // Создаем виджет
  auto exp_widget = CreateWidget({widget_id, widget_title, exp_name});

  auto exp_result1 = CreateExpResult("not_our_widget_id1");
  auto exp_result2 = CreateExpResult(exp_name, "type", true, false);

  Experiments exp_data = {exp_result1, exp_result2};

  formats::json::ValueBuilder response;

  exp_widget->SetExperiments(exp_data);

  exp_widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response.IsEmpty());
}
