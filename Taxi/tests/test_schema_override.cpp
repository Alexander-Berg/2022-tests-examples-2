#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <radio/utils/schema_override.hpp>

namespace hejmdal::radio::utils {

TEST(TestSchemaOverride, OverrideWithDuration) {
  const std::string kSchemaStr = R"=(
{
  "type": "schema",
  "history_data_duration_sec": 30,
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 1.0,
      "param2": "some_value",
      "param3": true
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

  const std::string kSchemaOverrideStr = R"=(
{
  "params": {
    "block_id_1": {
      "param2": "other_value"
    }
  },
  "history_data_duration_sec": 60
}
)=";

  const std::string kExpectedSchemaStr = R"=(
{
  "type": "schema",
  "history_data_duration_sec": 60,
  "blocks": [
    {
      "id": "block_id_1",
      "param1": 1.0,
      "param2": "other_value",
      "param3": true
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

  auto schema = formats::json::FromString(kSchemaStr);
  auto override = formats::json::FromString(kSchemaOverrideStr);
  auto expected = formats::json::FromString(kExpectedSchemaStr);

  auto actual = circuit_schema::ApplySchemaOverride(schema, override);
  EXPECT_EQ(expected, actual);
}

}  // namespace hejmdal::radio::utils
