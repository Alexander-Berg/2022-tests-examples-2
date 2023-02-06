#include "set_key_flat_mapper.hpp"

#include <userver/utest/utest.hpp>

#include <userver/logging/log.hpp>

namespace {

using formats::json::ValueBuilder;

eventus::mappers::SetKeyFlatMapper MakeTestMapper(
    const std::vector<std::string> recursive_keys) {
  return eventus::mappers::SetKeyFlatMapper(
      std::vector<eventus::common::OperationArgument>{
          {"recursive_keys", recursive_keys},
          {"flat_key", "new_flat_key"},
      });
}

const auto kBasicRecursiveKeys =
    std::vector<std::string>{"depth1", "depth2", "pick_key"};

}  // namespace

UTEST(MappersSuite, SetKeyFlatMapperTestOk) {
  auto mapper = MakeTestMapper(kBasicRecursiveKeys);

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"]["depth2"]["pick_key"] = "expected_value";
  eventus::mappers::Event e(builder.ExtractValue());

  mapper.Map(e);
  ASSERT_TRUE(e.HasKey("new_flat_key"));
  ASSERT_EQ(e.Get<std::string>("new_flat_key"), "expected_value");
}

UTEST(MappersSuite, SetKeyFlatMapperTestObjectOk) {
  auto mapper = MakeTestMapper(std::vector<std::string>{"depth1", "pick_key"});

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"]["pick_key"]["depth3"] = "expected_value";
  eventus::mappers::Event e(builder.ExtractValue());

  mapper.Map(e);
  ASSERT_TRUE(e.HasKey("new_flat_key"));
  ASSERT_EQ(
      formats::json::ToString(e.Get<formats::json::Value>("new_flat_key")),
      "{\"depth3\":\"expected_value\"}");

  e.Set("new_flat_key", "string");
  ASSERT_EQ(formats::json::ToString(e.GetData()["depth1"]["pick_key"]),
            "{\"depth3\":\"expected_value\"}");
  ASSERT_EQ(e.Get<std::string>("new_flat_key"), "string");
}

UTEST(MappersSuite, SetKeyFlatMapperTestLastKeyMissing) {
  auto mapper = MakeTestMapper(kBasicRecursiveKeys);

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"]["depth2"]["another_key"] = "unexpected_value";
  eventus::mappers::Event e(builder.ExtractValue());

  mapper.Map(e);
  ASSERT_FALSE(e.HasKey("new_flat_key"));
}

UTEST(MappersSuite, SetKeyFlatMapperTestEarlierKeyMissing) {
  auto mapper = MakeTestMapper(kBasicRecursiveKeys);

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"]["another_depth2"] = "unexpected_value";
  eventus::mappers::Event e(builder.ExtractValue());

  mapper.Map(e);
  ASSERT_FALSE(e.HasKey("new_flat_key"));
}

UTEST(MappersSuite, SetKeyFlatMapperTestFirstKeyMissing) {
  auto mapper = MakeTestMapper(kBasicRecursiveKeys);

  ValueBuilder builder(formats::json::Type::kObject);
  builder["another_depth1"] = "unexpected_value";
  eventus::mappers::Event e(builder.ExtractValue());

  mapper.Map(e);
  ASSERT_FALSE(e.HasKey("new_flat_key"));
}

UTEST(MappersSuite, SetKeyFlatMapperTestFirstIndexKeyOk) {
  auto mapper = MakeTestMapper(std::vector<std::string>{"depth1", "0"});

  ValueBuilder array(formats::json::Type::kArray);
  array.PushBack("expected_value");
  array.PushBack("unexpected_value");

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"] = array;

  eventus::mappers::Event e(builder.ExtractValue());

  LOG_DEBUG() << formats::json::ToString(e.GetData());
  mapper.Map(e);
  ASSERT_TRUE(e.HasKey("new_flat_key"));
  ASSERT_EQ(e.Get<std::string>("new_flat_key"), "expected_value");
}

UTEST(MappersSuite, SetKeyFlatMapperTestMiddleIndexKeyOk) {
  for (auto index : std::vector<std::string>{"-2", "1"}) {
    auto mapper = MakeTestMapper(std::vector<std::string>{"depth1", index});

    ValueBuilder array(formats::json::Type::kArray);
    array.PushBack("unexpected_value");
    array.PushBack("expected_value");
    array.PushBack("unexpected_value2");

    ValueBuilder builder(formats::json::Type::kObject);
    builder["depth1"] = array;
    eventus::mappers::Event e(builder.ExtractValue());

    LOG_DEBUG() << formats::json::ToString(e.GetData());
    mapper.Map(e);
    ASSERT_TRUE(e.HasKey("new_flat_key"));
    ASSERT_EQ(e.Get<std::string>("new_flat_key"), "expected_value");
  }
}

UTEST(MappersSuite, SetKeyFlatMapperTestLastIndexKeyOk) {
  auto mapper = MakeTestMapper(std::vector<std::string>{"depth1", "-1"});

  ValueBuilder builder(formats::json::Type::kObject);
  builder["depth1"] = ValueBuilder(formats::json::Type::kArray);
  builder["depth1"].PushBack("unexpected_value");
  builder["depth1"].PushBack("expected_value");
  eventus::mappers::Event e(builder.ExtractValue());

  LOG_DEBUG() << formats::json::ToString(e.GetData());
  mapper.Map(e);
  ASSERT_TRUE(e.HasKey("new_flat_key"));
  ASSERT_EQ(e.Get<std::string>("new_flat_key"), "expected_value");
}
