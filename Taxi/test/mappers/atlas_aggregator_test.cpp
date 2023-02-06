#include <userver/utest/utest.hpp>

#include <eventus/mappers/atlas/aggregator_mapper.hpp>
#include <string>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <vector>

using eventus::common::OperationArgs;

namespace {

const std::string kTestEvent = R"(
{
  "calculation_id": "dd1c40bc08d4470b82ee42816e686e87",
  "classes": {
    "business": {
      "calculation_meta": {
        "pins_meta": {
          "eta_by_category": {
            "business": {
              "$$history": [
                {
                  "$$meta_idx": 6,
                  "$$value": 0
                },
                {
                  "$$meta_idx": 7,
                  "$$value": 1
                }
              ]
            }
          }
        }
      }
    },
    "child_tariff": {
      "calculation_meta": {
        "pins_meta": {
          "eta_by_category": {
            "child_tariff": {
              "$$history": []
            }
          }
        }
      }
    },
    "courier": {
      "calculation_meta": {
        "pins_meta": {
          "eta_by_category": {
            "courier": {
              "$$history": [
                {
                  "$$meta_idx": 7,
                  "$$value": 3
                }
              ]
            }
          }
        }
      }
    },
    "uber": {
      "calculation_meta": 2
    }
  }
}
)";

void CheckMapper(const OperationArgs& args,
                 const std::vector<std::optional<int>>& should_be) {
  auto event_id_mapper =
      eventus::mappers::atlas::AggregatorMapper(OperationArgs{args});

  eventus::pipeline::Event event{formats::json::FromString(kTestEvent)};

  event_id_mapper.Map(event);
  const auto alpha_surge =
      event.GetData()["eta"].As<std::vector<std::optional<int>>>();
  ASSERT_EQ(alpha_surge, should_be);
}

}  // namespace

TEST(Mappers, AtlasAggregatorBasicTest) {
  std::vector<std::string> keys{
      "calculation_meta", "pins_meta", "eta_by_category", "$key",
      "$$history",        "-1",        "$$value"};
  const auto indexes = eventus::mappers::atlas::GetIndexesOfValue(keys, "$key");
  ASSERT_EQ(indexes, std::vector<int>{3});

  const std::vector<std::string> expected{
      "calculation_meta", "pins_meta", "eta_by_category", "replaced",
      "$$history",        "-1",        "$$value"};
  ASSERT_EQ(
      eventus::mappers::atlas::SetValueByIndexes(keys, indexes, "replaced"),
      expected);
}

TEST(Mappers, AtlasAggregatorTest) {
  using OperationArgsV = std::vector<eventus::common::OperationArgument>;
  {
    OperationArgsV mapper_args{
        {"dict_name", "classes"},
        {"src", std::vector<std::string>{"calculation_meta", "pins_meta",
                                         "eta_by_category", "$key", "$$history",
                                         "-1", "$$value"}},
        {"dst", "eta"},
    };

    const auto should_be =
        std::vector<std::optional<int>>{1, std::nullopt, 3, std::nullopt};

    CheckMapper(mapper_args, should_be);
  }
  {
    OperationArgsV mapper_args{
        {"dict_name", "classes"},
        {"src", std::vector<std::string>{"calculation_meta", "pins_meta",
                                         "eta_by_category", "$key", "$$history",
                                         "1", "$$value"}},
        {"dst", "eta"},
    };

    const auto should_be = std::vector<std::optional<int>>{
        1, std::nullopt, std::nullopt, std::nullopt};

    CheckMapper(mapper_args, should_be);
  }
}
