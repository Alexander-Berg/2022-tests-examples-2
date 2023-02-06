#include <clients/eats-core/client_gmock.hpp>
#include <testing/taxi_config.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

#include "components/dashboard_suggests.hpp"
#include "components/text_templater.hpp"
#include "models/places_units.hpp"
#include "types/place_ids.hpp"

namespace testing {

using PlaceId = eats_report_storage::types::PlaceId;

using namespace eats_report_storage::components;

std::vector<ConfigSuggestGroup> MakeSuggestsWithTemplate() {
  std::vector<ConfigSuggestGroup> data;
  const auto json_suggests =
      R"~(
{
  "groups": [
    {
      "group_slug": "group_1",
      "suggests": [
        {
          "suggest_slug": "low_rating",
          "icon_slug": "icon_slug",
          "section_slug": "section_slug_sel",
          "suggest_template_slug": "template:suggest_example_text",
          "suggest_text": {
            "text": "low_rating_text",
            "params": []
          },
          "title": "Title",
          "button_title": "BTN Title",
          "predicates": {
            "init": {
              "predicates": [
                {
                  "init": {
                    "value": 4,
                    "arg_name": "rating",
                    "arg_type": "double"
                  },
                  "type": "lt"
                }
              ]
            },
            "type": "any_of"
          }
        },
        {
          "suggest_slug": "more_photos",
          "icon_slug": "icon_slug",
          "section_slug": "section_slug_sel",
          "suggest_template_slug": "template:suggest_example_text_2",
          "suggest_text": {
            "text": "more_photos_text",
            "params": []
          },
          "title": "Title",
          "button_title": "BTN Title",
          "predicates": {
            "init": {
              "predicates": [
                {
                  "init": {
                    "value": 5.5,
                    "arg_name": "pict_share",
                    "arg_type": "double"
                  },
                  "type": "gt"
                }
              ]
            },
            "type": "any_of"
          }
        }
      ]
    }
  ]
}
)~";
  const auto json = formats::json::FromString(json_suggests);
  for (const auto& item : json["groups"]) {
    data.emplace_back(item.As<ConfigSuggestGroup>());
  }
  return data;
}

std::vector<ConfigSuggestGroup> MakeSuggestsWithIcon() {
  std::vector<ConfigSuggestGroup> data;
  const auto json_suggests =
      R"~(
{
  "groups": [
    {
      "group_slug": "group_1",
      "number_of_displays_in_group": 2,
      "suggests": [
        {
          "suggest_slug": "low_rating",
          "icon_slug": "icon_slug",
          "section_slug": "section_slug_sel",
          "suggest_text": {
            "text": "low_rating_text",
            "params": []
          },
          "title": "Title",
          "button_title": "BTN Title",
          "dynamic_icon": {
            "max_value": 3.7,
            "value_unit_sign": "Q",
            "local_value_unit": "currency",
            "symbols_after_comma": 2,
            "target": 4.3,
            "arg_name": "rating"
          },
          "predicates": {
            "init": {
              "predicates": [
                {
                  "init": {
                    "value": 4,
                    "arg_name": "rating",
                    "arg_type": "double"
                  },
                  "type": "lt"
                }
              ]
            },
            "type": "any_of"
          }
        },
        {
          "suggest_slug": "more_photos",
          "icon_slug": "icon_slug",
          "section_slug": "section_slug_sel",
          "suggest_text": {
            "text": "more_photos_text",
            "params": []
          },
          "dynamic_icon": {
            "max_value": 5.5,
            "value_unit_sign": "#",
            "local_value_unit": "currency",
            "symbols_after_comma": 2,
            "arg_name": "pict_share"
          },
          "title": "Title",
          "button_title": "BTN Title",
          "predicates": {
            "init": {
              "predicates": [
                {
                  "init": {
                    "value": 5.5,
                    "arg_name": "pict_share",
                    "arg_type": "double"
                  },
                  "type": "gt"
                }
              ]
            },
            "type": "any_of"
          }
        }
      ]
    }
  ]
}
)~";
  const auto json = formats::json::FromString(json_suggests);
  for (const auto& item : json["groups"]) {
    data.emplace_back(item.As<ConfigSuggestGroup>());
  }
  return data;
}

