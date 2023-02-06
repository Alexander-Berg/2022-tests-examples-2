#include <gtest/gtest.h>

#include "js-pipeline/models/serialization/json/schema.hpp"

struct SchemaTest : public ::testing::Test {
 protected:
  void SetUp() override {}
  void TearDown() override {}
};

TEST_F(SchemaTest, TestParseObjectAdditionalProperties) {
  // object with a fixed schema
  {
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": false,"
        "  \"properties\": { \"abc\": { \"type\": \"integer\" } },"
        "  \"type\": \"object\""
        "}");
    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);
    ASSERT_EQ(js_pipeline::models::Schema::ValueType::kObject,
              schema->GetType());

    schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation{"abc"});
    ASSERT_FALSE(!schema);
    ASSERT_EQ(js_pipeline::models::Schema::ValueType::kInteger,
              schema->GetType());
  }

  // object with a non-fixed schema (no fixed properties)
  {
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": true,"
        "  \"type\": \"object\""
        "}");
    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);
    ASSERT_EQ(js_pipeline::models::Schema::ValueType::kObject,
              schema->GetType());

    schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation());
    ASSERT_TRUE(!schema);
  }

  // object with a non-fixed schema (some fixed properties)
  {
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": true,"
        "  \"properties\": { \"abc\": { \"type\": \"integer\" } },"
        "  \"type\": \"object\""
        "}");
    ASSERT_THROW(json.As<js_pipeline::models::SchemaCPtr>(),
                 js_pipeline::SchemaParseError);
  }

  // dict with a fixed schema
  {
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": { \"type\": \"integer\" },"
        "  \"type\": \"object\""
        "}");
    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);
    ASSERT_EQ(js_pipeline::models::Schema::ValueType::kObject,
              schema->GetType());

    schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation());
    ASSERT_FALSE(!schema);
    ASSERT_EQ(js_pipeline::models::Schema::ValueType::kInteger,
              schema->GetType());
  }
}

TEST_F(SchemaTest, TestParseReursiveSchemas) {
  {
    // selfref object
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": false,"
        "  \"properties\": { \"next\": { \"$upstack\": 1 } },"
        "  \"type\": \"object\""
        "}");

    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);

    auto child_schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation{"next"});
    ASSERT_FALSE(!child_schema);

    ASSERT_TRUE(schema.get() == child_schema.get());
  }

  {
    // array
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": false,"
        "  \"properties\": { \"others\": { "
        "                    \"type\": \"array\","
        "                    \"items\": {\"$upstack\": 2} } },"
        "  \"type\": \"object\""
        "}");

    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);

    auto array_schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation{"others"});

    ASSERT_FALSE(!array_schema);
    ASSERT_TRUE(array_schema->IsArray());
    auto array_item_schema = array_schema->GetArrayMeta().items.Get();

    ASSERT_FALSE(!array_item_schema);

    ASSERT_TRUE(schema.get() == array_item_schema.get());
  }

  {
    // additionalProperties
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": {\"$upstack\": 1},"
        "  \"type\": \"object\""
        "}");

    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);

    auto additional_properties_schema = schema->Step(
        js_pipeline::models::Schema::DynamicPropertyAccessOperation(""));

    ASSERT_FALSE(!additional_properties_schema);

    ASSERT_TRUE(schema.get() == additional_properties_schema.get());
  }

  {
    // big $upstack
    auto json = formats::json::FromString(
        "{"
        "  \"additionalProperties\": false,"
        "  \"type\":  \"object\","
        "  \"properties\": { \"field\": { "
        "                    \"additionalProperties\": false,"
        "                    \"properties\": { \"others\": { "
        "                                      \"type\": \"array\","
        "                                      \"items\": {\"$upstack\": 3}}},"
        "                    \"type\": \"object\"}}"
        "}");

    auto schema = json.As<js_pipeline::models::SchemaCPtr>();
    ASSERT_FALSE(!schema);

    auto child_schema = schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation{"field"});
    ASSERT_FALSE(!child_schema);

    auto array_schema = child_schema->Step(
        js_pipeline::models::Schema::StaticPropertyAccessOperation{"others"});

    ASSERT_FALSE(!array_schema);
    ASSERT_TRUE(array_schema->IsArray());
    auto array_meta = array_schema->GetArrayMeta();

    auto array_item_schema = array_meta.items.Get();
    ASSERT_FALSE(!array_item_schema);

    ASSERT_TRUE(schema.get() == array_item_schema.get());
  }
}

TEST_F(SchemaTest, TestTraverseRecursiveSchemas) {
  auto json = formats::json::FromString(
      "{"
      "  \"additionalProperties\": false,"
      "  \"type\":  \"object\","
      "  \"properties\": { \"field\": { "
      "                    \"additionalProperties\": false,"
      "                    \"properties\": { \"others\": { "
      "                                      \"type\": \"array\","
      "                                      \"items\": {\"$upstack\": 3}}},"
      "                    \"type\": \"object\"}}"
      "}");

  auto schema = json.As<js_pipeline::models::SchemaCPtr>();
  ASSERT_FALSE(!schema);

  using Schema = js_pipeline::models::Schema;
  using Operation = std::variant<Schema::DynamicPropertyAccessOperation,
                                 Schema::StaticPropertyAccessOperation,
                                 Schema::IterationOperation>;

  auto item_schema = Schema::Traverse(
      schema,
      std::vector<Operation>{Schema::StaticPropertyAccessOperation{"field"},
                             Schema::StaticPropertyAccessOperation{"others"},
                             Schema::IterationOperation{}});
  ASSERT_FALSE(!item_schema);

  ASSERT_TRUE(schema.get() == item_schema.get());
}

TEST_F(SchemaTest, TestConvertibilityRecursiveSchemas) {
  auto json = formats::json::FromString(
      "{"
      "  \"additionalProperties\": false,"
      "  \"type\":  \"object\","
      "  \"properties\": { \"field\": { "
      "                    \"additionalProperties\": false,"
      "                    \"properties\": { \"others\": { "
      "                                      \"type\": \"array\","
      "                                      \"items\": {\"$upstack\": 3}}},"
      "                    \"type\": \"object\"}}"
      "}");

  auto schema = json.As<js_pipeline::models::SchemaCPtr>();
  auto same_schema = json.As<js_pipeline::models::SchemaCPtr>();
  ASSERT_FALSE(!schema);
  ASSERT_FALSE(!same_schema);

  ASSERT_FALSE(
      js_pipeline::models::Schema::CheckConvertibility(schema, same_schema)
          .has_value());
}
