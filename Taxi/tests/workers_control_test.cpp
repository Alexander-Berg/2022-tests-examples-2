#include "matching_fixture_plugin.hpp"
#include "tracks_collection.hpp"

#include <internal/experiments/experiments_test.hpp>
#include <internal/workers_control.hpp>
#include <types/driver_id_key.hpp>

#include <geometry/position.hpp>
#include <graph/tests/graph_fixture.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/logging/logger.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <boost/filesystem.hpp>

namespace yaga::test {

class WorkersControlTestFixture : public ::graph::test::GraphTestFixture,
                                  public MapmatcherFixturePlugin {
 protected:
  using Queue = internal::AdjustWorker::Queue;
  using AdjustWorker = internal::AdjustWorker;
  using WorkersControl = internal::WorkersControl;
  using AdjustWorkerSync = internal::AdjustWorkerSync;
  using DriverIdKey = internal::DriverIdKey;
  virtual void SetUp() override;
  virtual void TearDown() override;

  /// Access WorkersControl object. Object will be created after calling
  /// StartWorkersControl
  auto& GetWorkersControl() { return *workers_control_; }

  NTaxi::NGraph2::TPositionOnGraph GetLastDriverPosition(
      const DriverIdKey& driver_id);

  void SendTrack(const DriverIdKey& driver_id,
                 const TracksCollection::TrackName track_name);
  // Launches workers control
  // This method must be called in test, insed RunInCoro
  void StartWorkersControl(const size_t workers_count = 2);
  void StopWorkersControl();

  static auto Graph() { return ::graph::test::GraphTestFixture::GetGraph(); }

  static auto MatcherCache() {
    return ::graph::test::GraphTestFixture::GetMatcherCache();
  }

  static auto PersistentIndex() {
    return ::graph::test::GraphTestFixture::GetPersistentIndex();
  }

 private:
  std::unique_ptr<WorkersControl> workers_control_;
  std::unique_ptr<NTaxi::NMapMatcher2::TMatcherConfig> matcher_config_;
  NTaxi::NMapMatcher2::TFilterConfig filter_config_;
  std::shared_ptr<internal::ExperimentsBase> exp_;
  std::shared_ptr<internal::LoggerStream> raw_positions_logger_;
  std::shared_ptr<internal::LoggerStream> matcher_logger_;
};

void WorkersControlTestFixture::SetUp() {
  MapmatcherFixturePlugin::PluginSetUp();
  ASSERT_NE(nullptr, Graph());
  ASSERT_NE(nullptr, MatcherCache());
  matcher_config_ = CreateMatcherConfig();
}

void WorkersControlTestFixture::StartWorkersControl(
    const size_t workers_count) {
  using namespace driver_id::literals;
  ASSERT_NE(0, workers_count);
  exp_ = std::make_shared<internal::TestExperiments>();
  raw_positions_logger_ = std::make_shared<internal::LoggerStream>(
      logging::MakeStderrLogger("test-raw-positions", logging::Level::kInfo));
  matcher_logger_ = std::make_shared<internal::LoggerStream>(
      logging::MakeStderrLogger("test-matcher", logging::Level::kInfo));
  workers_control_ = std::make_unique<WorkersControl>(
      Graph(), MatcherCache(), workers_count, *matcher_config_, filter_config_,
      true, exp_, std::chrono::minutes(0), [](const auto&) { return "test"; },
      raw_positions_logger_, DriverIdKey{"uuid"_uuid, "clid1"_dbid},
      *PersistentIndex(), matcher_logger_);
  engine::Yield();
  engine::Yield();
  ASSERT_NE(nullptr, workers_control_);
}

void WorkersControlTestFixture::StopWorkersControl() {
  ASSERT_NE(nullptr, workers_control_);
  workers_control_->CancelWorkers();
  workers_control_ = nullptr;
}

void WorkersControlTestFixture::TearDown() {
  MapmatcherFixturePlugin::PluginTearDown();
}

void WorkersControlTestFixture::SendTrack(
    const DriverIdKey& driver_id,
    const TracksCollection::TrackName track_name) {
  // Write to queue
  for (const auto& signal : TracksCollection::GetTrack(track_name)) {
    internal::DriverPositionMessage pos{
        {driver_id.GetUuid(), driver_id.GetDbid()},
        signal,
        internal::SpecialAction::kNoAction,
        std::make_shared<internal::Pipeline>("dummy_pipeline",
                                             std::vector<int>{0}, "Adjusted")};
    workers_control_->SyncProcessPoint(pos);
  }
}

TEST_F(WorkersControlTestFixture, TestStart) {
  RunInCoro(
      [this]() {
        ASSERT_NO_FATAL_FAILURE(StartWorkersControl());
        ASSERT_NO_FATAL_FAILURE(StopWorkersControl());
      },
      3);
}

TEST_F(WorkersControlTestFixture, TestDistribute) {
  using namespace driver_id::literals;
  RunInCoro(
      [this]() {
        DriverIdKey driver_1{"uuid"_uuid, "clid1"_dbid};
        DriverIdKey driver_2{"uuid"_uuid, "clid2"_dbid};

        static constexpr const size_t workers_count = 2;

        ASSERT_NO_FATAL_FAILURE(StartWorkersControl(workers_count));

        // We need drivers with such hashes, that they will be assigned to
        // different workers. Instead of calculating what string constants will
        // have required hash value, I just 'guessed' them and put an assert to
        // ensure this invariant remains.

        ASSERT_NE(driver_1.Hash() % workers_count,
                  driver_2.Hash() % workers_count);

        SendTrack(driver_1, TracksCollection::kStatisticsTrack);
        SendTrack(driver_2, TracksCollection::kStatisticsTrack);

        auto worker_stats = GetWorkersControl().GetWorkersStatistics();
        for (const auto& stats : worker_stats) {
          EXPECT_GE(stats.main.out_of_order.Load(), 1);
          EXPECT_GE(stats.main.frozen_time.Load(), 2);
          EXPECT_GE(stats.main.rejected.Load(), 2);
        }

        ASSERT_NO_FATAL_FAILURE(StopWorkersControl());
      },
      3);
}

}  // namespace yaga::test
