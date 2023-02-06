#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <geo-pipeline/predicates.hpp>

namespace geo_pipeline::predicates {

using TestPipelineTypes = geo_pipeline_config::PipelineTypesOfVersion<4>;

inline formats::json::Value operator"" _json(const char* str, size_t len) {
  return formats::json::FromString(std::string_view(str, len));
}

template <typename Type>
Type ParseJsonAs(const formats::json::Value& json) {
  return handlers::libraries::geo_pipeline_config::Parse(
      json, formats::parse::To<Type>());
}

TEST(TestPredicates, TestSignalSourcePredicate) {
  auto include_json = R"(
    {
      "type": "signal-source-predicate",
      "operation": "include",
      "values": [
        "Verified",
        "Chtoto"
      ]
    }
  )"_json;

  auto exclude_json = R"(
    {
      "type": "signal-source-predicate",
      "operation": "exclude",
      "values": [
        "Verified",
        "Chtoto"
      ]
    }
  )"_json;

  geobus::types::UniversalSignals verified_signals;
  verified_signals.source = "Verified";

  geobus::types::UniversalSignals unknown_signals;
  unknown_signals.source = "Unknown";

  PredicatesRegistry<TestPipelineTypes> registry;

  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                include_json)}},
        registry);

    EXPECT_TRUE(predicates.Apply(verified_signals));
    EXPECT_FALSE(predicates.Apply(unknown_signals));
  }
  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                exclude_json)}},
        registry);

    EXPECT_FALSE(predicates.Apply(verified_signals));
    EXPECT_TRUE(predicates.Apply(unknown_signals));
  }
}

TEST(TestPredicates, TestSensorPredicate) {
  auto include_json = R"(
    {
      "type": "sensor-predicate",
      "sensor": "transport_type",
      "operation": "include",
      "values": [
        "pedestrian"
      ],
      "if_absent": true
    }
  )"_json;

  auto exclude_json = R"(
    {
      "type": "sensor-predicate",
      "sensor": "transport_type",
      "operation": "exclude",
      "values": [
        "pedestrian"
      ],
      "if_absent": false
    }
  )"_json;

  geobus::types::UniversalSignals pedestrian_signals;
  std::string pedestrian_sensor_value = "pedestrian";
  pedestrian_signals.sensors.push_back(
      {"transport_type",
       std::vector<unsigned char>(pedestrian_sensor_value.begin(),
                                  pedestrian_sensor_value.end())});

  geobus::types::UniversalSignals non_pedestrian_signals;
  std::string non_pedestrian_sensor_value = "non_pedestrian";
  non_pedestrian_signals.sensors.push_back(
      {"transport_type",
       std::vector<unsigned char>(non_pedestrian_sensor_value.begin(),
                                  non_pedestrian_sensor_value.end())});

  geobus::types::UniversalSignals empty_sensors_signals;

  PredicatesRegistry<TestPipelineTypes> registry;

  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                include_json)}},
        registry);

    EXPECT_TRUE(predicates.Apply(pedestrian_signals));
    EXPECT_FALSE(predicates.Apply(non_pedestrian_signals));
    // Expect true because if_absent is true
    EXPECT_TRUE(predicates.Apply(empty_sensors_signals));
  }

  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                exclude_json)}},
        registry);

    EXPECT_FALSE(predicates.Apply(pedestrian_signals));
    EXPECT_TRUE(predicates.Apply(non_pedestrian_signals));
    // Expect false because if_absent is false
    EXPECT_FALSE(predicates.Apply(empty_sensors_signals));
  }
}

TEST(TestPredicates, TestContractorIdPredicate) {
  auto include_json = R"(
    {
      "type": "contractor-id-predicate",
      "operation": "include",
      "percent": 100
    }
  )"_json;

  auto exclude_json = R"(
    {
      "type": "contractor-id-predicate",
      "operation": "exclude",
      "percent": 100
    }
  )"_json;

  geobus::types::UniversalSignals driver_signals;
  driver_signals.contractor_id = driver_id::DriverDbidUndscrUuid("dbid_uuid");

  PredicatesRegistry<TestPipelineTypes> registry;

  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                include_json)}},
        registry);

    EXPECT_TRUE(predicates.Apply(driver_signals));
  }

  {
    Predicates<TestPipelineTypes> predicates(
        std::optional<
            std::vector<typename TestPipelineTypes::PredicateVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(
                exclude_json)}},
        registry);

    EXPECT_FALSE(predicates.Apply(driver_signals));
  }
}

