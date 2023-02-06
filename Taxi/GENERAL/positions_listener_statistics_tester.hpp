#include <geobus/channels/positions/listener_statistics.hpp>

#include "listener_statistics_tester.hpp"

namespace geobus::statistics {

/// Tester helper for ListenerStatistics
struct PositionsListenerStatisticsTester
    : public ListenerStatisticsTesterLegacy {
  PositionsListenerStatisticsTester(const PositionsListenerStatistics& data_)
      : ListenerStatisticsTesterLegacy(data_), data(data_) {}

  /// Hold a reference to data.
  const PositionsListenerStatistics& data;

  auto GetReceivedPositions() const { return data.GetReceivedPositions(); }
};

}  // namespace geobus::statistics
