#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <userver/fs/blocking/read.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <helpers/yt_logging.hpp>

using namespace grocery_surge::models;

namespace {

formats::json::Value LoadJson(const std::string& file_name) {
  auto contents = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("src/tests/static/" + file_name));
  return formats::json::FromString(contents);
}

}  // namespace

TEST(YtLoggingHelpers, ParseToResourceMessageSuccess) {
  // js_pipeline_detailed_output.json contains four depots
  // depot_id  couriers  orders
  // 266222    1         0
  // 60287     1         1
  // 123456    0         3
  // 1         1         1

  const ::grocery_shared::LegacyDepotId depot_266222{"266222"};
  const ::grocery_shared::LegacyDepotId depot_60287{"60287"};
  const ::grocery_shared::LegacyDepotId depot_123456{"123456"};
  const ::grocery_shared::LegacyDepotId depot_1{"1"};

  js::ValuePerDepot pipeline_out;

  pipeline_out[depot_266222] = formats::json::FromString(R"(
    {
      "load_level": 266222.0
    }
  )");

  pipeline_out[depot_60287] = formats::json::FromString(R"(
    {
      "load_level": 60287.0
    }
  )");

  pipeline_out[depot_123456] = formats::json::FromString(R"(
    {
      "load_level": 123456.0
    }
  )");

  js::ValuePerDepot calculation_meta;

  calculation_meta[depot_266222] = formats::json::FromString(R"(
    {
      "nested_map": {
        "key": "value"
      },
      "nested_array": [
        "item_1",
        "item_2",
        "item_3"
      ]
    }
  )");

  calculation_meta[depot_60287] = formats::json::FromString("{}");

  // Intentionally skip calculation meta for depot 123456

  auto contents = LoadJson("js_pipeline_detailed_output.json");
  auto messages = grocery_surge::helpers::yt_logging::ParseToResourceMessage(
      ::grocery_surge_shared::js::PipelineName{"pipeline_0"}, contents,
      pipeline_out, calculation_meta);
  ASSERT_EQ(messages.size(), 2);

  auto msg_1 = messages[depot_266222];
  ASSERT_EQ(msg_1.depot_id, "266222");
  ASSERT_EQ(msg_1.pipeline_name, "pipeline_0");
  ASSERT_EQ(msg_1.orders_count, 0);
  ASSERT_EQ(msg_1.surge_info, pipeline_out[depot_266222]);
  ASSERT_EQ(msg_1.calculation_meta, calculation_meta[depot_266222]);
  ASSERT_EQ(msg_1.carts_count, 0);
  ASSERT_EQ(msg_1.carts, formats::json::FromString(R"(
    []
  )"));

  auto msg_2 = messages[depot_1];
  ASSERT_EQ(msg_2.orders_count, 1);
  ASSERT_EQ(msg_2.couriers_count, 1);
  ASSERT_EQ(msg_2.couriers, formats::json::FromString(R"(
    [
      {
        "performer_id": "dbid0_uuid777",
        "performer_status": "idle",
        "position": {
          "lat": 55.5,
          "lon": 37.5
        },
        "transport_type": ""
      }
    ]
  )"));
  ASSERT_EQ(msg_2.carts_count, 0);
}

TEST(YtLoggingHelpers, ParseToResourceMessageFailed) {
  formats::json::ValueBuilder builder;
  builder["key1"]["key2"] = "val";
  formats::json::Value empty_json = builder.ExtractValue();
  auto messages = grocery_surge::helpers::yt_logging::ParseToResourceMessage(
      ::grocery_surge_shared::js::PipelineName{"pipeline_0"}, empty_json, {},
      {});

  ASSERT_EQ(messages.size(), 0);
}
