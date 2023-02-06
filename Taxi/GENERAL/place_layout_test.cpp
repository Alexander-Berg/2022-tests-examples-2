#include "place_layout.hpp"

#include <gtest/gtest.h>

#include <set>

#include <fmt/format.h>

#include <userver/formats/json.hpp>

namespace place_layout = eats_layout_constructor::meta_widgets::place_layout;
namespace extenders = eats_layout_constructor::extenders;

namespace {

void CheckArrayElementsType(const formats::json::Value& data_array,
                            const std::vector<std::string> correct_types) {
  ASSERT_EQ(data_array.GetSize(), correct_types.size());
  for (auto i = 0u; i < data_array.GetSize(); ++i) {
    ASSERT_EQ(data_array[i]["type"].As<std::string>(), correct_types[i]);
  }
}
}  // namespace

namespace eats_layout_constructor::meta_widgets {

TEST(PlaceLayout, GetAllExtenders) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 5;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 5;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto extenders = place_layout.GetExtenders();
  std::set<std::string> extenders_set(extenders.begin(), extenders.end());
  ASSERT_EQ(extenders_set.size(), 8u);
  ASSERT_EQ(extenders_set.count("actions_review"), 1);
  ASSERT_EQ(extenders_set.count("actions_info"), 1);
  ASSERT_EQ(extenders_set.count("actions_promo"), 1);
  ASSERT_EQ(extenders_set.count("actions_badge_extender"), 1);
  ASSERT_EQ(extenders_set.count("meta_rating"), 1);
  ASSERT_EQ(extenders_set.count("meta_price_category"), 1);
  ASSERT_EQ(extenders_set.count("meta_info"), 1);
  ASSERT_EQ(extenders_set.count("hero_photo_changer"), 1);
}

