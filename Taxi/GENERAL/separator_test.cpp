#include "separator.hpp"

#include <gtest/gtest.h>
#include <widgets/separator/factory.hpp>

namespace {

namespace separator = eats_layout_constructor::widgets::separator;
using Response = eats_layout_constructor::sources::DataSourceResponses;

struct TestParams {
  std::unordered_set<std::string> depends_on_ids;
  std::unordered_set<std::string> master_ids;
};

struct SeparatorExistsTest : public ::testing::TestWithParam<TestParams> {};
struct SeparatorNotExistsTest : public ::testing::TestWithParam<TestParams> {};

std::vector<TestParams> kSeparatorExistsParams{
    {{"widget_1"}, {"widget_1", "widget_2", "widget_3"}},
    {{"widget_2"}, {"widget_1", "widget_2", "widget_3"}},
    {{"widget_3"}, {"widget_1", "widget_2", "widget_3"}},
    {{"widget_1", "widget_2", "widget_3"}, {"widget_1"}},
    {{"widget_1", "widget_2", "widget_3"}, {"widget_2"}},
    {{"widget_1", "widget_2", "widget_3"}, {"widget_3"}}};

std::vector<TestParams> kSeparatorNotExistsParams{
    {{"widget_3"}, {}},
    {{"widget_3"}, {"widget_1"}},
    {{"widget_4"}, {"widget_1", "widget_2", "widget_3"}},
    {{"widget_1", "widget_2", "widget_3"}, {"widget_4"}}};

formats::json::Value GetWidgetData(
    const std::string& id,
    const std::unordered_set<std::string>& depends_on_any) {
  formats::json::ValueBuilder widget;
  widget["id"] = id;
  widget["type"] = "separator";
  widget["payload"] = {};
  widget["meta"]["depends_on_any"] = depends_on_any;

  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id,
    const std::unordered_set<std::string>& depends_on_any) {
  const auto widget_data = GetWidgetData(id, depends_on_any);

  return eats_layout_constructor::widgets::separator::SeparatorFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

TEST(Separator, Smoke) {
  std::unordered_set<std::string> master_widgets_ids{"master"};
  auto separator = GetWidget("id_1", master_widgets_ids);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(separator->HasData());
  separator->FilterWidgetsWithData(master_widgets_ids);
  EXPECT_TRUE(separator->HasData());

  separator->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["separators"].GetSize(), 1);

  auto separators = json_response["data"]["separators"];
  EXPECT_TRUE(separators[0].HasMember("payload"));
  EXPECT_TRUE(separators[0]["payload"].IsObject());
  EXPECT_TRUE(separators[0]["payload"].IsEmpty());
}

TEST_P(SeparatorExistsTest, DependsOnExists) {
  const auto& depends_on_ids = GetParam().depends_on_ids;
  const auto& master_ids = GetParam().master_ids;

  auto separator = GetWidget("id_1", depends_on_ids);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(separator->HasData());
  separator->FilterWidgetsWithData(master_ids);
  EXPECT_TRUE(separator->HasData());

  separator->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["separators"].GetSize(), 1);
}

INSTANTIATE_TEST_SUITE_P(Separator, SeparatorExistsTest,
                         testing::ValuesIn(kSeparatorExistsParams));

TEST_P(SeparatorNotExistsTest, DependsOnNotExists) {
  const auto& depends_on_ids = GetParam().depends_on_ids;
  const auto& master_ids = GetParam().master_ids;

  auto separator = GetWidget("id_1", depends_on_ids);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(separator->HasData());
  separator->FilterWidgetsWithData(master_ids);
  EXPECT_FALSE(separator->HasData());
}

INSTANTIATE_TEST_SUITE_P(Separator, SeparatorNotExistsTest,
                         testing::ValuesIn(kSeparatorNotExistsParams));

}  // namespace
