#pragma once

#include <chrono>

namespace helpers::time {

using TimePoint = std::chrono::system_clock::time_point;

template <typename Time>
TimePoint CropTo(TimePoint tp) {
  auto dur = std::chrono::duration_cast<Time>(
      tp.time_since_epoch());
  return TimePoint(dur);
}

}  // namespace helpers::time
