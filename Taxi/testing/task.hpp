#pragma once

#include <js-pipeline/execution/task.hpp>
#include <js-pipeline/testing/context.hpp>

namespace js_pipeline::testing {

// TODO(EFFICIENCYDEV-12853): Consider making testing task not cachable
class Task : public execution::Task {
 public:
  Task(ContextPtr, std::chrono::seconds cache_max_unused_time,
       const std::string& test, const std::string& testcase);

  void InitializeState() const override;
};

}  // namespace js_pipeline::testing
