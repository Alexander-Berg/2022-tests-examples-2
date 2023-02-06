#include <variant>

#include <gtest/gtest.h>
#include <userver/formats/bson/serialize.hpp>

#include <caches/requirements_cache.hpp>
#include <models/requirement.hpp>

using RequirementType = models::requirement::types::RequirementType;

TEST(TestRequirementsCache, SelectRequirementParsing) {
  std::string data = R"(
  {
    "_id": {"$oid": "aaaaaaaaaaaaaaaaaaaaaaaa"},
    "default": null,
    "name": "count_luggage",
    "position": 1,
    "type": "select",
    "select": {
      "type": "number",
      "options": [
        {
          "style": "check",
          "name": "suitcase",
          "value": 1,
          "independent_tariffication": true
        },
        {
          "style": "check",
          "name": "suitcase2",
          "value": 2,
          "independent_tariffication": true
        },
        {
          "style": "check",
          "name": "suitcase3",
          "value": 3,
          "independent_tariffication": true
        }
      ]
    },
    "driver_name": "count_luggage",
    "multiselect": false
  }
  )";

  auto requirement_doc = formats::bson::FromJsonString(data);
  auto requirement =
      caches::RequirementsCacheTraits::DeserializeObject(requirement_doc);
  ASSERT_EQ(requirement.name, "count_luggage");
  ASSERT_EQ(requirement.type, RequirementType::Select);

  auto& description =
      std::get<models::requirement::SelectRequirementsDescription>(
          requirement.description);
  ASSERT_FALSE(description.required);
  ASSERT_FALSE(description.tariff_specific);
  ASSERT_EQ(description.driver_name, "count_luggage");
  ASSERT_FALSE(description.default_value);
  ASSERT_FALSE(description.multiselect);

  auto& options = description.options;
  ASSERT_EQ(options.size(), 3U);
  ASSERT_EQ(options[0].name, "suitcase");
  ASSERT_EQ(options[0].style, "check");
  ASSERT_EQ(options[0].value, 1U);
  ASSERT_TRUE(options[0].independent_tariffication);
  ASSERT_FALSE(options[0].weight);
  ASSERT_FALSE(options[0].max_count);
}