eats_report_storage::components::impl::ConfigTemplater MakeTemplatesEmpty() {
  const auto json_s =
      R"({
    "templates": []
})";
  const auto json = formats::json::FromString(json_s);
  return taxi_config::eats_report_storage_text_templater::Parse(
      json, formats::parse::To<
                eats_report_storage::components::impl::ConfigTemplater>());
}

eats_report_storage::components::impl::ConfigTemplater MakeTemplatesData() {
  const auto json_s =
      R"({
    "templates": [
{
    "slug": "suggest_example_text",
    "template": "Просто текст без параметров"
  },
{
    "slug": "suggest_example_text_2",
    "template": "Просто текст 2 без параметров"
  }
]
})";
  const auto json = formats::json::FromString(json_s);
  return taxi_config::eats_report_storage_text_templater::Parse(
      json, formats::parse::To<
                eats_report_storage::components::impl::ConfigTemplater>());
}

eats_report_storage::types::Suggest MakeResultWithParam(
    const ConfigGroupedSuggest& suggest, PlaceId place_id = PlaceId{1}) {
  eats_report_storage::types::Suggest result;
  result.place_id = place_id.GetUnderlying();
  result.title = suggest.title;
  result.button.text = suggest.button_title;
  result.button.slug = suggest.section_slug;
  result.description = suggest.suggest_text.text;
  result.icon_slug = suggest.icon_slug;
  if (suggest.suggest_template_slug.has_value()) {
    for (const auto& t : MakeTemplatesData().templates) {
      if (("template:" + t.slug) == suggest.suggest_template_slug.value()) {
        result.description = t.template_;
      }
    }
  }
  result.icon_slug = suggest.icon_slug;
  return result;
}

eats_report_storage::types::Suggest MakeResultWithParam(
    const ConfigGroupedSuggest& suggest, PlaceId place_id, double value,
    double max_value, std::string unit,
    std::optional<double> target = std::nullopt) {
  eats_report_storage::types::Suggest result;
  result.place_id = place_id.GetUnderlying();
  result.title = suggest.title;
  result.button.text = suggest.button_title;
  result.button.slug = suggest.section_slug;
  result.description = suggest.suggest_text.text;
  if (suggest.suggest_template_slug.has_value()) {
    for (const auto& t : MakeTemplatesData().templates) {
      if (("template:" + t.slug) == suggest.suggest_template_slug.value()) {
        result.description = t.template_;
      }
    }
  }
  if (suggest.dynamic_icon.has_value()) {
    eats_report_storage::types::SuggestIcon icon;
    icon.value = value;
    icon.limit = max_value;
    icon.target = target;
    icon.display = fmt::format("{:.2f} {}", value, unit);
    result.dynamic_icon = std::move(icon);
  }
  result.icon_slug = suggest.icon_slug;
  return result;
}

// Grouped suggests

std::vector<ConfigSuggestGroup> MakeGroupedSuggestsEmpty() {
  std::vector<ConfigSuggestGroup> data;
  const auto json_suggests =
      R"({
    "groups": []
})";
  const auto json = formats::json::FromString(json_suggests);
  for (const auto& item : json["groups"]) {
    data.emplace_back(item.As<ConfigSuggestGroup>());
  }
  return data;
}

