#include "tracks_collection.hpp"

#include <gtest/gtest.h>

namespace yaga::test {

using boost::units::si::meter_per_second;
using boost::units::si::meters_per_second;
using std::chrono::system_clock;
using namespace ::geometry::literals;
using namespace std::chrono_literals;

const auto kFutureStart = std::chrono::system_clock::now() + 100000h;

constexpr const auto kStartTimeInSeconds = 1514764800;
const auto kNowStart =
    std::chrono::system_clock::from_time_t(kStartTimeInSeconds);

// clang-format off
const std::array<const TracksCollection::Track,
                 TracksCollection::kTrackNameSize>
    TracksCollection::tracks_{{
      // latitude longitude speed accuracy direction timestamp
      // kSelfTestTrack
      {
        {0.0_lat, 0.0_lon, std::nullopt, std::nullopt, std::nullopt, system_clock::from_time_t(0)},
        {0.0_lat, 4.0_lon, std::nullopt, std::nullopt, std::nullopt, system_clock::from_time_t(0)}
      },
      // kSimpleTrack1
      {{
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764800) },
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764807) },
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764809) },
        { 55.720206_lat, 37.697820_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764815) },
        { 55.719651_lat, 37.695893_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764823) },
        { 55.719230_lat, 37.694498_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764828) },
        { 55.718765_lat, 37.694135_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764831) },
        { 55.718316_lat, 37.694035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764834) },
        { 55.717985_lat, 37.692801_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764839) },
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764846) }
      }},
      // kStatisticsTrack
      {{
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764800) },
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764800) }, // standing in place
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764807) },
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764801) }, // out of order
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764809) },
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764809) }, // standing in place
        { 55.720206_lat, 37.697820_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764815) },
        { 55.719651_lat, 37.695893_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764823) },
        { 55.719230_lat, 37.694498_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764828) },
        { 55.718765_lat, 37.694135_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764831) },
        { 55.718316_lat, 37.694035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764834) },
        { 55.717985_lat, 37.692801_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764839) },
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764846) },
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764847) }, // rejected, same pos, 1 sec diff
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764848) } // rejected, same reason
      }},
      // kDiscardOldSavedPosTrack. Should not have positions with diff in timestamp < 3
      {{
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764800) },
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764807) },
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764810) },
        { 55.720206_lat, 37.697820_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764815) },
        { 55.719651_lat, 37.695893_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764823) },
        { 55.719230_lat, 37.694498_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764828) },
        { 55.718765_lat, 37.694135_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764831) },
        { 55.718316_lat, 37.694035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764834) },
        { 55.717985_lat, 37.692801_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764839) },
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, system_clock::from_time_t(1514764846) }
      }},
      // kDiscardFuturePosTrack
      {{
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart },
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+7s },
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+9s },
        { 55.720206_lat, 37.697820_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+15s },
        { 55.719651_lat, 37.695893_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+23s },
        { 55.719230_lat, 37.694498_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+28s },
        { 55.718765_lat, 37.694135_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+31s },
        { 55.718316_lat, 37.694035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+34s },
        { 55.717985_lat, 37.692801_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+39s },
        { 55.717540_lat, 37.690895_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kFutureStart+46s }
      }},

      /// TODO(unlimiq): make normal tracks

      // kFirstTrackForSwitchingMatcherTypes
      {{
        { 55.721591_lat, 37.698035_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart },
        { 55.720928_lat, 37.699561_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart+7s },
        { 55.720603_lat, 37.699380_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart+9s }
      }},
      // kSecondTrackForSwitchingMatcherTypes
      {{
        { 55.720206_lat, 37.697820_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart+15s },
        { 55.719651_lat, 37.695893_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart+23s },
        { 55.719230_lat, 37.694498_lon, 16.6 * meter_per_second, std::nullopt, std::nullopt, kNowStart+28s }
      }}
      // To add new track, use a script from repo tools-py3, taxi-graph/scripts to convert JSON file with track to C++ code
    }};

// clang-format on

TEST(TracksCollectionFixture, SelfTest) {
  const auto& self_test_track =
      TracksCollection::GetTrack<TracksCollection::kSelfTestTrack>();
  EXPECT_EQ(2, self_test_track.size());
  EXPECT_EQ(0.0_lat, self_test_track[0].latitude);
  EXPECT_EQ(0.0_lon, self_test_track[0].longitude);
  EXPECT_EQ(0.0_lat, self_test_track[1].latitude);
  EXPECT_EQ(4.0_lon, self_test_track[1].longitude);
}

}  // namespace yaga::test
