#pragma once

#include <js-pipeline/compilation/codegen/builder.hpp>
#include <js-pipeline/compilation/parsing/pipeline/model.hpp>
#include <js-pipeline/models/handles.hpp>

namespace js_pipeline::compilation::codegen::pipeline_tests {

void Compile(const parsing::pipeline::Model&, Builder&,
             const models::PipelineTestRequest&);

}  // namespace js_pipeline::compilation::codegen::pipeline_tests