std::vector<ConfigSuggestGroup> MakeGroupedSuggests() {
  std::vector<ConfigSuggestGroup> data;
  const auto json_suggests =
      R"({
"groups": [
  {
    "group_slug": "group_1",
    "number_of_displays_in_group": 1,
    "suggests": [
      {
        "suggest_slug": "group_1_suggest_1",
        "icon_slug": "icon_slug_1",
        "section_slug": "section_slug_1",
        "suggest_text": {
          "text": "text1",
          "params": []
        },
        "title": "Title1",
        "button_title": "ButtonTitle1",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 4,
                  "arg_name": "rating",
                  "arg_type": "double"
                },
                "type": "lt"
              }
            ]
          },
          "type": "any_of"
        }
      },
      {
        "suggest_slug": "group_1_suggest_2",
        "icon_slug": "icon_slug_2",
        "section_slug": "section_slug_2",
        "suggest_text": {
          "text": "text2",
          "params": []
        },
        "title": "Title2",
        "button_title": "ButtonTitle2",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 5.5,
                  "arg_name": "pict_share",
                  "arg_type": "double"
                },
                "type": "gt"
              }
            ]
          },
          "type": "any_of"
        }
      }
    ]
  },
  {
    "group_slug": "group_2",
    "suggests": [
      {
        "suggest_slug": "group_2_suggest_1",
        "icon_slug": "icon_slug_3",
        "section_slug": "section_slug_3",
        "suggest_text": {
          "text": "text3",
          "params": []
        },
        "title": "Title3",
        "button_title": "ButtonTitle3",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 4,
                  "arg_name": "rating",
                  "arg_type": "double"
                },
                "type": "lt"
              }
            ]
          },
          "type": "any_of"
        }
      },
      {
        "suggest_slug": "group_2_suggest_2",
        "icon_slug": "icon_slug_4",
        "section_slug": "section_slug_4",
        "suggest_text": {
          "text": "text4",
          "params": []
        },
        "title": "Title4",
        "button_title": "ButtonTitle4",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 5.5,
                  "arg_name": "pict_share",
                  "arg_type": "double"
                },
                "type": "lt"
              }
            ]
          },
          "type": "any_of"
        }
      }
    ]
  },
  {
    "group_slug": "group_3",
    "number_of_displays_in_group": 1,
    "suggests": [
      {
        "suggest_slug": "group_3_suggest_1",
        "icon_slug": "icon_slug_5",
        "section_slug": "section_slug_5",
        "suggest_text": {
          "text": "text5",
          "params": []
        },
        "title": "Title5",
        "button_title": "ButtonTitle5",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 4,
                  "arg_name": "rating",
                  "arg_type": "double"
                },
                "type": "lt"
              }
            ]
          },
          "type": "any_of"
        }
      }
    ]
  },
  {
    "group_slug": "group_4",
    "number_of_displays_in_group": 0,
    "suggests": [
      {
        "suggest_slug": "group_4_suggest_1",
        "icon_slug": "icon_slug_6",
        "section_slug": "section_slug_6",
        "suggest_text": {
          "text": "text6",
          "params": []
        },
        "title": "Title6",
        "button_title": "ButtonTitle6",
        "predicates": {
          "init": {
            "predicates": [
              {
                "init": {
                  "value": 4,
                  "arg_name": "rating",
                  "arg_type": "double"
                },
                "type": "lt"
              }
            ]
          },
          "type": "any_of"
        }
      }
    ]
  }
]
})";
  const auto json = formats::json::FromString(json_suggests);
  for (const auto& item : json["groups"]) {
    data.emplace_back(item.As<ConfigSuggestGroup>());
  }
  return data;
}

std::optional<ConfigGroupedSuggest> FindSuggest(
    const std::vector<ConfigSuggestGroup>& groups_suggests,
    std::string_view suggest_slug) {
  for (const auto& group : groups_suggests) {
    for (const auto& item : group.suggests) {
      if (item.suggest_slug == suggest_slug) {
        return item;
      }
    }
  }
  return std::nullopt;
}

