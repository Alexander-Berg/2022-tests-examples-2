#include <userver/utest/utest.hpp>

#include <geo-pipeline/validation_types.hpp>

#include <processing/validator.hpp>

namespace {
namespace cv = ::geo_pipeline_config::current_version;
using GeoPipelineConfig = cv::PipelineConfig;

using ErrorCode = geo_pipeline::ErrorCode;

UTEST(PipelineValidationTest, YagrMissingChannel) {
  //  geo_pipeline_control_plane::processing::ConfigValidator validator;
  //  GeoPipelineConfig config;
  //  cv::ChannelsList channels_list{{
  //      {"channel1",
  //       cv::ChannelConfig{"positions", "redis_name",
  //       cv::ChannelType::kPositions,
  //                         cv::ChannelProtocol::kPositions, 0}},
  //  }};
  //  cv::InputPipelineConfig yagr;
  //  yagr.destinations.extra = {
  //      {"default", {{}, {}, {"channel1", "channel2"}, {}, false}}};
  //
  //  config.channels_list = channels_list;
  //  config.input = yagr;
  //  auto validation_result = validator.Validate(config, std::nullopt);
  //
  //  ASSERT_EQ(validation_result.size(), 1);
  //  ASSERT_EQ(validation_result[0].code, ErrorCode::kMissingChannel);
}
}  // namespace
