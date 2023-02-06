#pragma once

#include <chrono>
#include <string>

#include <stq/tasks_definitions/test.hpp>

namespace stq_tasks {
namespace test {

struct TaskDataParsed {
  std::string id;
  int exec_tries;
  int reschedule_counter;
  std::chrono::system_clock::time_point eta;
  Args args;
  std::optional<std::string> tag;
};

}  // namespace test
}  // namespace stq_tasks
