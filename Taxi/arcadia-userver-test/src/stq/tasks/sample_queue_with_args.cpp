#include "stq/tasks/sample_queue_with_args.hpp"

#include <userver/logging/log.hpp>

namespace stq_tasks::sample_queue_with_args {

void Performer::Perform(TaskDataParsed&& task, handlers::Dependencies&&) {
  if (!task.args.optional_arg.has_value()) {
    LOG_ERROR() << "sample_queue_with_args: optional_arg must be present";
    throw std::runtime_error("bad args");
  }
  LOG_INFO() << "Starting stq task: " << task.id
             << " with optional_arg=" << task.args.optional_arg;
}

}  // namespace stq_tasks::sample_queue_with_args
