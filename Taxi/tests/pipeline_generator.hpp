#include <geo-pipeline-config/types.hpp>

class PipelineGenerator {
 public:
  using PipelineConfig = ::geo_pipeline_config::current_version::PipelineConfig;
  PipelineConfig GeneratePipeline(bool enable_yagr = false,
                                  bool enable_yaga = false,
                                  bool enable_yaga_metrolog = false);

 private:
  size_t pipeline_number_ = 0;
};