eats_report_storage::types::Suggest MakeResult(
    const ConfigGroupedSuggest& suggest, PlaceId place_id = PlaceId{1}) {
  eats_report_storage::types::Suggest result;
  result.place_id = place_id.GetUnderlying();
  result.title = suggest.title;
  result.button.text = suggest.button_title;
  result.button.slug = suggest.section_slug;
  result.description = suggest.suggest_text.text;
  result.icon_slug = suggest.icon_slug;
  return result;
}

struct DashboardGroupedSuggestComponentTestEmptyConfig : public Test {
  DashboardSuggestsComponentImpl impl_;
  std::vector<ConfigSuggestGroup> suggests_ = MakeGroupedSuggestsEmpty();
  DashboardGroupedSuggestComponentTestEmptyConfig() : impl_() {}
};

TEST_F(DashboardGroupedSuggestComponentTestEmptyConfig,
       GetGroupedSuggests_empty_empty) {
  ASSERT_TRUE(impl_.GetSuggests(suggests_, {}, {}, nullptr, nullptr).empty());
}

struct DashboardGroupedSuggestComponentTest : public Test {
  DashboardSuggestsComponentImpl impl_;
  std::vector<ConfigSuggestGroup> suggests_ = MakeGroupedSuggests();
  DashboardGroupedSuggestComponentTest() : impl_() {}
};

TEST_F(DashboardGroupedSuggestComponentTest, GetSuggests_empty) {
  ASSERT_TRUE(impl_.GetSuggests(suggests_, {}, {}, nullptr, nullptr).empty());
}

TEST_F(DashboardGroupedSuggestComponentTest, GetSuggests_place_beautifull) {
  const auto place_suggest = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},          // place_id
      "group_1_suggest_1",  // suggest
      1                     // priority
  };
  auto value = eats_report_storage::types::SuggestValuesOpt{};
  value.place_id = PlaceId{11};
  value.brand_id = 12;
  value.rating = 4.9;

  ASSERT_TRUE(impl_
                  .GetSuggests(suggests_, {std::pair(value.place_id, value)},
                               {place_suggest}, nullptr, nullptr)
                  .empty());
}

TEST_F(DashboardGroupedSuggestComponentTest, GetSuggests_limit_suggests) {
  std::vector<eats_report_storage::types::PlaceSuggest> request_suggests;
  std::unordered_map<PlaceId, eats_report_storage::types::SuggestValuesOpt>
      place_data;

  PlaceId place_id{1};
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_2",  // suggest
      1                     // priority
  });
  // will not be included in the result, because a suggest is already displayed
  // from the first group
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_1",  // suggest
      2                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_3_suggest_1",  // suggest
      3                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_1",  // suggest
      4                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_2",  // suggest
      5                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_4_suggest_1",  // suggest
      6                     // priority
  });
  place_data[place_id] = eats_report_storage::types::SuggestValuesOpt{};
  place_data[place_id].place_id = place_id;
  place_data[place_id].brand_id = 11;
  place_data[place_id].pict_share = 6.2;
  place_data[place_id].rating = 3.2;

  auto suggest12 = FindSuggest(suggests_, "group_1_suggest_2").value();
  auto suggest21 = FindSuggest(suggests_, "group_2_suggest_1").value();
  auto suggest31 = FindSuggest(suggests_, "group_3_suggest_1").value();

  // Mock result
  eats_report_storage::types::SuggestList result;
  result.emplace_back(MakeResult(suggest12, PlaceId{1}));
  result.emplace_back(MakeResult(suggest31, PlaceId{1}));
  result.emplace_back(MakeResult(suggest21, PlaceId{1}));
  ASSERT_EQ(impl_.GetSuggests(suggests_, place_data, request_suggests, nullptr,
                              nullptr),
            result);
}

