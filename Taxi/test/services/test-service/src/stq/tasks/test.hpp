#pragma once

#include <string>

#include <handlers/dependencies_fwd.hpp>
#include <stq/models/test.hpp>

namespace stq_tasks::test {

class Performer {
 public:
  static void Perform(TaskDataParsed&& task,
                      handlers::Dependencies&& dependencies);
};

}  // namespace stq_tasks::test
