#include "stq/tasks/eda_delivery_price_test_delivery_price_surge.hpp"

#include <helpers/testing.hpp>
#include <views/v1/calc-delivery-price-surge/post/view.hpp>

namespace stq_tasks::eda_delivery_price_test_delivery_price_surge {

void Performer::Perform(TaskDataParsed&& task,
                        handlers::Dependencies&& dependencies) {
  using handlers::v1_calc_delivery_price_surge::post::View;
  auto& args = task.args;
  helpers::testing::ExecuteTest<View>(
      task.id, args.requests_count, std::move(args.headers.extra),
      std::move(args.payload.extra), std::move(dependencies));
}

}  // namespace stq_tasks::eda_delivery_price_test_delivery_price_surge