TEST_F(DashboardGroupedSuggestComponentTest,
       GetSuggests_limit_suggests_multi_places) {
  std::vector<eats_report_storage::types::PlaceSuggest> request_suggests;
  std::unordered_map<PlaceId, eats_report_storage::types::SuggestValuesOpt>
      place_data;

  PlaceId place_id{1};
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_2",  // suggest
      1                     // priority
  });
  // will not be included in the result, because a suggest is already displayed
  // from the first group
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_1",  // suggest
      2                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_3_suggest_1",  // suggest
      3                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_1",  // suggest
      4                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_2",  // suggest
      5                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_4_suggest_1",  // suggest
      6                     // priority
  });
  place_data[place_id] = eats_report_storage::types::SuggestValuesOpt{};
  place_data[place_id].place_id = place_id;
  place_data[place_id].brand_id = 11;
  place_data[place_id].pict_share = 6.2;
  place_data[place_id].rating = 3.2;

  place_id = PlaceId{2};
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_2",  // suggest
      1                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_1_suggest_1",  // suggest
      2                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_3_suggest_1",  // suggest
      3                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_1",  // suggest
      4                     // priority
  });
  request_suggests.emplace_back(eats_report_storage::types::PlaceSuggest{
      place_id,             // place_id
      "group_2_suggest_2",  // suggest
      5                     // priority
  });
  place_data[place_id] = eats_report_storage::types::SuggestValuesOpt{};
  place_data[place_id].place_id = place_id;
  place_data[place_id].brand_id = 11;
  place_data[place_id].pict_share = 1.2;
  place_data[place_id].rating = 1.2;

  auto suggest11 = FindSuggest(suggests_, "group_1_suggest_1").value();
  auto suggest12 = FindSuggest(suggests_, "group_1_suggest_2").value();
  auto suggest21 = FindSuggest(suggests_, "group_2_suggest_1").value();
  auto suggest22 = FindSuggest(suggests_, "group_2_suggest_2").value();
  auto suggest31 = FindSuggest(suggests_, "group_3_suggest_1").value();

  // Mock result
  eats_report_storage::types::SuggestList result;
  result.emplace_back(MakeResult(suggest12, PlaceId{1}));
  result.emplace_back(MakeResult(suggest31, PlaceId{1}));
  result.emplace_back(MakeResult(suggest21, PlaceId{1}));
  result.emplace_back(MakeResult(suggest11, PlaceId{2}));
  result.emplace_back(MakeResult(suggest31, PlaceId{2}));
  result.emplace_back(MakeResult(suggest21, PlaceId{2}));
  result.emplace_back(MakeResult(suggest22, PlaceId{2}));
  ASSERT_EQ(impl_.GetSuggests(suggests_, place_data, request_suggests, nullptr,
                              nullptr),
            result);
}

struct DashboardSuggestComponentWithTemplatesTest : public Test {
  DashboardSuggestsComponentImpl impl_;
  std::shared_ptr<Templater> templater_ = std::make_shared<Templater>();
  std::vector<ConfigSuggestGroup> groups_ = MakeSuggestsWithTemplate();
  DashboardSuggestComponentWithTemplatesTest() : impl_() {}
};

TEST_F(DashboardSuggestComponentWithTemplatesTest,
       GetSuggests_multi_suggests_with_template) {
  templater_->ParseTemplates(MakeTemplatesData());
  const auto place_suggest_ph = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},    // place_id
      "more_photos",  // suggest
      10              // priority
  };
  const auto place_suggest_rating = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},   // place_id
      "low_rating",  // suggest
      1              // priority
  };
  auto value = eats_report_storage::types::SuggestValuesOpt{};
  value.place_id = PlaceId{11};
  value.brand_id = 12;
  value.pict_share = 6.2;
  value.rating = 3.2;

  eats_report_storage::types::SuggestList result;
  if (auto suggest = FindSuggest(groups_, "low_rating"); suggest.has_value()) {
    result.emplace_back(MakeResultWithParam(suggest.value(), value.place_id));
  }
  if (auto suggest = FindSuggest(groups_, "more_photos"); suggest.has_value()) {
    result.emplace_back(MakeResultWithParam(suggest.value(), value.place_id));
  }
  auto res = impl_.GetSuggests(groups_, {std::pair(value.place_id, value)},
                               {place_suggest_rating, place_suggest_ph},
                               templater_, nullptr);
  ASSERT_EQ(res.size(), result.size());

  ASSERT_EQ(res, result);
}

