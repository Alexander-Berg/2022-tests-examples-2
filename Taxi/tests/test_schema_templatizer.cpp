#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <models/circuit_schema_template.hpp>
#include <radio/detail/schemas/templatizer.hpp>
#include <utils/except.hpp>

namespace hejmdal::radio::detail::schemas {

namespace {
const std::string kTemplateStr = R"=(
{
  "type": "template",
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 1.0,
      "param2": "some_value",
      "param3": true,
      "must_specify": ["param2", "param3"]
    },
    {
      "id": "block_id_2",
      "param4": 2.0
    }
  ],
  "entry_points": [
    {
      "id": "entry_point_1"
    }
  ],
  "out_points": [
    {
      "id": "out_point_1"
    }
  ]
}
  )=";
}

TEST(TestSchemaTemplatizer, HappyPath) {
  const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param1": 2.0,
      "param2": "other_value",
      "param3": false,
      "new_param": 42
    },
    "block_id_2": {
      "param5": "yet_another_value"
    },
    "entry_point_1": {
      "debug": ["data"]
    },
    "out_point_1": {
      "debug": ["state"]
    }
  }
}
  )=";
  const std::string kExpectedStr = R"=(
{
  "type": "schema",
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 2.0,
      "param2": "other_value",
      "param3": false,
      "new_param": 42
    },
    {
      "id": "block_id_2",
      "param4": 2.0,
      "param5": "yet_another_value"
    }
  ],
  "entry_points": [
    {
      "id": "entry_point_1",
      "debug": ["data"]
    }
  ],
  "out_points": [
    {
      "id": "out_point_1",
      "debug": ["state"]
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema = formats::json::FromString(kSchemaStr);
  auto expected = formats::json::FromString(kExpectedStr);
  auto result = ApplyTemplate(schema, tpl);
  EXPECT_EQ(formats::json::ToString(expected), formats::json::ToString(result));
}

TEST(TestSchemaTemplatizer, Errors) {
  auto tpl = formats::json::FromString(kTemplateStr);
  {
    // minimal nothrow test
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param2": "other_value",
      "param3": false
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_NO_THROW(ApplyTemplate(schema, tpl));
  }
  {
    // no required param
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param1": 2.0,
      "param2": "other_value",
      "new_param": 42
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_THROW(ApplyTemplate(schema, tpl), except::Error);
  }
  {
    // no block with required param
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_2": {
      "param5": "yet_another_value"
    },
    "entry_point_1": {
      "debug": ["data"]
    },
    "out_point_1": {
      "debug": ["state"]
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_THROW(ApplyTemplate(schema, tpl), except::Error);
  }
  {
    // incorrect block id
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param2": "other_value",
      "param3": false
    },
    "block_id_incorrect": {
      "param2": "other_value",
      "param3": false
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_THROW(ApplyTemplate(schema, tpl), except::Error);
  }
  {
    // override id
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param2": "other_value",
      "param3": false,
      "id": "new_id"
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_THROW(ApplyTemplate(schema, tpl), except::Error);
  }
  {
    // override type
    const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "params": {
    "block_id_1": {
      "param2": "other_value",
      "param3": false,
      "type": "new_type"
    }
  }
}
  )=";
    auto schema = formats::json::FromString(kSchemaStr);
    EXPECT_THROW(ApplyTemplate(schema, tpl), except::Error);
  }
}

