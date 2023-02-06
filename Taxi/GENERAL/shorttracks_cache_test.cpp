#include <trackstory-shared/types.hpp>
#include <trackstory-shorttracks/shorttracks_cache.hpp>
#include <trackstory-shorttracks/track.hpp>

#include <algorithm>
#include <geobus/channels/edge_positions/edge_positions_generator.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include "shorttracks_tester.hpp"

using geobus::generators::EdgePositionsGenerator;
using geobus::generators::PositionsGenerator;
using gpssignal::test::GpsSignalTestPlugin;
using TimePoint = std::chrono::system_clock::time_point;

UTEST(ShortTracksCache, TestAddAndClearAdjustTracks) {
  trackstory::shorttracks::ShortTracksCache cache;
  trackstory::shorttracks::ShortTracksCacheTester cache_tester(cache);
  TimePoint first_timestamp{std::chrono::milliseconds{500}};
  TimePoint second_timestamp{std::chrono::milliseconds{550}};
  TimePoint third_timestamp{std::chrono::milliseconds{1000}};
  std::chrono::seconds max_age{150};

  ::geobus::types::Message<::geobus::types::DriverEdgePosition> payload;
  auto pos1 = EdgePositionsGenerator::CreateValidEdgePosition(5);
  pos1.timestamp = first_timestamp;
  payload.data.push_back(pos1);

  pos1.timestamp = second_timestamp;
  payload.data.push_back(pos1);

  auto pos2 = EdgePositionsGenerator::CreateValidEdgePosition(15);
  pos2.timestamp = third_timestamp;
  payload.data.push_back(pos2);

  utils::datetime::MockNowSet(third_timestamp);

  cache.ProcessEdgePayload(std::move(payload));

  EXPECT_EQ(2, cache.Size());

  /// set max age more than 15 seconds than first point of first driver,
  /// so track fo first driver gonna contain only one point.
  utils::datetime::MockNowSet(
      TimePoint{first_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto raw_track = driver_1_track->raw_track.Lock();
    auto adjusted_track = driver_1_track->adjusted_track.Lock();

    EXPECT_EQ(1, adjusted_track->size());
    EXPECT_EQ(0, raw_track->size());

    EXPECT_EQ(50ull, adjusted_track->GetCapacity());
    EXPECT_EQ(0ull, raw_track->GetCapacity());
  }

  /// set max age more than 15 seconds than all points of first driver,
  /// so track fo first driver gonna become empty.
  utils::datetime::MockNowSet(
      TimePoint{second_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto raw_track = driver_1_track->raw_track.Lock();
    auto adjusted_track = driver_1_track->adjusted_track.Lock();

    EXPECT_EQ(0, adjusted_track->size());
    EXPECT_EQ(0, raw_track->size());

    EXPECT_EQ(0ull, adjusted_track->GetCapacity());
    EXPECT_EQ(0ull, raw_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto raw_track = driver_2_track->raw_track.Lock();
    auto adjusted_track = driver_2_track->adjusted_track.Lock();

    EXPECT_EQ(1, adjusted_track->size());
    EXPECT_EQ(0, raw_track->size());

    EXPECT_EQ(50ull, adjusted_track->GetCapacity());
    EXPECT_EQ(0ull, raw_track->GetCapacity());
  }

  utils::datetime::MockNowUnset();
}

UTEST(ShortTracksCache, EnsureOnlyFreshPoints) {
  trackstory::shorttracks::ShortTracksConfig config;
  config.max_age_seconds = std::chrono::seconds{2};
  config.max_alternatives_for_position_count = 10;
  config.max_alternatives_track_length = 5;
  config.max_points_count = 10;

  trackstory::shorttracks::ShortTracksCache cache;
  cache.SetConfig(config);

  trackstory::shorttracks::ShortTracksCacheTester cache_tester(cache);
  constexpr const size_t generated_drivers_count = 5;
  std::vector<TimePoint> timestamps;
  for (size_t i = 0; i < 10e3; ++i) {
    timestamps.push_back(TimePoint{std::chrono::seconds{i * 10}});
  }

  std::vector<::geobus::types::DriverId> generated_drivers_ids;
  ::geobus::types::Message<::geobus::types::DriverEdgePosition> payload;
  // more than max_alternatives_for_position_count for ensure stripping
  // unnecessary ones
  const size_t alternatives_count =
      4 * config.max_alternatives_for_position_count;
  for (size_t i = 0; i < generated_drivers_count; ++i) {
    auto position =
        EdgePositionsGenerator::CreateValidEdgePosition(i, alternatives_count);
    generated_drivers_ids.push_back(position.driver_id);
    for (const auto& timestamp : timestamps) {
      position.timestamp = timestamp;
      payload.data.push_back(position);
    }
  }
  utils::datetime::MockNowSet(TimePoint{timestamps.front()});
  cache.ProcessEdgePayload(std::move(payload));

  for (const auto& driver_id : generated_drivers_ids) {
    auto driver_track = cache.Find(driver_id);
    ASSERT_NE(nullptr, driver_track);

    auto raw_track_ptr = driver_track->raw_track.Lock();
    auto adjusted_track_ptr = driver_track->adjusted_track.Lock();
    auto adjusted_alternatives_ptr =
        driver_track->adjusted_alternatives_track.Lock();

    EXPECT_EQ(0, raw_track_ptr->size());
    EXPECT_EQ(config.max_points_count, adjusted_track_ptr->size());
    EXPECT_EQ(config.max_alternatives_track_length,
              adjusted_alternatives_ptr->size());

    // check we have only fresh ones
    auto timestamp_it = timestamps.rbegin();
    for (auto it = adjusted_alternatives_ptr->BeginFromMostRecentToOldest();
         it != adjusted_alternatives_ptr->EndFromMostRecentToOldest(); ++it) {
      EXPECT_EQ(it->timestamp, *timestamp_it);
      ++timestamp_it;
    }

    timestamp_it = timestamps.rbegin();
    for (auto it = adjusted_track_ptr->BeginFromMostRecentToOldest();
         it != adjusted_track_ptr->EndFromMostRecentToOldest(); ++it) {
      EXPECT_EQ(it->timestamp, *timestamp_it);
      ++timestamp_it;
    }
  }
}

UTEST(ShortTracksCache, TestAddAndClearAlternativeTracks) {
  trackstory::shorttracks::ShortTracksConfig config;
  config.max_age_seconds = std::chrono::seconds{2};
  config.max_alternatives_for_position_count = 10;
  config.max_alternatives_track_length = 5;

  trackstory::shorttracks::ShortTracksCache cache;
  cache.SetConfig(config);

  trackstory::shorttracks::ShortTracksCacheTester cache_tester(cache);
  constexpr const size_t generated_drivers_count = 5;
  std::vector<size_t> times = {5, 10, 15, 20, 25, 30, 35};
  std::vector<TimePoint> timestamps;
  for (const auto& time : times) {
    timestamps.push_back(TimePoint{std::chrono::seconds{time}});
  }

  std::vector<::geobus::types::DriverId> generated_drivers_ids;
  ::geobus::types::Message<::geobus::types::DriverEdgePosition> payload;
  // more than max_alternatives_for_position_count for ensuring that
  // unnecessary ones were stripped
  const size_t alternatives_count =
      4 * config.max_alternatives_for_position_count;
  for (size_t i = 0; i < generated_drivers_count; ++i) {
    auto position =
        EdgePositionsGenerator::CreateValidEdgePosition(i, alternatives_count);
    generated_drivers_ids.push_back(position.driver_id);
    for (const auto& timestamp : timestamps) {
      position.timestamp = timestamp;
      payload.data.push_back(position);
    }
  }

  // and add driver with only first timestamp point
  ::geobus::types::DriverId one_point_driver_id;
  {
    auto position = EdgePositionsGenerator::CreateValidEdgePosition(
        generated_drivers_count + 1, alternatives_count);
    one_point_driver_id = position.driver_id;
    position.timestamp = timestamps.front();
    payload.data.push_back(position);
  }

  struct PropertiesShouldBe {
    size_t adjusted_track_length = 0;
    size_t alternatives_track_length = 0;
    size_t alternatives_count = 0;
    size_t one_point_driver_adjusted_track_length = 0;
    size_t one_point_driver_alternatives_track_length = 0;
    size_t one_point_driver_alternatives_count = 0;
  };

  auto ensure_properties = [&generated_drivers_ids, &cache,
                            &one_point_driver_id](
                               const PropertiesShouldBe& should_be) {
    EXPECT_EQ(generated_drivers_count + 1, cache.Size());
    for (const auto& driver_id : generated_drivers_ids) {
      auto driver_track = cache.Find(driver_id);
      ASSERT_NE(nullptr, driver_track);

      auto raw_track_ptr = driver_track->raw_track.Lock();
      auto adjusted_track_ptr = driver_track->adjusted_track.Lock();
      auto adjusted_alternatives_ptr =
          driver_track->adjusted_alternatives_track.Lock();

      EXPECT_EQ(0, raw_track_ptr->size());
      EXPECT_EQ(should_be.adjusted_track_length, adjusted_track_ptr->size());
      EXPECT_EQ(should_be.alternatives_track_length,
                adjusted_alternatives_ptr->size());

      // ensure non-ascending sorting by log likelihood
      // i.e. likelihood of first element attains maximum value
      for (const auto& alternatives : adjusted_alternatives_ptr->points) {
        EXPECT_EQ(should_be.alternatives_count, alternatives.size());

        // https://en.cppreference.com/w/cpp/algorithm/is_sorted
        // A sequence is sorted with respect to a comparator comp if for
        // any iterator it pointing to the sequence and any non-negative
        // integer n such that it + n is a valid iterator pointing to an
        // element of the sequence, comp(*(it + n), *it) evaluates to
        // false.
        EXPECT_TRUE(std::is_sorted(
            alternatives.begin(), alternatives.end(),
            [](const auto& first, const auto& second) noexcept {
              return first.GetLogLikelihood() > second.GetLogLikelihood();
            }));
      }
    }
    {
      auto driver_track = cache.Find(one_point_driver_id);
      ASSERT_NE(nullptr, driver_track);

      auto raw_track_ptr = driver_track->raw_track.Lock();
      auto adjusted_track_ptr = driver_track->adjusted_track.Lock();
      auto adjusted_alternatives_ptr =
          driver_track->adjusted_alternatives_track.Lock();

      EXPECT_EQ(0, raw_track_ptr->size());
      EXPECT_EQ(should_be.one_point_driver_adjusted_track_length,
                adjusted_track_ptr->size());
      EXPECT_EQ(should_be.one_point_driver_alternatives_track_length,
                adjusted_alternatives_ptr->size());
      const auto& points = adjusted_alternatives_ptr->points;
      for (const auto& point_alternatives : points) {
        EXPECT_EQ(should_be.one_point_driver_alternatives_count,
                  point_alternatives.size());
      }
    }
  };
  utils::datetime::MockNowSet(TimePoint{timestamps.front()});
  cache.ProcessEdgePayload(std::move(payload));

  PropertiesShouldBe should_be;
  should_be.adjusted_track_length = timestamps.size();
  should_be.alternatives_track_length = config.max_alternatives_track_length;
  should_be.alternatives_count = config.max_alternatives_for_position_count;
  should_be.one_point_driver_adjusted_track_length = 1;
  should_be.one_point_driver_alternatives_track_length = 1;
  should_be.one_point_driver_alternatives_count =
      config.max_alternatives_for_position_count;

  ensure_properties(should_be);

  // here we should have in adjusted 5, 10, 15, 20, 25, 30, 35
  //                     in alternatives 15, 20, 25, 30, 35
  // i.e. last points w.r.t. max_alternatives_track_length and
  // max_points_count configs.
  // So if we set time to 5 (timestamps[0]) +
  // max_age, then there should be 6 points in adjusted and 5 points in
  // alternatives, because 'clean old tracks' will clear all tracks with
  // timestamp
  // <= 5 + max_age - max_age = 5.
  // 'One point' driver will be truncated.
  utils::datetime::MockNowSet(
      TimePoint{timestamps[0] + config.max_age_seconds});
  cache_tester.CleanOldTracks();

  should_be.one_point_driver_alternatives_track_length = 0;
  should_be.one_point_driver_adjusted_track_length = 0;
  should_be.adjusted_track_length = 6;
  should_be.alternatives_track_length = 5;

  ensure_properties(should_be);

  // Check total clear
  utils::datetime::MockNowSet(timestamps.back() + 2 * config.max_age_seconds);
  cache_tester.CleanOldTracks();
  // now each driver's tracks should be empty
  should_be.adjusted_track_length = 0;
  should_be.alternatives_track_length = 0;

  ensure_properties(should_be);

  utils::datetime::MockNowUnset();
}

UTEST(ShortTracksCache, TestAddAndClearRawTracks) {
  trackstory::shorttracks::ShortTracksCache cache;
  trackstory::shorttracks::ShortTracksCacheTester cache_tester(cache);
  TimePoint first_timestamp{std::chrono::milliseconds{500}};
  TimePoint second_timestamp{std::chrono::milliseconds{550}};
  TimePoint third_timestamp{std::chrono::milliseconds{1000}};
  std::chrono::seconds max_age{150};

  ::geobus::types::Message<::geobus::types::DriverPosition> payload;
  auto pos1 = PositionsGenerator::CreateDriverPosition(5);
  pos1.signal.timestamp = first_timestamp;
  payload.data.push_back(pos1);

  pos1.signal.timestamp = second_timestamp;
  payload.data.push_back(pos1);

  auto pos2 = PositionsGenerator::CreateDriverPosition(15);
  pos2.signal.timestamp = TimePoint{third_timestamp};
  payload.data.push_back(pos2);

  utils::datetime::MockNowSet(TimePoint{third_timestamp});
  cache.ProcessPayload(std::move(payload));

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto raw_track = driver_1_track->raw_track.Lock();
    auto adjusted_track = driver_1_track->adjusted_track.Lock();

    EXPECT_EQ(0, adjusted_track->size());
    EXPECT_EQ(2, raw_track->size());

    EXPECT_EQ(50ull, raw_track->GetCapacity());
  }

  /// set now more than 150 seconds than all points of first driver,
  /// so track fo first driver gonna become empty.
  utils::datetime::MockNowSet(
      TimePoint{first_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto raw_track = driver_1_track->raw_track.Lock();
    auto adjusted_track = driver_1_track->adjusted_track.Lock();

    EXPECT_EQ(0, adjusted_track->size());
    EXPECT_EQ(1, raw_track->size());

    EXPECT_EQ(0ull, adjusted_track->GetCapacity());
    EXPECT_EQ(50ull, raw_track->GetCapacity());
  }

  /// set now more than 150 seconds than all points of first driver,
  /// so track fo first driver gonna become empty.
  utils::datetime::MockNowSet(
      TimePoint{second_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto raw_track = driver_1_track->raw_track.Lock();
    auto adjusted_track = driver_1_track->adjusted_track.Lock();

    EXPECT_EQ(0, adjusted_track->size());
    EXPECT_EQ(0, raw_track->size());

    EXPECT_EQ(0ull, adjusted_track->GetCapacity());
    EXPECT_EQ(0ull, raw_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto raw_track = driver_2_track->raw_track.Lock();
    auto adjusted_track = driver_2_track->adjusted_track.Lock();

    EXPECT_EQ(0, adjusted_track->size());
    EXPECT_EQ(1, raw_track->size());

    EXPECT_EQ(0ull, adjusted_track->GetCapacity());
    EXPECT_EQ(50ull, raw_track->GetCapacity());
  }

  utils::datetime::MockNowUnset();
}

UTEST(ShortTracksCache, TestAddAndClearFullGeometryTracks) {
  trackstory::shorttracks::ShortTracksCache cache;
  trackstory::shorttracks::ShortTracksCacheTester cache_tester(cache);
  TimePoint first_timestamp{std::chrono::milliseconds{500}};
  TimePoint second_timestamp{std::chrono::milliseconds{550}};
  TimePoint third_timestamp{std::chrono::milliseconds{1000}};
  std::chrono::seconds max_age{5};

  ::geobus::types::Message<::geobus::types::DriverPosition> payload;
  auto pos1 = PositionsGenerator::CreateDriverPosition(5);
  pos1.signal.timestamp = first_timestamp;
  payload.data.push_back(pos1);

  pos1.signal.timestamp = second_timestamp;
  payload.data.push_back(pos1);

  auto pos2 = PositionsGenerator::CreateDriverPosition(15);
  pos2.signal.timestamp = TimePoint{third_timestamp};
  payload.data.push_back(pos2);

  utils::datetime::MockNowSet(TimePoint{third_timestamp});
  cache.ProcessFullGeometryPayload(std::move(payload));

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto full_geometry_track = driver_1_track->full_geometry_track.Lock();

    EXPECT_EQ(2, full_geometry_track->size());

    EXPECT_EQ(5ull, full_geometry_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto full_geometry_track = driver_2_track->full_geometry_track.Lock();

    EXPECT_EQ(1, full_geometry_track->size());

    EXPECT_EQ(5ull, full_geometry_track->GetCapacity());
  }

  /// set now more than 150 seconds than first points of first driver,
  /// so first point for first driver gonna deleted.
  utils::datetime::MockNowSet(
      TimePoint{first_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto full_geometry_track = driver_1_track->full_geometry_track.Lock();

    EXPECT_EQ(1, full_geometry_track->size());

    EXPECT_EQ(5ull, full_geometry_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto full_geometry_track = driver_2_track->full_geometry_track.Lock();

    EXPECT_EQ(1, full_geometry_track->size());

    EXPECT_EQ(5ull, full_geometry_track->GetCapacity());
  }

  /// set now more than 150 seconds than all points of first driver,
  /// so track for first driver gonna become empty.
  utils::datetime::MockNowSet(
      TimePoint{second_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto full_geometry_track = driver_1_track->full_geometry_track.Lock();

    EXPECT_EQ(0, full_geometry_track->size());

    EXPECT_EQ(0ull, full_geometry_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto full_geometry_track = driver_2_track->full_geometry_track.Lock();

    EXPECT_EQ(1, full_geometry_track->size());

    EXPECT_EQ(5ull, full_geometry_track->GetCapacity());
  }

  /// set now more than 150 seconds than all points for all drivers,
  /// so tracks for all drivers gonna become empty.
  utils::datetime::MockNowSet(
      TimePoint{third_timestamp + max_age + std::chrono::milliseconds(1)});
  cache_tester.CleanOldTracks();

  EXPECT_EQ(2, cache.Size());
  {
    auto driver_1_track = cache.Find(pos1.driver_id);
    ASSERT_NE(nullptr, driver_1_track);
    auto full_geometry_track = driver_1_track->full_geometry_track.Lock();

    EXPECT_EQ(0, full_geometry_track->size());

    EXPECT_EQ(0ull, full_geometry_track->GetCapacity());
  }
  {
    auto driver_2_track = cache.Find(pos2.driver_id);
    ASSERT_NE(nullptr, driver_2_track);
    auto full_geometry_track = driver_2_track->full_geometry_track.Lock();

    EXPECT_EQ(0, full_geometry_track->size());

    EXPECT_EQ(0ull, full_geometry_track->GetCapacity());
  }

  utils::datetime::MockNowUnset();
}
