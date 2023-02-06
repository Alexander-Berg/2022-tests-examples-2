#include "coro_fixture_plugin.hpp"
#include "matching_fixture_plugin.hpp"
#include "track.hpp"
#include "tracks_collection.hpp"

#include <internal/experiments/experiments_test.hpp>
#include <internal/pipeline.hpp>
#include <internal/worker.hpp>
#include <types/driver_id_key.hpp>
#include <utils/logger_adapter.hpp>

#include <graph/point_conversions.hpp>
#include <graph/tests/graph_fixture.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <boost/filesystem.hpp>

namespace yaga::test {

/// Convinient fixture to test worker. Use StartWorker and StopWorker
/// to launch it.
class WorkerTestFixture : public ::graph::test::GraphTestFixture,
                          public CoroutineFixturePlugin,
                          public MapmatcherFixturePlugin {
 public:
  using Queue = internal::AdjustWorker::Queue;
  using AdjustWorker = internal::AdjustWorker;
  using AdjustWorkerSync = internal::AdjustWorkerSync;
  using DriverIdKey = internal::DriverIdKey;
  /// This consumer stores every received object.
  struct StoringConsumer;
  /// Points with diff in lat and lon less then this threashold are considered
  /// identical.
  static constexpr const double kNearPointsThreashold = 0.003;
  void CoroSetUp() override;
  void CoroTearDown() override;

  /// Access to worker task.
  auto& GetWorkerTask() { return *worker_task_; }

  /// Access to Producer
  auto& GetProducer() { return producer_; }
  /// Access to Worker itself
  AdjustWorker& GetWorker() { return *worker_; }
  /// everything from worker's output is stored here
  const StoringConsumer& GetWorkerOutputStorage() { return *storing_consumer_; }

  auto& GetExperiments() { return *exp_; }

  /// Push point to worker and wait for completition
  void SyncPushPoint(
      std::unique_ptr<AdjustWorker::DriverPositionMessage>&& msg);
  void SyncPushMessage(const AdjustWorker::DriversPositionsMessage& message);

  /// Get last matched position for direvr
  /// @param driver_id Driver's id
  NTaxi::NGraph2::TPositionOnGraph GetCurrentDriverPosition(
      const DriverIdKey& driver_id);

  /// Push (synchroniously) all points from given track.
  void SendTrack(const DriverIdKey& driver_id,
                 const TracksCollection::TrackName track_name);
  void SendTrack(const DriverIdKey& driver_id,
                 const TracksCollection::Track& track);
  /// Push (synchronoiously) whole empty message that created at
  /// now() + time_delta
  void SendEmptyMessage(const std::chrono::seconds time_delta);
  /// This method must be called in test, in the beginning of RunInCoro
  void StartWorker();
  /// This method must be called in test, in the end of RunInCoro
  void StopWorker();

  static auto Graph() { return ::graph::test::GraphTestFixture::GetGraph(); }

  static auto MatcherCache() {
    return ::graph::test::GraphTestFixture::GetMatcherCache();
  }

  static auto PersistentIndex() {
    return ::graph::test::GraphTestFixture::GetPersistentIndex();
  }

 public:
  inline static const DriverIdKey TestDriverId{
      ::driver_id::DriverUuid("test_uuid"),
      ::driver_id::DriverDbid("test_dbid")};

 private:
  std::unique_ptr<AdjustWorker> worker_;
  std::shared_ptr<StoringConsumer> storing_consumer_;
  std::unique_ptr<engine::Task> worker_task_;
  std::shared_ptr<Queue> channel_;
  std::unique_ptr<Queue::Producer> producer_;
  std::unique_ptr<NTaxi::NMapMatcher2::TMatcherConfig> matcher_config_;
  NTaxi::NMapMatcher2::TFilterConfig filter_config_;
  std::shared_ptr<internal::TestExperiments> exp_;
  std::shared_ptr<internal::LoggerStream> raw_positions_logger_;
  std::shared_ptr<internal::LoggerStream> matcher_logger_;
};

/// This consumer stores every received object.
struct WorkerTestFixture::StoringConsumer
    : public yaga::internal::AdjustmentConsumer {
  /// All received data for a driver
  struct DriverData {
    std::vector<Track> current_positions;
  };

  // Data for every driver
  ::yaga::internal::DriverDataStorage<DriverData> data;

  virtual void ProcessCurrentBestPositions(
      const yaga::internal::DriverIdKey& driver_id,
      std::shared_ptr<yaga::internal::Pipeline>,
      const std::vector<internal::THypotheses>& last_best_positions) override {
    data[driver_id].current_positions.push_back(
        Track(last_best_positions.front()));
  }
};

template <typename T>
class WorkerConsumerTestFixture : public WorkerTestFixture {};

template <int V>
struct IntTypeWrapper {
  static constexpr const int Value = V;
};

}  // namespace yaga::test