TEST(TestPredicates, TestBoolAnyPredicate) {
  auto config = R"(
    {
      "type": "any",
      "predicates":
        {
          "predicates": [
            {
              "type": "signal-source-predicate",
              "operation": "include",
              "values": [
                "Verified",
                "Chtoto"
              ]
            },
            {
              "type": "sensor-predicate",
              "sensor": "transport_type",
              "operation": "include",
              "values": [
                "pedestrian"
              ],
              "if_absent": true
            }
          ]
      }
    }
  )"_json;

  std::string pedestrian_sensor_string_value = "pedestrian";
  std::vector<unsigned char> pedestrian_sensor_value(
      pedestrian_sensor_string_value.begin(),
      pedestrian_sensor_string_value.end());

  std::string non_pedestrian_sensor_string_value = "non-pedestrian";
  std::vector<unsigned char> non_pedestrian_sensor_value(
      non_pedestrian_sensor_string_value.begin(),
      non_pedestrian_sensor_string_value.end());

  geobus::types::UniversalSignals pedestrian_verified_signals;
  pedestrian_verified_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals pedestrian_unknown_signals;
  pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_unknown_signals.source = "Unknown";

  geobus::types::UniversalSignals non_pedestrian_verified_signals;
  non_pedestrian_verified_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals non_pedestrian_unknown_signals;
  non_pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_unknown_signals.source = "Unknown";

  PredicatesRegistry<TestPipelineTypes> registry;

  Predicates<TestPipelineTypes> predicates(
      std::optional<std::vector<typename TestPipelineTypes::PredicateVariant>>{
          {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(config)}},
      registry);

  EXPECT_TRUE(predicates.Apply(pedestrian_verified_signals));
  EXPECT_TRUE(predicates.Apply(pedestrian_unknown_signals));
  EXPECT_TRUE(predicates.Apply(non_pedestrian_verified_signals));
  EXPECT_FALSE(predicates.Apply(non_pedestrian_unknown_signals));
}

TEST(TestPredicates, TestBoolAllPredicate) {
  auto config = R"(
    {
      "type": "all",
      "predicates":
        {
          "predicates": [
            {
              "type": "signal-source-predicate",
              "operation": "include",
              "values": [
                "Verified",
                "Chtoto"
              ]
            },
            {
              "type": "sensor-predicate",
              "sensor": "transport_type",
              "operation": "include",
              "values": [
                "pedestrian"
              ],
              "if_absent": true
            }
          ]
      }
    }
  )"_json;

  std::string pedestrian_sensor_string_value = "pedestrian";
  std::vector<unsigned char> pedestrian_sensor_value(
      pedestrian_sensor_string_value.begin(),
      pedestrian_sensor_string_value.end());

  std::string non_pedestrian_sensor_string_value = "non-pedestrian";
  std::vector<unsigned char> non_pedestrian_sensor_value(
      non_pedestrian_sensor_string_value.begin(),
      non_pedestrian_sensor_string_value.end());

  geobus::types::UniversalSignals pedestrian_verified_signals;
  pedestrian_verified_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals pedestrian_unknown_signals;
  pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_unknown_signals.source = "Unknown";

  geobus::types::UniversalSignals non_pedestrian_verified_signals;
  non_pedestrian_verified_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals non_pedestrian_unknown_signals;
  non_pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_unknown_signals.source = "Unknown";

  PredicatesRegistry<TestPipelineTypes> registry;

  Predicates<TestPipelineTypes> predicates(
      std::optional<std::vector<typename TestPipelineTypes::PredicateVariant>>{
          {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(config)}},
      registry);

  EXPECT_TRUE(predicates.Apply(pedestrian_verified_signals));
  EXPECT_FALSE(predicates.Apply(pedestrian_unknown_signals));
  EXPECT_FALSE(predicates.Apply(non_pedestrian_verified_signals));
  EXPECT_FALSE(predicates.Apply(non_pedestrian_unknown_signals));
}

TEST(TestPredicates, TestBoolNonePredicate) {
  auto config = R"(
    {
      "type": "none_of",
      "predicates":
        {
          "predicates": [
            {
              "type": "signal-source-predicate",
              "operation": "include",
              "values": [
                "Verified",
                "Chtoto"
              ]
            },
            {
              "type": "sensor-predicate",
              "sensor": "transport_type",
              "operation": "include",
              "values": [
                "pedestrian"
              ],
              "if_absent": true
            }
          ]
      }
    }
  )"_json;

  std::string pedestrian_sensor_string_value = "pedestrian";
  std::vector<unsigned char> pedestrian_sensor_value(
      pedestrian_sensor_string_value.begin(),
      pedestrian_sensor_string_value.end());

  std::string non_pedestrian_sensor_string_value = "non-pedestrian";
  std::vector<unsigned char> non_pedestrian_sensor_value(
      non_pedestrian_sensor_string_value.begin(),
      non_pedestrian_sensor_string_value.end());

  geobus::types::UniversalSignals pedestrian_verified_signals;
  pedestrian_verified_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals pedestrian_unknown_signals;
  pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", pedestrian_sensor_value});
  pedestrian_unknown_signals.source = "Unknown";

  geobus::types::UniversalSignals non_pedestrian_verified_signals;
  non_pedestrian_verified_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_verified_signals.source = "Verified";

  geobus::types::UniversalSignals non_pedestrian_unknown_signals;
  non_pedestrian_unknown_signals.sensors.push_back(
      {"transport_type", non_pedestrian_sensor_value});
  non_pedestrian_unknown_signals.source = "Unknown";

  PredicatesRegistry<TestPipelineTypes> registry;

  Predicates<TestPipelineTypes> predicates(
      std::optional<std::vector<typename TestPipelineTypes::PredicateVariant>>{
          {ParseJsonAs<typename TestPipelineTypes::PredicateVariant>(config)}},
      registry);

  EXPECT_FALSE(predicates.Apply(pedestrian_verified_signals));
  EXPECT_FALSE(predicates.Apply(pedestrian_unknown_signals));
  EXPECT_FALSE(predicates.Apply(non_pedestrian_verified_signals));
  EXPECT_TRUE(predicates.Apply(non_pedestrian_unknown_signals));
}

