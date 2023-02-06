#include "testsuite_total.hpp"

namespace order_metrics::collectors::order_events {

CollectorReturn TestsuiteTotal::GetMetrics(
    const OrderEventsMessage& message) const {
  if (message.is_testsuite) {
    Metric metric("testsuite_total");

    metric.AddLabel("city", message.nz);
    metric.AddLabel("payment_type", message.payment_type);

    return {metric};
  }
  return {};
}

}  // namespace order_metrics::collectors::order_events
