#include <endpoints/full/plugins/verticals/common/verticals_serializable.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::verticals {

TariffVertical MockTariffVertical() {
  TariffVertical result;
  result.tariff = Tariff{"econom"};
  return result;
}

MulticlassInfo MockMulticlass() {
  MulticlassInfo result;
  result.tariffs = {MulticlassTariff{"vip", true},
                    MulticlassTariff{"maybach", false}};
  result.position = 2;
  result.name = "The fastest";

  result.details.description.title = "Multiple classes";
  result.details.description.subtitle = "The nearest car will pick you up";
  result.details.order_button.text = "Order";
  result.details.price = "from 500 rub";
  result.details.search_screen.title = "Search";
  result.details.search_screen.subtitle = "in multiple classes";

  result.selection_rules.min_selected_count.text = "Min classes selected";
  result.selection_rules.min_selected_count.value = 2;

  result.estimated_waiting = MulticlassEstimatedWaiting{"1 min", 60};

  result.tariff_unavailable = TariffUnavailable{
      "multiclass_preorder_unavailable", "Unavailable by preorder"};
  return result;
}

GroupVertical MockGroupVertical(const bool has_multiclass) {
  GroupVertical result;
  result.core.id = "ultima";
  result.default_tariff = "vip";
  result.formatted_price = "500 rub";
  result.core.tariffs = {Tariff{"vip", true}, Tariff{"maybach"}};

  if (has_multiclass) {
    result.multiclass_info = MockMulticlass();
  }
  return result;
}

TEST(VerticalsSerializable, Empty) {
  std::vector<Vertical> verticals{};

  const auto& serializable = VerticalsSerializable(
      verticals,
      {handlers::RoutestatsResponseVerticalsmodesA::kVerticalsSelector});
  handlers::RoutestatsResponse response;
  plugins::common::ResultWrapper<handlers::RoutestatsResponse> wrapper(
      response);
  serializable.SerializeInPlace(wrapper);

  if (response.verticals) {
    const auto& result_verticals = *response.verticals;
    ASSERT_TRUE(result_verticals.empty());
  }

  if (response.verticals_modes) {
    const auto& result_modes = *response.verticals_modes;
    ASSERT_TRUE(result_modes.empty());
  }
}

TEST(VerticalsSerializable, OkWithoutMulticlass) {
  std::vector<Vertical> verticals{
      MockTariffVertical(),
      MockGroupVertical(false /*has_multiclass*/),
  };

  const auto& serializable = VerticalsSerializable(
      verticals,
      {handlers::RoutestatsResponseVerticalsmodesA::kVerticalsSelector});
  handlers::RoutestatsResponse response;
  plugins::common::ResultWrapper<handlers::RoutestatsResponse> wrapper(
      response);
  serializable.SerializeInPlace(wrapper);

  const auto& result_verticals = *response.verticals;
  ASSERT_EQ(result_verticals.size(), 2);

  using formats::json::FromString;
  using formats::json::ValueBuilder;
  ASSERT_EQ(ValueBuilder(result_verticals.at(0)).ExtractValue(), FromString(R"({
            "type": "tariff",
            "class": "econom"})"));

  ASSERT_EQ(ValueBuilder(result_verticals.at(1)).ExtractValue(), FromString(R"({
             "type": "group",
             "id": "ultima",
             "price": "500 rub",
             "default_tariff": "vip",
             "tariffs": [
                {
                    "class": "vip",
                    "use_tariff_title_on_vertical_name": true
                },
                {
                    "class": "maybach"
                }
            ]})"));

  const auto& result_modes = *response.verticals_modes;
  ASSERT_EQ(result_modes.size(), 1);
  ASSERT_EQ(result_modes.at(0),
            handlers::RoutestatsResponseVerticalsmodesA::kVerticalsSelector);
}

TEST(VerticalsSerializable, OkWithMulticlass) {
  std::vector<Vertical> verticals{
      MockTariffVertical(),
      MockGroupVertical(true /*has_multiclass*/),
  };

  const auto& serializable = VerticalsSerializable(
      verticals,
      {handlers::RoutestatsResponseVerticalsmodesA::kVerticalsSelector});
  handlers::RoutestatsResponse response;
  plugins::common::ResultWrapper<handlers::RoutestatsResponse> wrapper(
      response);
  serializable.SerializeInPlace(wrapper);

  const auto& result_verticals = *response.verticals;
  ASSERT_EQ(result_verticals.size(), 2);

  using formats::json::FromString;
  using formats::json::ValueBuilder;
  ASSERT_EQ(ValueBuilder(result_verticals.at(0)).ExtractValue(), FromString(R"({
            "type": "tariff",
            "class": "econom"})"));

  ASSERT_EQ(ValueBuilder(result_verticals.at(1)).ExtractValue(), FromString(R"({
             "type": "group",
             "id": "ultima",
             "price": "500 rub",
             "default_tariff": "vip",
             "tariffs": [
                {
                    "class": "vip",
                    "use_tariff_title_on_vertical_name": true
                },
                {
                    "class": "maybach"
                }
            ],
            "multiclass": {
              "tariffs": [{"tariff": "vip","selected": true}, {"tariff": "maybach","selected": false}],
              "position": 2,
              "name": "The fastest",
              "details": {
                "description": {"title": "Multiple classes", "subtitle": "The nearest car will pick you up"},
                "price": "from 500 rub",
                "order_button": {"text": "Order"},
                "search_screen": {"title": "Search", "subtitle": "in multiple classes"}
              },
              "selection_rules": {"min_selected_count": {"text": "Min classes selected", "value": 2}},
              "estimated_waiting": {"message": "1 min", "seconds": 60},
              "tariff_unavailable": {"code": "multiclass_preorder_unavailable", "message": "Unavailable by preorder"}
            }
            })"));

  const auto& result_modes = *response.verticals_modes;
  ASSERT_EQ(result_modes.size(), 1);
  ASSERT_EQ(result_modes.at(0),
            handlers::RoutestatsResponseVerticalsmodesA::kVerticalsSelector);
}
}  // namespace routestats::plugins::verticals