TEST(TestPredicates, EmptyPredicates) {
  auto json = R"({})"_json;

  {
    PredicatesRegistry<TestPipelineTypes> registry(
        std::nullopt, ConfigValidationMode::kAllertMode);
    EXPECT_EQ(registry.GetErrors().size(), 0);
    EXPECT_EQ(registry.GetCycleNodes().size(), 0);
    EXPECT_EQ(registry.GetValidPredicates().size(), 0);
  }
  {
    PredicatesRegistry<TestPipelineTypes> registry(
        ParseJsonAs<
            typename TestPipelineTypes::PipelineConfigDefinitionsPredicates>(
            json),
        ConfigValidationMode::kAllertMode);
    EXPECT_EQ(registry.GetErrors().size(), 0);
    EXPECT_EQ(registry.GetCycleNodes().size(), 0);
    EXPECT_EQ(registry.GetValidPredicates().size(), 0);
  }
}

TEST(TestPredicates, UnexpectedVertex) {
  /// 1 -> 2
  /// 2 (undefined in definitions map)
  auto json = R"(
    {
      "predicate_1": {
        "type": "ref",
        "ref": "predicate_2"
      }
    }
  )"_json;

  PredicatesRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsPredicates>(
          json));

  EXPECT_EQ(registry.GetErrors().size(), 1);
  EXPECT_EQ(registry.GetErrors()[0].code, ErrorCode::kMissingPredicate);
  EXPECT_EQ(registry.GetCycleNodes().size(), 0);
  EXPECT_EQ(registry.GetValidPredicates().size(), 0);
}

TEST(TestPredicates, OneNodeCycle) {
  /// 1 <----
  /// |     |
  /// ------
  auto cycle_json = R"(
    {
      "predicate_1": {
        "type": "ref",
        "ref": "predicate_1"
      }
    }
  )"_json;

  PredicatesRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsPredicates>(
          cycle_json));

  EXPECT_EQ(registry.GetErrors().size(), 1);
  EXPECT_EQ(registry.GetErrors()[0].code, ErrorCode::kPredicatesCycle);
  EXPECT_EQ(registry.GetCycleNodes().size(), 1);
  EXPECT_EQ(registry.GetValidPredicates().size(), 0);
}

TEST(TestPredicates, TestCycleDetecting) {
  //      4 -> -
  //           |
  // 0 -> 1 -> 2 -> 3 -> 5
  //      |         |
  //      - <- - <- -
  //
  // Only predicate 5 is not a part of cycle
  auto cycle_json = R"(
    {
      "predicate_0": {
        "type": "ref",
        "ref": "predicate_1"
      },
      "predicate_1": {
        "type": "ref",
        "ref": "predicate_2"
      },
      "predicate_2": {
        "type": "ref",
        "ref": "predicate_3"
      },
      "predicate_3": {
        "type": "all",
        "predicates":{
          "predicates": [
            {
              "type": "ref",
              "ref": "predicate_5"
            },
            {
              "type": "ref",
              "ref": "predicate_1"
            }
          ]
        }
      },
      "predicate_4": {
        "type": "ref",
        "ref": "predicate_2"
      },
      "predicate_5": {
        "type": "sensor-predicate",
        "sensor": "transport_type",
        "operation": "include",
        "values": [
          "pedestrian"
        ],
        "if_absent": true
      }
    }
  )"_json;

  EXPECT_THROW(
      std::make_shared<PredicatesRegistry<TestPipelineTypes>>(
          ParseJsonAs<
              typename TestPipelineTypes::PipelineConfigDefinitionsPredicates>(
              cycle_json),
          ConfigValidationMode::kAllertMode),
      std::exception);

  std::unordered_set<std::string> cycle_nodes = {"predicate_0", "predicate_1",
                                                 "predicate_2", "predicate_3",
                                                 "predicate_4"};

  PredicatesRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsPredicates>(
          cycle_json));

  EXPECT_TRUE(cycle_nodes == registry.GetCycleNodes());
}

}  // namespace geo_pipeline::predicates
