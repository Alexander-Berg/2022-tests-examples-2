#include "worker_test.hpp"

#include <statistics/pipeline_tracking.hpp>

#include <gtest/gtest.h>

namespace yaga::statistics {

struct PipelineTrackingTester {
  using PositionTracking = PipelineTracking::PositionTracking;
  /// Access to default signal value
  static const auto& SignalValue() { return PipelineTracking::signal_value; }
  /// Access to tracking object ids
  /// @{
  static const auto& TrackingDriverId() {
    return PipelineTracking::kTrackingDriverId;
  }
  static const auto& TrackingDriverIdKey() {
    return PipelineTracking::kTrackingDriverIdKey;
  }
  /// @}

  /// Get copy of current PositionTracking object for this id (encoded as
  /// timestamp)
  std::optional<PositionTracking> GetTrackingObject(
      const PipelineTracking& tracking,
      std::chrono::system_clock::time_point timestamp) const {
    return tracking.GetTrackingObject(timestamp);
  }
};

class PipelineTrackingFixture : public ::testing::Test,
                                public PipelineTrackingTester {
 protected:
  /// Access to PipelineTracking object
  PipelineTracking& Tracking() { return tracking_; }

  /// Get copy of current PositionTracking object for this id (encoded as
  /// timestamp)
  std::optional<PositionTracking> GetTrackingObject(
      std::chrono::system_clock::time_point timestamp) const {
    return PipelineTrackingTester::GetTrackingObject(tracking_, timestamp);
  }

  NTaxi::NMapMatcher2::TTimedPositionOnEdge ToTimedPositionOnEdge(
      const ::geobus::types::UniversalSignals& pos);

 private:
  PipelineTracking tracking_;
};

NTaxi::NMapMatcher2::TTimedPositionOnEdge
PipelineTrackingFixture::ToTimedPositionOnEdge(
    const ::geobus::types::UniversalSignals& pos) {
  NTaxi::NMapMatcher2::TTimedPositionOnEdge result;
  result.Timestamp = std::chrono::system_clock::to_time_t(pos.client_timestamp);

  return result;
}

/// Test that consecutivly created objects has different timestamp
/// (tracking object id is stored as timestamp)
TEST_F(PipelineTrackingFixture, Creation) {
  RunInCoro(
      [this]() {
        auto first = Tracking().CreateNextTrackingObject();
        auto second = Tracking().CreateNextTrackingObject();

        EXPECT_NE(first.client_timestamp, second.client_timestamp);

        auto tracking_object = GetTrackingObject(first.client_timestamp);

        ASSERT_NE(std::nullopt, tracking_object);
        EXPECT_NE(std::chrono::steady_clock::time_point::min(),
                  tracking_object->created);
      },
      2);
}

TEST_F(PipelineTrackingFixture, UniversalSignalsPipeline) {
  RunInCoro(
      [this]() {
        auto first = Tracking().CreateNextTrackingObject();

        EXPECT_EQ(PipelineTracking::Success,
                  Tracking().MarkAsPublishedToUniversalSignals(first));

        auto tracking_object = GetTrackingObject(first.client_timestamp);

        ASSERT_NE(std::nullopt, tracking_object);
        EXPECT_NE(std::chrono::steady_clock::time_point::min(),
                  tracking_object->universal_signals_published);
        EXPECT_FALSE(tracking_object->IsFinished());
      },
      2);
}

TEST_F(PipelineTrackingFixture, PublisherStartStage) {
  RunInCoro(
      [this]() {
        auto first = Tracking().CreateNextTrackingObject();

        EXPECT_EQ(PipelineTracking::Success,
                  Tracking().MarkAsEnteredPublisherStage(
                      TrackingDriverIdKey(), ToTimedPositionOnEdge(first)));

        auto tracking_object = GetTrackingObject(first.client_timestamp);

        ASSERT_NE(std::nullopt, tracking_object);
        EXPECT_NE(std::chrono::steady_clock::time_point::min(),
                  tracking_object->publishing_started);
        EXPECT_FALSE(tracking_object->IsFinished());
      },
      2);
}

TEST_F(PipelineTrackingFixture, Finished) {
  RunInCoro(
      [this]() {
        auto first = Tracking().CreateNextTrackingObject();

        EXPECT_EQ(PipelineTracking::Success,
                  Tracking().MarkAsPublishedToUniversalSignals(first));

        EXPECT_EQ(PipelineTracking::Success,
                  Tracking().MarkAsEnteredPublisherStage(
                      TrackingDriverIdKey(), ToTimedPositionOnEdge(first)));

        auto tracking_object = GetTrackingObject(first.client_timestamp);

        // Should be removed as finished
        ASSERT_EQ(std::nullopt, tracking_object);
      },
      2);
}

TEST_F(PipelineTrackingFixture, Stats) {
  RunInCoro(
      [this]() {
        auto first = Tracking().CreateNextTrackingObject();

        ASSERT_NO_THROW(Tracking().GetStatistics());
        auto stats = Tracking().GetStatistics(std::chrono::minutes{1});

        ASSERT_NO_THROW(stats.GetJsonStatistics());
      },
      2);
}

/////////////////////////////////////////////////////////////////////////
/// Tests for various subsystems handling tracking objects
class PipelineTrackingWorkerFixture : public test::WorkerTestFixture,
                                      public PipelineTrackingTester {
 public:
  /// Access to PipelineTracking object
  PipelineTracking& Tracking() { return tracking_; }

 private:
  PipelineTracking tracking_;
};

/// Worker should correctly process points with tracking objects
TEST_F(PipelineTrackingWorkerFixture, WorkerProcessing) {
  RunInCoro([this]() {
    DriverIdKey driver_id{PipelineTracking::kTrackingUuid,
                          PipelineTracking::kTrackingDbid};
    // Make a track of tracking signals
    test::TracksCollection::Track test_track;
    auto consumer = std::make_shared<StoringConsumer>();
    for (size_t i = 0; i < 10; ++i) {
      test_track.push_back(
          Tracking().CreateNextTrackingObject().signals.front().geo_signal);
    }
    GetWorker().AddAdjustmentConsumer(consumer);

    SendTrack(driver_id, test_track);
    // Consumer must have received some data.
    const auto& received_data = consumer->data[driver_id];
    EXPECT_EQ(test_track.size(), received_data.current_positions.size());
    std::cerr << "Test finished" << std::endl;
  });
}

}  // namespace yaga::statistics