TEST(TestSchemaTemplatizer, NoParams) {
  static const std::string kTemplateStr = R"=(
{
  "type": "template",
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 1.0,
      "param2": "some_value",
      "param3": true
    }
  ],
  "entry_points": [
    {
      "id": "entry_point_1"
    }
  ],
  "out_points": [
    {
      "id": "out_point_1"
    }
  ]
}
  )=";
  const std::string kSchemaStr = R"=(
{
  "type": "schema"
}
  )=";
  static const std::string kExpectedStr = R"=(
{
  "type": "schema",
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 1.0,
      "param2": "some_value",
      "param3": true
    }
  ],
  "entry_points": [
    {
      "id": "entry_point_1"
    }
  ],
  "out_points": [
    {
      "id": "out_point_1"
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema = formats::json::FromString(kSchemaStr);
  auto expected = formats::json::FromString(kExpectedStr);
  auto result = ApplyTemplate(schema, tpl);
  EXPECT_EQ(formats::json::ToString(expected), formats::json::ToString(result));
}

TEST(TestParametrizedTemplate, OverrideRequired) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": true
    },
    "param_2_p": {
      "type": "string",
      "required": true
    },
    "param_3_p": {
      "type": "string",
      "default": "default value"
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p",
      "param_3": "$param_3_p"
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  const std::string kSchemaStr = R"=(
{
    "name": "Test schema name",
    "override_params": {
        "param_1_p": 300,
        "param_2_p": "test value"
    },
    "type": "schema",
    "use_template": "template_threshold"
}
  )=";
  static const std::string kExpectedStr = R"=(
{
  "blocks": [
    {
      "id": "id_1",
      "param_1": 300,
      "param_3": "default value"
    },
    {
      "id": "id_2",
      "param_2": "test value"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test schema name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "schema",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema = formats::json::FromString(kSchemaStr);
  auto expected = formats::json::FromString(kExpectedStr);
  auto result = ApplyTemplate(schema, tpl);
  EXPECT_EQ(expected, result);
}

TEST(TestParametrizedTemplate, OverrideDefault) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": true
    },
    "param_2_p": {
      "type": "string",
      "required": true
    },
    "param_3_p": {
      "type": "string",
      "default": "default value"
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p",
      "param_3": "$param_3_p"
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  const std::string kSchemaOverrideDefaultStr = R"=(
{
    "name": "Test schema name",
    "override_params": {
        "param_1_p": 300,
        "param_2_p": "test value",
        "param_3_p": "new value"
    },
    "type": "schema",
    "use_template": "template_threshold"
}
  )=";
  static const std::string kExpectedOverrideStr = R"=(
{
  "blocks": [
    {
      "id": "id_1",
      "param_1": 300,
      "param_3": "new value"
    },
    {
      "id": "id_2",
      "param_2": "test value"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test schema name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "schema",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema_override = formats::json::FromString(kSchemaOverrideDefaultStr);
  auto expected_override = formats::json::FromString(kExpectedOverrideStr);
  auto result_override = ApplyTemplate(schema_override, tpl);
  EXPECT_EQ(expected_override, result_override);
}

TEST(TestParametrizedTemplate, NotDefineRequired) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": true
    },
    "param_2_p": {
      "type": "string",
      "required": true
    },
    "param_3_p": {
      "type": "string",
      "default": "default value"
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p",
      "param_3": "$param_3_p"
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  const std::string kSchemaNotDefinedStr = R"=(
{
    "name": "Test schema name",
    "override_params": {
        "param_1_p": 300
    },
    "type": "schema",
    "use_template": "template_threshold"
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema_not_def = formats::json::FromString(kSchemaNotDefinedStr);
  ASSERT_THROW(ApplyTemplate(schema_not_def, tpl), except::TemplateParamsError);
}

TEST(TestParametrizedTemplate, DefineNotUsed) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": true
    },
    "param_2_p": {
      "type": "string",
      "required": true
    },
    "param_3_p": {
      "type": "string",
      "default": "default value"
    },
    "param_4_p": {
      "type": "string",
      "default": "not used"
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p",
      "param_3": "$param_3_p"
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  ASSERT_THROW(models::ValidateTemplateUsedParams(tpl),
               except::TemplateParamsError);
}

TEST(TestParametrizedTemplate, NotOverridenNotIncludedToResult) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": false
    },
    "param_2_p": {
      "type": "number",
      "required": true
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p"
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  const std::string kSchemaStr = R"=(
{
    "name": "Test schema name",
    "override_params": {
        "param_2_p": 300
    },
    "type": "schema",
    "use_template": "template_threshold"
}
  )=";
  static const std::string kExpectedStr = R"=(
{
  "blocks": [
    {
      "id": "id_1"
    },
    {
      "id": "id_2",
      "param_2": 300
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test schema name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "schema",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";

  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema = formats::json::FromString(kSchemaStr);
  auto expected = formats::json::FromString(kExpectedStr);
  auto result = ApplyTemplate(schema, tpl);
  EXPECT_EQ(expected, result);
}

TEST(TestParametrizedTemplate, ParametrizedAndOverride) {
  static const std::string kTemplateStr = R"=(
{
  "used_params": {
    "param_1_p": {
      "type": "number",
      "required": true
    },
    "param_2_p": {
      "type": "string",
      "required": true
    }
  },
  "blocks": [
    {
      "id": "id_1",
      "param_1": "$param_1_p",
      "must_specify": ["param_3"]
    },
    {
      "id": "id_2",
      "param_2": "$param_2_p"
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test template name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  const std::string kSchemaStr = R"=(
{
    "name": "Test schema name",
    "override_params": {
        "param_1_p": 300,
        "param_2_p": "test value"
    },
    "params": {
      "id_1": {
        "param_3": true
      },
      "id_2": {
        "param_2": "new value",
        "new_param": 100
      }
    },
    "type": "schema",
    "use_template": "template_threshold"
}
  )=";
  static const std::string kExpectedStr = R"=(
{
  "blocks": [
    {
      "id": "id_1",
      "param_1": 300,
      "param_3": true
    },
    {
      "id": "id_2",
      "param_2": "new value",
      "new_param": 100
    }
  ],
  "entry_points": [
    {
      "id": "entry_id",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "Test schema name",
  "out_points": [
    {
      "id": "out_point_id",
      "type": "state_out_point"
    }
  ],
  "type": "schema",
  "wires": [
    {
      "from": "entry_id",
      "to": "id_1",
      "type": "data"
    },
    {
      "from": "id_1",
      "to": "id_2",
      "type": "data"
    },
    {
      "from": "id_2",
      "to": "out_point_id",
      "type": "state"
    }
  ]
}
  )=";
  auto tpl = formats::json::FromString(kTemplateStr);
  auto schema = formats::json::FromString(kSchemaStr);
  auto expected = formats::json::FromString(kExpectedStr);
  auto result = ApplyTemplate(schema, tpl);
  EXPECT_EQ(expected, result);
}

}  // namespace hejmdal::radio::detail::schemas
