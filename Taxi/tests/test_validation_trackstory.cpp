#include <userver/utest/utest.hpp>

#include <geo-pipeline/validation_types.hpp>

#include <processing/validator.hpp>

namespace {
namespace cv = ::geo_pipeline_config::current_version;
using GeoPipelineConfig = cv::PipelineConfig;
using ErrorCode = geo_pipeline::ErrorCode;
}  // namespace
