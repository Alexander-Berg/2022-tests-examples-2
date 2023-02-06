#include "pipeline_generator.hpp"

#include <string>

PipelineGenerator::PipelineConfig PipelineGenerator::GeneratePipeline(
    bool enable_yagr, bool enable_yaga, bool enable_yaga_metrolog) {
  ::handlers::libraries::geobus_channel_config::ChannelList channels_list{};
  /// Конфиг для yagr (обрабатывает входящие позиции)
  ::std::optional<::geo_pipeline_config::current_version::InputPipelineConfig>
      input = std::nullopt;
  ::std::optional<::geo_pipeline_config::current_version::YagaPipelineConfig>
      yaga = std::nullopt;
  /// Конфиг для yaga-metrolog
  ::std::optional<
      ::geo_pipeline_config::current_version::MetrologPipelineConfig>
      yaga_metrolog = std::nullopt;

  std::string yagr_channel_name =
      "channel-yagr-" + std::to_string(pipeline_number_);
  handlers::libraries::geobus_channel_config::ChannelConfig yagr_config{
      "channel:yagr:" + std::to_string(pipeline_number_), "taxi-passing"};
  std::string yaga_channel_name =
      "channel-yaga-" + std::to_string(pipeline_number_);
  handlers::libraries::geobus_channel_config::ChannelConfig yaga_config{
      "channel:yaga:" + std::to_string(pipeline_number_), "taxi-passing"};

  if (enable_yagr) {
    input = ::geo_pipeline_config::current_version::InputPipelineConfig{};
    channels_list.extra[yagr_channel_name] = yagr_config;
  }
  if (enable_yaga) {
    yaga = ::geo_pipeline_config::current_version::YagaPipelineConfig{
        {{{yagr_channel_name, {}, {}}}}};
    channels_list.extra[yaga_channel_name] = yaga_config;
  }
  if (enable_yaga_metrolog) {
    yaga_metrolog =
        ::geo_pipeline_config::current_version::MetrologPipelineConfig{
            {
                yagr_channel_name,
                yaga_channel_name,
            },
            "metrolog-key-" + std::to_string(pipeline_number_)};
    channels_list.extra[yagr_channel_name] = yagr_config;
    channels_list.extra[yaga_channel_name] = yaga_config;
  }

  PipelineConfig config{channels_list, std::nullopt, input, yaga,
                        yaga_metrolog};
  ++pipeline_number_;

  return config;
}
