#include <gtest/gtest.h>

#include <unordered_map>

#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <models/circuit_schema.hpp>
#include <models/postgres/circuit_schema.hpp>
#include <names/circuit_schema.hpp>
#include <radio/detail/schemas/templatizer.hpp>

namespace hejmdal::models {

std::ostream& operator<<(std::ostream& os, const CircuitSchema& bar) {
  os << "[" << bar.id << ", " << bar.description << ", "
     << formats::json::ToString(bar.schema) << ", "
     << ::utils::datetime::Timestring(bar.updated) << ", " << bar.revision
     << " ]";
  return os;
}

::testing::AssertionResult CheckPointerMapEq(const CircuitSchemaMap& expected,
                                             const CircuitSchemaMap& test) {
  if (expected.size() != test.size()) {
    return ::testing::AssertionFailure() << "expected size " << expected.size()
                                         << ", test size " << test.size();
  }

  for (const auto& [key, expected_value] : expected) {
    if (auto it = test.find(key); it != test.end()) {
      if (*expected_value != *it->second) {
        return ::testing::AssertionFailure()
               << "mismatch at key " << key << ": expected " << *expected_value
               << ", test " << *it->second;
      }
    }
    if (!test.count(key)) {
      return ::testing::AssertionFailure()
             << "test does not contain expected key " << key;
    }
    if (*expected_value != *test.at(key)) {
    }
  }
  return ::testing::AssertionSuccess();
}

namespace nm = names::circuit_schema;

void MockBlocks(formats::json::ValueBuilder& builder) {
  builder[nm::kBlocks].PushBack(
      formats::json::MakeObject("type", "some_type", "id", "block_1"));
  builder[nm::kEntryPoints].PushBack(
      formats::json::MakeObject("id", "entry_1"));
  builder[nm::kOutPoints].PushBack(formats::json::MakeObject("id", "out_1"));
}

formats::json::Value MockJsonSchema(bool is_template,
                                    std::optional<const char*> tpl_to_use) {
  formats::json::ValueBuilder json_schema;
  if (is_template) {
    json_schema[nm::kType] = nm::type::kTemplate;
    MockBlocks(json_schema);
  } else {
    json_schema[nm::kType] = nm::type::kSchema;
    if (tpl_to_use.has_value()) {
      json_schema[nm::kUseTemplate] = tpl_to_use.value();
      json_schema[nm::kParams]["block_1"]["param_1"] = "some_value";
    } else {
      MockBlocks(json_schema);
    }
  }
  return json_schema.ExtractValue();
}

postgres::CircuitSchema MockPgCircuitSchema(
    const std::string& id, bool is_template,
    std::optional<const char*> tpl_to_use, std::int32_t revision) {
  postgres::CircuitSchema result;
  result.id = id;
  result.type = is_template ? names::circuit_schema::type::kTemplate
                            : names::circuit_schema::type::kSchema;
  result.schema = MockJsonSchema(is_template, tpl_to_use);
  result.revision = revision;
  return result;
}

CircuitSchemaPtr MockCircuitSchemaPtr(const std::string& id, bool is_template,
                                      std::optional<const char*> tpl_to_use,
                                      std::int32_t revision) {
  auto pg_schema = std::make_shared<postgres::CircuitSchema>(
      MockPgCircuitSchema(id, is_template, tpl_to_use, revision));
  return CircuitSchemaCache::PgToModel(pg_schema);
}

CircuitSchema MockTemplatizedSchema(const std::string& id,
                                    std::int32_t revision) {
  auto templatized_json_schema = radio::detail::schemas::ApplyTemplate(
      MockJsonSchema(false, "some_id"), MockJsonSchema(true, {}));

  CircuitSchema result;
  result.id = CircuitSchemaId(id);
  result.type = SchemaType::kSchema;
  result.schema = templatized_json_schema;
  result.revision = revision;
  return result;
}

CircuitSchemaPtr MockTemplatizedSchemaPtr(const std::string& id,
                                          std::int32_t revision) {
  return std::make_shared<const CircuitSchema>(
      MockTemplatizedSchema(id, revision));
}

TEST(TestSchemaCache, GetUpdate) {
  CircuitSchemaCache cache;
  cache.insert(
      {{}, MockPgCircuitSchema("schema_id1", false, "template_id1", 1)});
  cache.insert({{}, MockPgCircuitSchema("schema_id2", false, {}, 2)});
  cache.insert({{}, MockPgCircuitSchema("template_id1", true, {}, 3)});
  cache.insert(
      {{}, MockPgCircuitSchema("schema_id3", false, "template_id2", 4)});
  cache.insert({{}, MockPgCircuitSchema("schema_id4", false, {}, 5)});
  cache.insert({{}, MockPgCircuitSchema("template_id2", true, {}, 6)});
  cache.insert(
      {{}, MockPgCircuitSchema("schema_id5", false, "template_id2", 7)});

  auto [affected_schemas_rev_2, all_schemas_rev_2, last_rev_2] =
      cache.GetUpdates(2);
  CircuitSchemaMap expected_affected_schemas_rev_2{
      {CircuitSchemaId{"schema_id1"},
       MockTemplatizedSchemaPtr("schema_id1", 1)},
      {CircuitSchemaId{"schema_id3"},
       MockTemplatizedSchemaPtr("schema_id3", 4)},
      {CircuitSchemaId{"schema_id4"},
       MockCircuitSchemaPtr("schema_id4", false, {}, 5)},
      {CircuitSchemaId{"schema_id5"},
       MockTemplatizedSchemaPtr("schema_id5", 7)}};

  EXPECT_TRUE(CheckPointerMapEq(expected_affected_schemas_rev_2,
                                affected_schemas_rev_2));
  EXPECT_EQ(7, last_rev_2);

  CircuitSchemaMap expected_all_schemas = expected_affected_schemas_rev_2;
  expected_all_schemas.insert(
      {CircuitSchemaId{"schema_id2"},
       MockCircuitSchemaPtr("schema_id2", false, {}, 2)});

  EXPECT_TRUE(CheckPointerMapEq(expected_all_schemas, all_schemas_rev_2));

  auto [affected_schemas_rev_6, all_schemas_rev_6, last_rev_6] =
      cache.GetUpdates(6);

  CircuitSchemaMap expected_affected_schemas_rev_6{
      {CircuitSchemaId{"schema_id5"},
       MockTemplatizedSchemaPtr("schema_id5", 7)}};

  EXPECT_TRUE(CheckPointerMapEq(expected_affected_schemas_rev_6,
                                affected_schemas_rev_6));
  EXPECT_TRUE(CheckPointerMapEq(expected_all_schemas, all_schemas_rev_6));
  EXPECT_EQ(7, last_rev_6);
}
}  // namespace hejmdal::models
