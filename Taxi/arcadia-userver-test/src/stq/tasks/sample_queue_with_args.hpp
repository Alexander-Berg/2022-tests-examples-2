#pragma once

#include <string>

#include <handlers/dependencies.hpp>
#include <stq/models/sample_queue_with_args.hpp>

namespace stq_tasks::sample_queue_with_args {

class Performer {
 public:
  static void Perform(TaskDataParsed&& task,
                      handlers::Dependencies&& dependencies);
};

}  // namespace stq_tasks::sample_queue_with_args