TEST_F(DashboardSuggestComponentWithTemplatesTest,
       GetSuggests_multi_suggests_with_template_empty) {
  templater_->ParseTemplates(MakeTemplatesEmpty());
  const auto place_suggest_ph = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},    // place_id
      "more_photos",  // suggest
      10              // priority
  };
  const auto place_suggest_rating = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},   // place_id
      "low_rating",  // suggest
      1              // priority
  };
  auto value = eats_report_storage::types::SuggestValuesOpt{};
  value.place_id = PlaceId{11};
  value.brand_id = 12;
  value.pict_share = 6.2;
  value.rating = 3.2;

  eats_report_storage::types::SuggestList result;
  if (auto suggest = FindSuggest(groups_, "low_rating"); suggest.has_value()) {
    result.emplace_back(MakeResult(suggest.value(), value.place_id));
  }
  if (auto suggest = FindSuggest(groups_, "more_photos"); suggest.has_value()) {
    result.emplace_back(MakeResult(suggest.value(), value.place_id));
  }
  ASSERT_EQ(impl_.GetSuggests(groups_, {std::pair(value.place_id, value)},
                              {place_suggest_rating, place_suggest_ph},
                              templater_, nullptr),
            result);
}

struct DashboardSuggestComponentWithUnitsTest : public Test {
  DashboardSuggestsComponentImpl impl_;

  StrictMock<clients::eats_core::ClientGMock> core_mock;

  clients::eats_core::Place MakePlace(int64_t place_id,
                                      const std::string& currency) {
    clients::eats_core::Place place;
    place.id = place_id;
    place.currency.sign = currency;
    return place;
  }

  std::vector<ConfigSuggestGroup> groups_ = MakeSuggestsWithIcon();
  DashboardSuggestComponentWithUnitsTest() : impl_() {}
};

TEST_F(DashboardSuggestComponentWithUnitsTest,
       GetSuggests_multi_suggests_with_icons) {
  eats_report_storage::models::PlacesUnitsPtr units =
      std::make_shared<eats_report_storage::models::PlacesUnits>(
          core_mock, eats_report_storage::types::PlaceIds{PlaceId{11}});

  clients::eats_core::v1_places_info::post::Response response;
  response.payload = {MakePlace(11, "$$")};
  EXPECT_CALL(core_mock, V1PlacesInfo(_, _)).WillRepeatedly(Return(response));

  const auto place_suggest_ph = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},    // place_id
      "more_photos",  // suggest
      10              // priority
  };
  const auto place_suggest_rating = eats_report_storage::types::PlaceSuggest{
      PlaceId{11},   // place_id
      "low_rating",  // suggest
      1              // priority
  };
  auto value = eats_report_storage::types::SuggestValuesOpt{};
  value.place_id = PlaceId{11};
  value.brand_id = 12;
  value.pict_share = 6.2;
  value.rating = 3.2;

  eats_report_storage::types::SuggestList result;
  if (auto suggest = FindSuggest(groups_, "more_photos"); suggest.has_value()) {
    result.emplace_back(
        MakeResultWithParam(suggest.value(), value.place_id, 6.2, 5.5, "$$"));
  }

  if (auto suggest = FindSuggest(groups_, "low_rating"); suggest.has_value()) {
    result.emplace_back(MakeResultWithParam(suggest.value(), value.place_id,
                                            3.2, 3.7, "$$", 4.3));
  }

  ASSERT_EQ(impl_.GetSuggests(groups_, {std::pair(value.place_id, value)},
                              {place_suggest_ph, place_suggest_rating}, nullptr,
                              units),
            result);
}

}  // namespace testing
