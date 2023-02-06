#pragma once

#include "collectors/collector.hpp"
#include "models/order_events_message.hpp"

namespace order_metrics::collectors::order_events {

using models::messages::OrderEventsMessage;

class TestsuiteTotal final : public Collector<OrderEventsMessage> {
 public:
  CollectorReturn GetMetrics(const OrderEventsMessage& message) const override;
};

}  // namespace order_metrics::collectors::order_events
