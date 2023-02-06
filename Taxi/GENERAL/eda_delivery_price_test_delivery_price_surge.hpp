#pragma once

#include <string>

#include <handlers/dependencies_fwd.hpp>
#include <stq/models/eda_delivery_price_test_delivery_price_surge.hpp>

namespace stq_tasks::eda_delivery_price_test_delivery_price_surge {

class Performer {
 public:
  static void Perform(TaskDataParsed&& task,
                      handlers::Dependencies&& dependencies);
};

}  // namespace stq_tasks::eda_delivery_price_test_delivery_price_surge
