#include <userver/utest/utest.hpp>

#include <geo-pipeline/validation_types.hpp>

#include <processing/validator.hpp>

namespace {
namespace cv = ::geo_pipeline_config::current_version;
using GeoPipelineConfig = cv::PipelineConfig;
using ChannelsList = cv::ChannelsList;

using ErrorCode = geo_pipeline::ErrorCode;

UTEST(PipelineValidationTest, YagaMetrologMissingChannel) {
  //  geo_pipeline_control_plane::processing::ConfigValidator validator;
  //  GeoPipelineConfig config;
  //  ChannelsList channels_list{
  //      {{"channel1", cv::ChannelConfig{"address1", "taxi-passing",
  //                                      cv::ChannelType::kAdjusted,
  //                                      cv::ChannelProtocol::kEdge, 0}},
  //       {"channel2", cv::ChannelConfig{"address2", "taxi-passing",
  //                                      cv::ChannelType::kAdjusted,
  //                                      cv::ChannelProtocol::kEdge, 0}}}};
  //  cv::MetrologPipelineConfig metrolog{{"channel1", "channel2",
  //  "channel-bad"},
  //                                      ""};
  //  config.channels_list = channels_list;
  //  config.yaga_metrolog = metrolog;
  //  auto validation_result = validator.Validate(config, std::nullopt);
  //
  //  ASSERT_EQ(validation_result.size(), 1);
  //  ASSERT_EQ(validation_result[0].code, ErrorCode::kMissingChannel);
}

UTEST(PipelineValidationTest, YagaMetrologWrongProtocol_Positions) {
  //  geo_pipeline_control_plane::processing::ConfigValidator validator;
  //  GeoPipelineConfig config;
  //  ChannelsList channels_list{
  //      {{"channel1", cv::ChannelConfig{"address1", "taxi-passing",
  //                                      cv::ChannelType::kPositions,
  //                                      cv::ChannelProtocol::kPositions,
  //                                      0}}}};
  //  cv::MetrologPipelineConfig metrolog{{"channel1"}, ""};
  //  config.channels_list = channels_list;
  //  config.yaga_metrolog = metrolog;
  //  auto validation_result = validator.Validate(config, std::nullopt);
  //
  //  ASSERT_EQ(validation_result.size(), 1);
  //  ASSERT_EQ(validation_result[0].code, ErrorCode::kChannelProtocolError);
}

UTEST(PipelineValidationTest, YagaMetrologValidConfig) {
  //  geo_pipeline_control_plane::processing::ConfigValidator validator;
  //  GeoPipelineConfig config;
  //  ChannelsList channels_list{
  //      {{"channel-adj", cv::ChannelConfig{"address-adj", "taxi-passing",
  //                                         cv::ChannelType::kPositions,
  //                                         cv::ChannelProtocol::kEdge, 0}},
  //       {"channel-uni",
  //        cv::ChannelConfig{"address-uni", "taxi-passing",
  //                          cv::ChannelType::kPositions,
  //                          cv::ChannelProtocol::kUniversalSignal, 0}}}};
  //  cv::MetrologPipelineConfig metrolog{{"channel-adj", "channel-uni"}, ""};
  //  config.channels_list = channels_list;
  //  config.yaga_metrolog = metrolog;
  //  auto validation_result = validator.Validate(config, std::nullopt);
  //
  //  ASSERT_EQ(validation_result.size(), 0);
}

}  // namespace
