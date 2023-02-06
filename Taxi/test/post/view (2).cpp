#include "view.hpp"

#include <js-pipeline/testing/component.hpp>

#include <js-pipeline/generated/consumers.hpp>

#include <userver/logging/log.hpp>

namespace handlers::v1_js_pipeline_test::post {
namespace {
const std::string kInvalidPipelineError{"invalid_pipeline"};
namespace js_pipeline_consumers = js_pipeline::generated::consumers;
}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;
  try {
    return Response200{{dependencies.extra.js_test
                            .PerformTests<js_pipeline_consumers::LavkaSurgeTag>(
                                std::move(request.body))}};
  } catch (const std::exception& e) {
    Response400 response400;

    LOG_ERROR() << "Compile error in /pipeline/compile: " << e.what();
    response400.code = kInvalidPipelineError;
    response400.message = e.what();
    response400.x_yataxi_error_code = kInvalidPipelineError;

    return response400;
  }

  return response;
}
}  // namespace handlers::v1_js_pipeline_test::post
