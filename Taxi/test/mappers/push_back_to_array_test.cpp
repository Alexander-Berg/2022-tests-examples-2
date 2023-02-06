#include <userver/utest/utest.hpp>

#include <userver/formats/json/value.hpp>

#include <eventus/mappers/push_back_to_array_mapper.hpp>

namespace {

using StringV = std::vector<std::string>;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

constexpr const auto kTestEvent = R"(
{
  "lat": 1,
  "lon": 2,
  "string": "string"
}
)";

}  // namespace

UTEST(KeyMapping, PushBackTest) {
  const auto event_data = formats::json::FromString(kTestEvent);
  eventus::mappers::Event event(event_data);
  {
    auto mapper = eventus::mappers::PushBackToArrayMapper(OperationArgsV{
        {"src", "lon"},
        {"dst_array", "array_value"},
    });
    mapper.Map(event);

    const std::vector<int> should_be{2};
    ASSERT_EQ(event.Get<std::vector<int>>("array_value"), should_be);
  }
  {
    auto mapper = eventus::mappers::PushBackToArrayMapper(OperationArgsV{
        {"src", "lat"},
        {"dst_array", "array_value"},
    });
    mapper.Map(event);

    const auto data = event.GetData();
    const std::vector<int> should_be{2, 1};
    ASSERT_EQ(data["array_value"].As<std::vector<int>>(), should_be);
  }
  {
    auto mapper = eventus::mappers::PushBackToArrayMapper(OperationArgsV{
        {"src", "string"},
        {"dst_array", "array_value"},
    });
    mapper.Map(event);

    const auto data = event.GetData();
    std::vector<formats::json::Value> should_be{
        formats::json::ValueBuilder{2}.ExtractValue(),
        formats::json::ValueBuilder{1}.ExtractValue(),
        formats::json::ValueBuilder{"string"}.ExtractValue()};
    ASSERT_EQ(data["array_value"].As<std::vector<formats::json::Value>>(),
              should_be);
  }
}

UTEST(KeyMapping, PushBackNotFoundSource) {
  const auto event_data = formats::json::FromString(kTestEvent);
  {
    auto mapper = eventus::mappers::PushBackToArrayMapper(OperationArgsV{
        {"src", "looon"},
        {"dst_array", "array_value"},
    });
    eventus::mappers::Event event(event_data);
    ASSERT_THROW(mapper.Map(event), std::exception);
  }
}
