#include <userver/utest/utest.hpp>

#include <string>
#include <vector>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <eventus/mappers/set_json_value_mapper.hpp>
#include <eventus/order_event.hpp>

using eventus::common::OperationArgs;
using eventus::common::OperationArgument;
using OperationArgsV = std::vector<eventus::common::OperationArgumentType>;

TEST(Mappers, SetJsonValueMapperTest) {
  namespace keys = eventus::order_event::keys;

  formats::json::ValueBuilder builder;
  std::string expected_name = "descriptor_name";
  std::vector<std::string> expected_tags{"tag1", "tag2"};
  builder["name"] = expected_name;
  builder["tags"] = expected_tags;
  auto json_mapper =
      eventus::mappers::SetJsonValueMapper(std::vector<OperationArgument>{
          {"dst_key", keys::kEventDescriptor},
          {"value", formats::json::ToString(builder.ExtractValue())},
          {"policy", "set"},
      });

  eventus::mappers::Event event({});
  json_mapper.Map(event);

  ASSERT_TRUE(event.HasKey(keys::kEventDescriptor));
  auto descriptor_json =
      event.Get<formats::json::Value>(keys::kEventDescriptor);
  ASSERT_TRUE(!descriptor_json.IsNull());
  ASSERT_TRUE(descriptor_json.HasMember("name"));
  ASSERT_TRUE(descriptor_json.HasMember("tags"));
  ASSERT_EQ(descriptor_json["name"].As<std::string>(), expected_name);
  ASSERT_EQ(descriptor_json["tags"].As<std::vector<std::string>>(),
            expected_tags);
}
