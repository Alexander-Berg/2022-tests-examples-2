#pragma once

namespace geobus::test {

using PartitionData = geobus::subscription::SubscriptionStrategy::PartitionData;

template <typename PartitionedListenerType>
class PartitionedListenerTester {
 public:
  static void ResubscribeTo(PartitionedListenerType& listener,
                            const PartitionData& partitions) {
    listener.UpdateListenersSubscriptions(partitions);
  }
};

}  // namespace geobus::test
