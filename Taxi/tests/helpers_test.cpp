#include <geo-pipeline/helpers/source_resolver.hpp>

#include <userver/utest/utest.hpp>

namespace {
UTEST(HelpersTest, ResolveSources) {
  ::geo_pipeline_config::current_version::SourcesData data;
  data.sources = {{"A", "B", "C", "D", "E"}};
  ::geo_pipeline_config::current_version::SourcesDataSourcesets
      data_source_sets;
  data_source_sets.extra["FirstThree"] = {"A", "B", "C"};
  data_source_sets.extra["LastThree"] = {"C", "D", "E"};
  data.source_sets = data_source_sets;

  ::geo_pipeline_config::current_version::PipelineConfig config{{}, data};

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>({"All"}, config);
    std::sort(result.begin(), result.end());
    ASSERT_EQ(result, *data.sources);
  }

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>(
        {"E", "D", "FirstThree"}, config);
    std::sort(result.begin(), result.end());
    ASSERT_EQ(result, *data.sources);
  }

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>(
        {"FirstThree", "LastThree"}, config);
    std::sort(result.begin(), result.end());
    ASSERT_EQ(result, *data.sources);
  }

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>({"FirstThree"},
                                                            config);
    std::sort(result.begin(), result.end());
    std::vector<std::string> target{"A", "B", "C"};
    ASSERT_EQ(result, target);
  }

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>(
        {"FirstThree", "A", "C"}, config);
    std::sort(result.begin(), result.end());
    std::vector<std::string> target{"A", "B", "C"};
    ASSERT_EQ(result, target);
  }

  {
    auto result = geo_pipeline::ResolveSources<
        ::geo_pipeline_config::PipelineTypesCurrentVersion>(
        {"FirstThree", "UnsupportedSource"}, config);
    std::sort(result.begin(), result.end());
    std::vector<std::string> target{"A", "B", "C"};
    ASSERT_EQ(result, target);
  }
}
}  // namespace
