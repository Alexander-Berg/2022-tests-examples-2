#pragma once

#include <string>

#include <handlers/dependencies.hpp>
#include <stq-dispatcher/models/task.hpp>

namespace stq_tasks::sample_queue {

class Performer {
 public:
  static void Perform(const stq_dispatcher::models::TaskData& task,
                      handlers::Dependencies&& dependencies);
};

}  // namespace stq_tasks::sample_queue
