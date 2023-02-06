#include <userver/utest/utest.hpp>

#include <userver/formats/json/value.hpp>

#include <eventus/common/operation_argument.hpp>

#include <eventus/mappers/atlas/no_cars_setter_mapper.hpp>

namespace {

using StringV = std::vector<std::string>;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

constexpr const auto kTestEvent = R"(
{
  "classes": {
    "comfort": {
      "estimated_waiting": 4,
      "surge": {
        "value": 5
      }
    },
    "econom": {
      "surge": {
        "value": 5
      }
    },
    "vip": {
      "estimated_waiting": 4
    }
  }
}
)";

}  // namespace

UTEST(KeyMapping, NoCarsTest) {
  const auto event_data = formats::json::FromString(kTestEvent);

  auto mapper = eventus::mappers::atlas::NoCarsSetterMapper(OperationArgsV{
      {"dict", "classes"},
      {"dst", "no_cars"},
      {"exists", std::vector<std::string>{"surge", "value"}},
      {"doesnt_exist", std::vector<std::string>{"estimated_waiting"}}});
  eventus::mappers::Event event(event_data);
  mapper.Map(event);

  const auto data = event.GetData();
  const std::vector<int> should_be{0, 1, 0};
  ASSERT_EQ(data["no_cars"].As<std::vector<int>>(), should_be);
}
