#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/value.hpp>

#include <eventus/common/operation_argument.hpp>
#include <eventus/mappers/atlas/list_to_map_mapper.hpp>

namespace {

using StringV = std::vector<std::string>;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

constexpr const auto kTestEvent = R"(
{
  "empty": [],
  "container": {
    "sub": [
      {
        "name": "abc"
      },
      {
        "name": "bcd"
      },
      {
        "invalid-item": "should-be-gone"
      }
    ],
    "this-key": "should-be-left"
  },
  "depth0": {
      "depth1": {
          "depth2": {
              "bus": [
                  {
                    "name": "cde",
                    "null": null,
                    "x": 1.0
                  },
                  {
                    "name": "def",
                    "bool": false,
                    "y": 2.0
                  },
                  {
                    "name": "efg",
                    "num": 0,
                    "z": 3.5
                  }
              ]
          }
      }
  },
  "invalid-value": 0.0,
  "null-value": null
}
)";

}  // namespace

UTEST(KeyMapping, ListToMapMapperInvalidValueTest) {
  const auto event_data = formats::json::FromString(kTestEvent);
  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", "invalid-value"},
      {"dst", "will-not-be-set"},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("invalid-value"));
  ASSERT_FALSE(data.HasMember("will-not-be-set"));
}

UTEST(KeyMapping, ListToMapMapperNullValueTest) {
  const auto event_data = formats::json::FromString(kTestEvent);

  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", "null-value"},
      {"dst", "will-not-be-set"},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("invalid-value"));
  ASSERT_FALSE(data.HasMember("will-not-be-set"));
}

UTEST(KeyMapping, ListToMapMapperSimpleTest) {
  const auto event_data = formats::json::FromString(kTestEvent);

  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", StringV{"container", "sub"}},
      {"dst", "xsub"},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("container"));
  ASSERT_TRUE(data["container"].HasMember("sub"));
  ASSERT_TRUE(data.HasMember("xsub"));
  ASSERT_TRUE(data["xsub"].HasMember("abc"));
  ASSERT_TRUE(data["xsub"].HasMember("bcd"));
  ASSERT_FALSE(data["xsub"].HasMember("invalid-item"));
  ASSERT_EQ(data["container"]["sub"][0], data["xsub"]["abc"]);
  ASSERT_EQ(data["container"]["sub"][1], data["xsub"]["bcd"]);
}

UTEST(KeyMapping, ListToMapMapperDepthDstTest) {
  const auto event_data = formats::json::FromString(kTestEvent);
  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", StringV{"container", "sub"}},
      {"dst", StringV{"mod_container", "sub"}},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("container"));
  ASSERT_TRUE(data["container"].HasMember("sub"));
  ASSERT_TRUE(data.HasMember("mod_container"));
  ASSERT_TRUE(data["mod_container"].HasMember("sub"));
  ASSERT_TRUE(data["mod_container"]["sub"].HasMember("abc"));
  ASSERT_TRUE(data["mod_container"]["sub"].HasMember("bcd"));
  ASSERT_FALSE(data["mod_container"]["sub"].HasMember("invalid-item"));
  ASSERT_EQ(data["container"]["sub"][0], data["mod_container"]["sub"]["abc"]);
  ASSERT_EQ(data["container"]["sub"][1], data["mod_container"]["sub"]["bcd"]);
}

UTEST(KeyMapping, ListToMapMapperInPlaceTest) {
  const auto event_data = formats::json::FromString(kTestEvent);
  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", StringV{"container", "sub"}},
      {"dst", StringV{"container", "sub"}},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  const auto old_data = event.GetData();
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("container"));
  ASSERT_TRUE(data["container"].HasMember("sub"));
  ASSERT_TRUE(data["container"].HasMember("this-key"));
  ASSERT_TRUE(data["container"]["sub"].HasMember("abc"));
  ASSERT_TRUE(data["container"]["sub"].HasMember("bcd"));
  ASSERT_FALSE(data["container"]["sub"].HasMember("invalid-item"));
  ASSERT_EQ(old_data["container"]["sub"][0], data["container"]["sub"]["abc"]);
  ASSERT_EQ(old_data["container"]["sub"][1], data["container"]["sub"]["bcd"]);
}

TEST(KeyMapping, ListToMapMapperDeepSetTest) {
  const auto event_data = formats::json::FromString(kTestEvent);
  auto mapper = eventus::mappers::atlas::ListToMapMapper(OperationArgsV{
      {"src", StringV{"depth0", "depth1", "depth2", "bus"}},
      {"dst", StringV{"xdepth0", "xdepth1", "xdepth2", "xbus"}},
      {"map_by_key", "name"},
  });
  eventus::mappers::Event event(event_data);
  const auto old_data = event.GetData();
  mapper.Map(event);
  LOG_DEBUG() << "Updated event: " << formats::json::ToString(event.GetData());

  const auto data = event.GetData();
  ASSERT_TRUE(data.HasMember("depth0"));
  ASSERT_TRUE(data.HasMember("container"));
  ASSERT_TRUE(data["depth0"].HasMember("depth1"));
  ASSERT_TRUE(data["depth0"]["depth1"].HasMember("depth2"));
  ASSERT_TRUE(data["depth0"]["depth1"]["depth2"].HasMember("bus"));
  ASSERT_TRUE(data.HasMember("xdepth0"));
  ASSERT_TRUE(data["xdepth0"].HasMember("xdepth1"));
  ASSERT_TRUE(data["xdepth0"]["xdepth1"].HasMember("xdepth2"));
  ASSERT_TRUE(data["xdepth0"]["xdepth1"]["xdepth2"].HasMember("xbus"));
  ASSERT_TRUE(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"].HasMember("cde"));
  ASSERT_TRUE(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"].HasMember("def"));
  ASSERT_TRUE(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"].HasMember("efg"));

  ASSERT_EQ(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"]["cde"],
            data["depth0"]["depth1"]["depth2"]["bus"][0]);
  ASSERT_EQ(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"]["def"],
            data["depth0"]["depth1"]["depth2"]["bus"][1]);
  ASSERT_EQ(data["xdepth0"]["xdepth1"]["xdepth2"]["xbus"]["efg"],
            data["depth0"]["depth1"]["depth2"]["bus"][2]);
}
