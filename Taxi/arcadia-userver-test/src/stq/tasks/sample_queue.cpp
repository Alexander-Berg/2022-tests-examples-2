#include "stq/tasks/sample_queue.hpp"

#include "userver/logging/log.hpp"

#include <userver/logging/log.hpp>

namespace stq_tasks::sample_queue {

void Performer::Perform(const stq_dispatcher::models::TaskData& task,
                        handlers::Dependencies&& /*dependencies*/) {
  if (!task.args.IsArray()) {
    LOG_ERROR() << "sample_queue: args are not an array";
    throw std::runtime_error("bad args");
  }

  if (task.args[0].As<int>() != 42) {
    LOG_ERROR() << "sample_queue: incorrect args";
    throw std::runtime_error("bad args");
  }

  if (!task.kwargs.HasMember("some_arg")) {
    LOG_ERROR() << "sample_queue: kwargs must have some_arg";
    throw std::runtime_error("bad args");
  }

  if (task.kwargs["some_arg"].As<std::string>() != "some_value") {
    LOG_ERROR() << "sample_queue: some_arg must be some_value";
    throw std::runtime_error("bad args");
  }
}

}  // namespace stq_tasks::sample_queue
