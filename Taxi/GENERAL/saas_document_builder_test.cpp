#include <gtest/gtest.h>

#include "saas_document_builder.hpp"

#include <userver/formats/json/serialize.hpp>

using namespace eats_full_text_search_indexer::utils;

TEST(SaasDocumentBuilder, AddZone) {
  constexpr std::string_view kExpectedJson = R"(
  {
    "key": {
      "value": "my_value",
      "type": "#zp"
    }
  }
  )";
  auto expected = formats::json::FromString(kExpectedJson);
  SaasDocumentBuilder builder;
  builder.AddZone("key", "my_value");
  ASSERT_EQ(expected, builder.Build().ExtractValue());
}

TEST(SaasDocumentBuilder, AddSearchPropertyString) {
  constexpr std::string_view kExpectedJson = R"(
    {
      "key": {
        "value": "my_value_property",
        "type": "#lp"
      }
    }
  )";
  auto expected = formats::json::FromString(kExpectedJson);
  SaasDocumentBuilder builder;
  builder.AddSearchProperty("key", "my_value_property");
  ASSERT_EQ(expected, builder.Build().ExtractValue());
}

TEST(SaasDocumentBuilder, AddSearchPropertyInt) {
  constexpr std::string_view kExpectedJson = R"(
    {
      "key": {
        "value": 1,
        "type": "#ip"
      }
    }
  )";
  auto expected = formats::json::FromString(kExpectedJson);
  SaasDocumentBuilder builder;
  builder.AddSearchProperty("key", 1);
  ASSERT_EQ(expected, builder.Build().ExtractValue());
}

TEST(SaasDocumentBuilder, AddPropertyString) {
  constexpr std::string_view kExpectedJson = R"(
    {
      "key": {
        "value": "my_value_property",
        "type": "#p"
      }
    }
  )";
  auto expected = formats::json::FromString(kExpectedJson);
  SaasDocumentBuilder builder;
  builder.AddProperty("key", "my_value_property");
  ASSERT_EQ(expected, builder.Build().ExtractValue());
}

TEST(SaasDocumentBuilder, AddMoneyProperty) {
  constexpr std::string_view kExpectedJson = R"(
    {
      "key": {
        "value": "1.23",
        "type": "#p"
      }
    }
  )";
  auto expected = formats::json::FromString(kExpectedJson);
  SaasDocumentBuilder builder;
  builder.AddMoneyProperty("key", 1.234);
  ASSERT_EQ(expected, builder.Build().ExtractValue());
}
