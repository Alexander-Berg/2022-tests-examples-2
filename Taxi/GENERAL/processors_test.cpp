#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <geo-pipeline/processors.hpp>

namespace geo_pipeline::processors {

using TestPipelineTypes = geo_pipeline_config::PipelineTypesOfVersion<4>;

inline formats::json::Value operator"" _json(const char* str, size_t len) {
  return formats::json::FromString(std::string_view(str, len));
}

template <typename Type>
Type ParseJsonAs(const formats::json::Value& json) {
  return handlers::libraries::geo_pipeline_config::Parse(
      json, formats::parse::To<Type>());
}

TEST(TestProcessors, TestTimeShiftProcessor) {
  auto include_json = R"(
    {
      "type": "time-shift-processor",
      "operation": "include",
      "begin": 5,
      "end": 15
    }
  )"_json;

  auto exclude_json = R"(
    {
      "type": "time-shift-processor",
      "operation": "exclude",
      "begin": 5,
      "end": 15
    }
  )"_json;

  std::vector<size_t> shifts{0, 3, 5, 10, 15, 20};
  geobus::types::UniversalSignals signals;
  for (const auto& shift : shifts) {
    geobus::types::UniversalSignal signal;
    signal.prediction_shift = std::chrono::seconds{shift};
    signals.signals.push_back(std::move(signal));
  }

  ProcessorsRegistry<TestPipelineTypes> registry;

  {
    auto copy_signals = signals;
    Processors<TestPipelineTypes> processors(
        std::optional<
            std::vector<typename TestPipelineTypes::ProcessorVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::ProcessorVariant>(
                include_json)}},
        registry);

    processors.Apply(copy_signals);

    EXPECT_EQ(copy_signals.signals.size(), 2);
  }
  {
    auto copy_signals = signals;
    Processors<TestPipelineTypes> processors(
        std::optional<
            std::vector<typename TestPipelineTypes::ProcessorVariant>>{
            {ParseJsonAs<typename TestPipelineTypes::ProcessorVariant>(
                exclude_json)}},
        registry);

    processors.Apply(copy_signals);

    EXPECT_EQ(copy_signals.signals.size(), 4);
  }
}

TEST(TestProcessors, EmptyProcessors) {
  auto json = R"({})"_json;

  {
    ProcessorsRegistry<TestPipelineTypes> registry(
        std::nullopt, ConfigValidationMode::kAllertMode);
    EXPECT_EQ(registry.GetErrors().size(), 0);
    EXPECT_EQ(registry.GetCycleNodes().size(), 0);
    EXPECT_EQ(registry.GetValidProcessors().size(), 0);
  }
  {
    ProcessorsRegistry<TestPipelineTypes> registry(
        ParseJsonAs<
            typename TestPipelineTypes::PipelineConfigDefinitionsProcessors>(
            json),
        ConfigValidationMode::kAllertMode);
    EXPECT_EQ(registry.GetErrors().size(), 0);
    EXPECT_EQ(registry.GetCycleNodes().size(), 0);
    EXPECT_EQ(registry.GetValidProcessors().size(), 0);
  }
}

TEST(TestProcessors, UnexpectedVertex) {
  /// 1 -> 2
  /// 2 (undefined in definitions map)
  auto json = R"(
    {
      "processor_1": {
        "type": "ref",
        "ref": "processor_2"
      }
    }
  )"_json;

  ProcessorsRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsProcessors>(
          json));

  EXPECT_EQ(registry.GetErrors().size(), 1);
  EXPECT_EQ(registry.GetErrors()[0].code, ErrorCode::kMissingProcessor);
  EXPECT_EQ(registry.GetCycleNodes().size(), 0);
  EXPECT_EQ(registry.GetValidProcessors().size(), 0);
}

TEST(TestProcessors, OneNodeCycle) {
  /// 1 <----
  /// |     |
  /// ------
  auto cycle_json = R"(
    {
      "processor_1": {
        "type": "ref",
        "ref": "processor_1"
      }
    }
  )"_json;

  ProcessorsRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsProcessors>(
          cycle_json));

  EXPECT_EQ(registry.GetErrors().size(), 1);
  EXPECT_EQ(registry.GetErrors()[0].code, ErrorCode::kProcessorsCycle);
  EXPECT_EQ(registry.GetCycleNodes().size(), 1);
  EXPECT_EQ(registry.GetValidProcessors().size(), 0);
}

TEST(TestProcessors, TestCycleDetecting) {
  //      4 -> -
  //           |
  // 0 -> 1 -> 2 -> 3
  //      |         |
  //      - <- - <- -
  auto cycle_json = R"(
    {
      "processor_0": {
        "type": "ref",
        "ref": "processor_1"
      },
      "processor_1": {
        "type": "ref",
        "ref": "processor_2"
      },
      "processor_2": {
        "type": "ref",
        "ref": "processor_3"
      },
      "processor_3": {
        "type": "ref",
        "ref": "processor_1"
      },
      "processor_4": {
        "type": "ref",
        "ref": "processor_2"
      }
    }
  )"_json;

  EXPECT_THROW(
      std::make_shared<ProcessorsRegistry<TestPipelineTypes>>(
          ParseJsonAs<
              typename TestPipelineTypes::PipelineConfigDefinitionsProcessors>(
              cycle_json),
          ConfigValidationMode::kAllertMode),
      std::exception);

  std::unordered_set<std::string> cycle_nodes = {"processor_0", "processor_1",
                                                 "processor_2", "processor_3",
                                                 "processor_4"};

  ProcessorsRegistry<TestPipelineTypes> registry(
      ParseJsonAs<
          typename TestPipelineTypes::PipelineConfigDefinitionsProcessors>(
          cycle_json));

  EXPECT_TRUE(cycle_nodes == registry.GetCycleNodes());
}

}  // namespace geo_pipeline::processors
