#include "task.hpp"

#include <userver/formats/parse/common_containers.hpp>

#include <js-pipeline/compilation/conventions.hpp>
#include <js-pipeline/execution/types.hpp>

namespace js_pipeline::testing {
namespace {
const std::string kTestStatisticsDomain{"testing"};
}

Task::Task(ContextPtr context, std::chrono::seconds cache_max_unused_time,
           const std::string&, const std::string&)
    : execution::Task(std::move(context), cache_max_unused_time,
                      kTestStatisticsDomain) {}

void Task::InitializeState() const {
  InitializeStateImpl(/*init_resource_fetch=*/false);
}

}  // namespace js_pipeline::testing
