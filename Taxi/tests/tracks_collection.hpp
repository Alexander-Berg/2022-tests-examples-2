#pragma once

#include <gpssignal/gps_signal.hpp>

#include <array>
#include <vector>

namespace yaga::test {

/// This is a collection of tracks for various testing needs.
/// To add new track, use a convinient script from repository tools-py3,
/// taxi-graph/scripts to convert JSON file with track to c++ code.
class TracksCollection {
 public:
  /// Sequence of signals
  using Track = std::vector<::gpssignal::GpsSignal>;
  // Enum with track 'names'. Usefull for data-driven unit-test
  enum TrackName {
    kSelfTestTrack,
    // Some simple track, without caveats
    kSimpleTrack1,
    // Tracks for statistics, with predefined number of
    // standing in place, out of order and other points.
    kStatisticsTrack,

    /// Track suitable for testing 'discard old saved pos' functionality.
    kDiscardOldSavedPosTrack,

    /// Track entirely in far far future
    kDiscardFuturePosTrack,

    /// Basically it's Discard Future track separated into 2 parts and with
    /// normal time
    kFirstTrackForSwitchingMatcherTypes,
    kSecondTrackForSwitchingMatcherTypes,

    kTrackNameSize
  };

  /// Return requested track
  static constexpr const Track& GetTrack(const TrackName track_name) {
    return tracks_[track_name];
  }

  /// Return the requested track, template-based
  template <TrackName Name>
  static const Track& GetTrack() {
    return std::get<Name>(tracks_);
  }

 private:
  static const std::array<const Track, kTrackNameSize> tracks_;
};

}  // namespace yaga::test