TEST(PlaceLayout, OrderExisting) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 5;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 5;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};
  std::vector<std::string> action_types = {"review", "info", "promo"};
  std::vector<std::string> meta_types = {"rating", "price_category", "info"};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo"}},
      {"id": "actions_2", "type": "review", "payload":{"some": "actions_review"}},
      {"id": "actions_3", "type": "info", "payload":{"some": "actions_info"}}
    ],
    "meta": [
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info"}},
      {"id": "meta_2", "type": "rating", "payload":{"some": "meta_rating"}},
      {"id": "meta_3", "type": "price_category", "payload":{"some": "meta_price_category"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_1", "type": "info"},
         {"id": "meta_2", "type": "rating"},
         {"id": "meta_3", "type": "price_category"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "review"},
         {"id": "actions_3", "type": "info"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  ASSERT_EQ(extended_places.size(), 1u);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  CheckArrayElementsType(place["data"]["actions"], action_types);
  ASSERT_TRUE(place["data"].HasMember("meta"));
  CheckArrayElementsType(place["data"]["meta"], meta_types);

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 2u);
  for (auto i = 0u; i < place["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][i]["type"].As<std::string>(),
              place_layout::ToString(settings.order[i]));
    CheckArrayElementsType(place["layout"][i]["layout"],
                           settings.order[i] == place_layout::OrderA::kMeta
                               ? meta_types
                               : action_types);
  }
}

TEST(PlaceLayout, ExtendExisting) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 5;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 5;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};

  std::vector<std::string> action_types = {"review", "info", "promo"};
  std::vector<std::string> meta_types = {"rating", "price_category", "info"};

  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo"}},
      {"id": "actions_2", "type": "review", "payload":{"some": "actions_review"}}
    ],
    "meta": [
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info"}},
      {"id": "meta_2", "type": "rating", "payload":{"some": "meta_rating"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_1", "type": "info"},
         {"id": "meta_2", "type": "rating"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "review"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  std::vector<extenders::ExtensionResponse> extenders;
  extenders::ExtensionResponse action_info;
  action_info.extension_type = extenders::ExtensionType("actions_info");
  action_info.requester_id = extenders::RequesterId("widget_id");
  action_info.extensions[extenders::Id(123)] =
      place_layout::GetExistingFieldExtender(formats::json::FromString(R"=(
{
  "id": "actions_3",
  "type": "info",
  "payload": {
    "some": "actions_info"
  }
})="),
                                             place_layout::OrderA::kActions);
  extenders.push_back(action_info);

  extenders::ExtensionResponse meta_price_category;
  meta_price_category.extension_type =
      extenders::ExtensionType("meta_price_category");
  meta_price_category.requester_id = extenders::RequesterId("widget_id");
  meta_price_category.extensions[extenders::Id(123)] =
      place_layout::GetExistingFieldExtender(formats::json::FromString(
                                                 R"=(
{
  "id": "meta_3",
  "type": "price_category",
  "payload": {
    "some": "meta_price_category"
  }
})="),
                                             place_layout::OrderA::kMeta);
  extenders.push_back(meta_price_category);

  auto extended_places = place_layout.ProcessExtenders(extenders, places);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  CheckArrayElementsType(place["data"]["actions"], action_types);
  ASSERT_TRUE(place["data"].HasMember("meta"));
  CheckArrayElementsType(place["data"]["meta"], meta_types);

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 2u);
  for (auto i = 0u; i < place["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][i]["type"].As<std::string>(),
              place_layout::ToString(settings.order[i]));
    CheckArrayElementsType(place["layout"][i]["layout"],
                           settings.order[i] == place_layout::OrderA::kMeta
                               ? meta_types
                               : action_types);
  }
}

TEST(PlaceLayout, LeftOnlyNeeded) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 5;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 5;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};

  std::vector<std::string> action_types = {"info", "promo"};
  std::vector<std::string> meta_types = {"price_category", "info"};

  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo"}},
      {"id": "actions_2", "type": "review", "payload":{"some": "actions_review"}}
    ],
    "meta": [
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info"}},
      {"id": "meta_2", "type": "rating", "payload":{"some": "meta_rating"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_1", "type": "info"},
         {"id": "meta_2", "type": "rating"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "review"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  std::vector<extenders::ExtensionResponse> extenders;
  extenders::ExtensionResponse action_info;
  action_info.extension_type = extenders::ExtensionType("actions_info");
  action_info.requester_id = extenders::RequesterId("widget_id");
  action_info.extensions[extenders::Id(123)] =
      place_layout::GetExistingFieldExtender(formats::json::FromString(R"=(
{
  "id": "actions_3",
  "type": "info",
  "payload": {
    "some": "actions_info"
  }
})="),
                                             place_layout::OrderA::kActions);
  extenders.push_back(action_info);

  extenders::ExtensionResponse meta_price_category;
  meta_price_category.extension_type =
      extenders::ExtensionType("meta_price_category");
  meta_price_category.requester_id = extenders::RequesterId("widget_id");
  meta_price_category.extensions[extenders::Id(123)] =
      place_layout::GetExistingFieldExtender(formats::json::FromString(
                                                 R"=(
{
  "id": "meta_3",
  "type": "price_category",
  "payload": {
    "some": "meta_price_category"
  }
})="),
                                             place_layout::OrderA::kMeta);
  extenders.push_back(meta_price_category);

  auto extended_places = place_layout.ProcessExtenders(extenders, places);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  CheckArrayElementsType(place["data"]["actions"], action_types);
  ASSERT_TRUE(place["data"].HasMember("meta"));
  CheckArrayElementsType(place["data"]["meta"], meta_types);

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 2u);
  for (auto i = 0u; i < place["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][i]["type"].As<std::string>(),
              place_layout::ToString(settings.order[i]));
    CheckArrayElementsType(place["layout"][i]["layout"],
                           settings.order[i] == place_layout::OrderA::kMeta
                               ? meta_types
                               : action_types);
  }
}

TEST(PlaceLayout, MaxCount) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 1;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 2;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};
  std::vector<std::string> action_types = {"review"};
  std::vector<std::string> meta_types = {"rating", "price_category"};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo"}},
      {"id": "actions_2", "type": "review", "payload":{"some": "actions_review"}},
      {"id": "actions_3", "type": "info", "payload":{"some": "actions_info"}}
    ],
    "meta": [
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info"}},
      {"id": "meta_2", "type": "rating", "payload":{"some": "meta_rating"}},
      {"id": "meta_3", "type": "price_category", "payload":{"some": "meta_price_category"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_1", "type": "info"},
         {"id": "meta_2", "type": "rating"},
         {"id": "meta_3", "type": "price_category"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "review"},
         {"id": "actions_3", "type": "info"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  CheckArrayElementsType(place["data"]["actions"], action_types);
  ASSERT_TRUE(place["data"].HasMember("meta"));
  CheckArrayElementsType(place["data"]["meta"], meta_types);

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 2u);
  for (auto i = 0u; i < place["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][i]["type"].As<std::string>(),
              place_layout::ToString(settings.order[i]));
    CheckArrayElementsType(place["layout"][i]["layout"],
                           settings.order[i] == place_layout::OrderA::kMeta
                               ? meta_types
                               : action_types);
  }
}

TEST(PlaceLayout, RemoveField) {
  place_layout::Settings settings;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 3;
  settings.order = {place_layout::OrderA::kMeta};
  std::vector<std::string> meta_types = {"rating", "price_category", "info"};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo"}},
      {"id": "actions_2", "type": "review", "payload":{"some": "actions_review"}},
      {"id": "actions_3", "type": "info", "payload":{"some": "actions_info"}}
    ],
    "meta": [
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info"}},
      {"id": "meta_2", "type": "rating", "payload":{"some": "meta_rating"}},
      {"id": "meta_3", "type": "price_category", "payload":{"some": "meta_price_category"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_1", "type": "info"},
         {"id": "meta_2", "type": "rating"},
         {"id": "meta_3", "type": "price_category"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "review"},
         {"id": "actions_3", "type": "info"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_FALSE(place["data"].HasMember("actions"));
  ASSERT_TRUE(place["data"].HasMember("meta"));
  CheckArrayElementsType(place["data"]["meta"], meta_types);

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 1u);
  ASSERT_EQ(place["layout"][0]["type"].As<std::string>(),
            place_layout::ToString(settings.order[0]));
  CheckArrayElementsType(place["layout"][0]["layout"], meta_types);
}

TEST(PlaceLayout, MultiSameTypeAll) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 5;
  settings.meta_extenders = {place_layout::MetaextendersA::kMetaRating,
                             place_layout::MetaextendersA::kMetaPriceCategory,
                             place_layout::MetaextendersA::kMetaInfo};
  settings.max_meta_count = 5;
  settings.order = {place_layout::OrderA::kActions,
                    place_layout::OrderA::kMeta};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_0", "type": "promo", "payload":{"some": "actions_promo_0"}},
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo_1"}},
      {"id": "actions_2", "type": "promo", "payload":{"some": "actions_promo_2"}}
    ],
    "meta": [
      {"id": "meta_0", "type": "info", "payload":{"some": "meta_info_0"}},
      {"id": "meta_1", "type": "info", "payload":{"some": "meta_info_1"}}
    ]
  },
  "layout": [
    {
      "type": "meta",
      "layout": [
         {"id": "meta_0", "type": "info"},
         {"id": "meta_1", "type": "info"}
      ]
    },
    {
      "type": "action",
      "layout": [
         {"id": "actions_0", "type": "promo"},
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "promo"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  ASSERT_EQ(extended_places.size(), 1u);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  const auto& actions = place["data"]["actions"];
  ASSERT_EQ(actions.GetSize(), 3);
  for (auto i = 0u; i < actions.GetSize(); ++i) {
    ASSERT_EQ(actions[i]["type"].As<std::string>(), "promo");
    ASSERT_EQ(actions[i]["id"].As<std::string>(), fmt::format("actions_{}", i));
    ASSERT_EQ(actions[i]["payload"]["some"].As<std::string>(),
              fmt::format("actions_promo_{}", i));
  }
  ASSERT_TRUE(place["data"].HasMember("meta"));

  const auto& meta = place["data"]["meta"];
  ASSERT_EQ(meta.GetSize(), 2);
  for (auto i = 0u; i < meta.GetSize(); ++i) {
    ASSERT_EQ(meta[i]["type"].As<std::string>(), "info");
    ASSERT_EQ(meta[i]["id"].As<std::string>(), fmt::format("meta_{}", i));
    ASSERT_EQ(meta[i]["payload"]["some"].As<std::string>(),
              fmt::format("meta_info_{}", i));
  }

  ASSERT_TRUE(place.HasMember("layout"));
  ASSERT_EQ(place["layout"].GetSize(), 2u);
  ASSERT_EQ(place["layout"][0]["type"].As<std::string>(), "actions");
  for (auto i = 0u; i < place["layout"][0]["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][0]["layout"][i]["type"].As<std::string>(),
              "promo");
    ASSERT_EQ(place["layout"][0]["layout"][i]["id"].As<std::string>(),
              fmt::format("actions_{}", i));
  }

  ASSERT_EQ(place["layout"][1]["type"].As<std::string>(), "meta");
  for (auto i = 0u; i < place["layout"][1]["layout"].GetSize(); ++i) {
    ASSERT_EQ(place["layout"][1]["layout"][i]["type"].As<std::string>(),
              "info");
    ASSERT_EQ(place["layout"][1]["layout"][i]["id"].As<std::string>(),
              fmt::format("meta_{}", i));
  }
}

TEST(PlaceLayout, MultiSameTypeLimitCount) {
  place_layout::Settings settings;
  settings.action_extenders = {place_layout::ActionextendersA::kActionsReview,
                               place_layout::ActionextendersA::kActionsInfo,
                               place_layout::ActionextendersA::kActionsPromo};
  settings.max_actions_count = 2;
  settings.meta_extenders = {};
  settings.max_meta_count = 0;
  settings.order = {place_layout::OrderA::kActions};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_0", "type": "promo", "payload":{"some": "actions_promo_0"}},
      {"id": "actions_1", "type": "promo", "payload":{"some": "actions_promo_1"}},
      {"id": "actions_2", "type": "promo", "payload":{"some": "actions_promo_2"}},
      {"id": "actions_3", "type": "review", "payload":{"some": "actions_review"}}
    ]
  },
  "layout": [
    {
      "type": "action",
      "layout": [
         {"id": "actions_0", "type": "promo"},
         {"id": "actions_1", "type": "promo"},
         {"id": "actions_2", "type": "promo"},
         {"id": "actions_3", "type": "review"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  ASSERT_EQ(extended_places.size(), 1u);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  const auto& actions = place["data"]["actions"];
  ASSERT_EQ(actions.GetSize(), 2);
  ASSERT_EQ(actions[0]["type"].As<std::string>(), "review");
  ASSERT_EQ(actions[1]["type"].As<std::string>(), "promo");
}

TEST(PlaceLayout, SpecialProjectAction) {
  // Проверяем, что мета виджет умеет перекладывать
  // экшон с типом special_project

  place_layout::Settings settings{};
  settings.action_extenders = {
      place_layout::ActionextendersA::kActionsSpecialProject};
  settings.max_actions_count = 1;
  settings.order = {place_layout::OrderA::kActions};
  auto place_layout = meta_widgets::PlaceLayout(
      settings, models::constructor::MetaWidgetSlug{""});
  auto place_str =
      R"=(
{
  "data": {
    "actions": [
      {"id": "actions_0", "type": "special_project", "payload":{"some": "actions_special_project_0"}}
    ]
  },
  "layout": [
    {
      "type": "action",
      "layout": [
         {"id": "actions_0", "type": "special_project"}
      ]
    }
  ]
}
)=";
  std::unordered_map<int, formats::json::Value> places{
      {123, formats::json::FromString(place_str)}};
  auto extended_places = place_layout.ProcessExtenders({}, places);
  ASSERT_EQ(extended_places.size(), 1u);
  auto place = extended_places[123];
  ASSERT_TRUE(place.HasMember("data"));
  ASSERT_TRUE(place["data"].HasMember("actions"));
  const auto& actions = place["data"]["actions"];
  ASSERT_EQ(actions.GetSize(), 1);
  ASSERT_EQ(actions[0]["type"].As<std::string>(), "special_project");
  ASSERT_EQ(actions[0]["payload"]["some"].As<std::string>(),
            "actions_special_project_0");
}

}  // namespace eats_layout_constructor::meta_widgets
