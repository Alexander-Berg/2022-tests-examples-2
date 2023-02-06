#include <geobus/statistics/listener_statistics.hpp>

namespace geobus::statistics {

/// Tester helper for ListenerStatisticsLegacy
struct ListenerStatisticsTesterLegacy {
  ListenerStatisticsTesterLegacy(const ListenerStatisticsLegacy& data_)
      : data(data_) {}

  /// Hold a reference to data.
  const ListenerStatisticsLegacy& data;

  auto GetReceivedMessages() const { return data.GetReceivedMessages(); }
};

/// Tester helper for ListenerStatistics
struct ListenerStatisticsTester {
  ListenerStatisticsTester(const ListenerStatistics& data_) : data(data_) {}

  /// Hold a reference to data.
  const ListenerStatistics& data;

  auto GetReceivedMessages() const { return data.GetReceivedMessages(); }
};

}  // namespace geobus::statistics
