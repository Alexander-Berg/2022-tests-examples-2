#pragma once

#include <internal/conversion.hpp>

#include <taxi/graph/libs/yaga_selector/selector_consumer.h>

namespace yaga::test {

struct Track {
  using TrackData = std::vector<internal::YagaPosition>;
  TrackData data;

  Track() = default;
  // Non-copyable, to prevent accidents. If you need to copy,
  // 'data' member is at your service.
  Track(const Track&) = delete;
  Track& operator=(const Track&) = delete;
  // Moving is ok.
  Track(Track&&) noexcept = default;
  Track& operator=(Track&&) noexcept = default;
  Track(const NTaxi::NYagaSelector::THypotheses& data);

  auto& GetMostRecentPosition() { return data.back(); }
  auto& GetOldestPosition() { return data.front(); }
  const auto& GetMostRecentPosition() const { return data.back(); }
  const auto& GetOldestPosition() const { return data.front(); }

  /// Add new element as newest position.
  template <typename... T>
  void EmplaceNewPosition(T&&... args) {
    data.emplace_back(std::forward<T>(args)...);
  }

  /// Remove X oldest positions
  void RemoveNOldest(const size_t n) {
    data.erase(data.begin(), data.begin() + std::min(n, data.size()));
  }

  bool empty() const { return data.empty(); }
  auto size() const { return data.size(); }
};

inline Track::Track(const NTaxi::NYagaSelector::THypotheses& data_) {
  data.emplace_back(internal::ConvertToYagaPosition(data_.Hypotheses.front(),
                                                    data_.Timestamp));
}

}  // namespace yaga::test
