#include <geo-pipeline/config/config_storage.hpp>

class DiffListener final {
 public:
  using GeoPipelineConfigDiff = geo_pipeline::config::GeoPipelineConfigDiff<
      geo_pipeline_config::PipelineTypesOfVersion<3>>;

  void Callback(const GeoPipelineConfigDiff& diff) { diff_ = diff; }

  const auto& GetDiff() const { return diff_; }

 private:
  GeoPipelineConfigDiff diff_;
};
