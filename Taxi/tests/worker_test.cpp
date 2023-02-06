#include "worker_test.hpp"

#include <geometry/position.hpp>
#include <statistics/pipeline_tracking.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/logging/logger.hpp>
#include <userver/utils/mock_now.hpp>

#include <vector>

namespace yaga::test {

void WorkerTestFixture::CoroSetUp() {
  CoroutineFixturePlugin::CoroSetUp();
  MapmatcherFixturePlugin::PluginSetUp();
  ASSERT_NE(nullptr, Graph());
  ASSERT_NE(nullptr, MatcherCache());
  channel_ = AdjustWorker::Queue::Create();
  producer_ = std::make_unique<Queue::Producer>(channel_->GetProducer());
  matcher_config_ = CreateMatcherConfig();
  ASSERT_NO_FATAL_FAILURE(StartWorker());
}

void WorkerTestFixture::StartWorker() {
  ASSERT_EQ(nullptr, worker_task_) << "Can't launch worker second time";
  exp_ = std::make_shared<internal::TestExperiments>();
  raw_positions_logger_ = std::make_shared<internal::LoggerStream>(
      logging::MakeStderrLogger("test-raw-positions", logging::Level::kInfo));
  matcher_logger_ = std::make_shared<internal::LoggerStream>(
      logging::MakeStderrLogger("test-matcher", logging::Level::kInfo));
  worker_ = std::make_unique<AdjustWorker>(
      *Graph(), MatcherCache(), channel_->GetConsumer(), *matcher_config_,
      filter_config_, true, exp_, [](const auto&) { return "test"; },
      raw_positions_logger_, TestDriverId, *PersistentIndex(), matcher_logger_);
  storing_consumer_ = std::make_shared<StoringConsumer>();
  worker_->AddAdjustmentConsumer(storing_consumer_);
  worker_task_ = std::make_unique<engine::Task>(
      this->Async("TestAdjustWorkerRun", [this]() { GetWorker().Run(); }));
  // engine::Yield();
  // engine::Yield();
  ASSERT_TRUE(worker_task_->IsValid());
  ASSERT_TRUE(worker_task_->IsValid());
}

void WorkerTestFixture::StopWorker() {
  ASSERT_NE(nullptr, worker_task_);
  ASSERT_TRUE(worker_task_->IsValid());
  if (worker_task_->IsFinished()) {
    worker_task_ = nullptr;
    return;
  }
  worker_task_->RequestCancel();
  worker_task_->Wait();
  // Have to kill Task object now, or otherwise RunInCoro won't end.
  worker_task_ = nullptr;
}

void WorkerTestFixture::CoroTearDown() {
  if (worker_task_ != nullptr) {
    StopWorker();
  }
  MapmatcherFixturePlugin::PluginTearDown();
  // Kill worker before queue, because queue has assert that Consumer is
  // destroyed
  worker_ = nullptr;
  channel_ = nullptr;
  CoroutineFixturePlugin::CoroTearDown();
}

void WorkerTestFixture::SyncPushPoint(
    std::unique_ptr<AdjustWorker::DriverPositionMessage>&& msg) {
  ASSERT_NE(nullptr, worker_);
  AdjustWorkerSync* sync_object = worker_->SyncObject();
  ASSERT_NE(nullptr, sync_object);

  worker_->TestPushNextSignal(*msg);
}

void WorkerTestFixture::SyncPushMessage(
    const AdjustWorker::DriversPositionsMessage& message) {
  ASSERT_NE(nullptr, worker_);
  AdjustWorkerSync* sync_object = worker_->SyncObject();
  ASSERT_NE(nullptr, sync_object);

  worker_->TestPushMessage(message);
}

void WorkerTestFixture::SendTrack(
    const DriverIdKey& driver_id,
    const TracksCollection::TrackName track_name) {
  // Write to queue
  const auto track = TracksCollection::GetTrack(track_name);
  SendTrack(driver_id, track);
}

void WorkerTestFixture::SendTrack(const DriverIdKey& driver_id,
                                  const TracksCollection::Track& track) {
  auto it = track.begin();
  auto it_end = track.end() - 1;  // Last point will be send separaterly
  for (; it != it_end; ++it) {
    const auto& signal = *it;
    auto msg = std::make_unique<AdjustWorker::DriverPositionMessage>();
    msg->signal = signal;
    msg->driver_id = driver_id;
    SyncPushPoint(std::move(msg));

    ASSERT_TRUE(GetWorkerTask().IsValid());
  }

  ASSERT_NE(track.end(), it);

  // Requset force-matching with last point
  {
    // Use last track signal as data payload.
    auto msg = std::make_unique<AdjustWorker::DriverPositionMessage>();
    msg->signal = *it;
    msg->driver_id = driver_id;
    // This is the request to force match
    msg->special_action = ::yaga::internal::SpecialAction::kForceMatch;
    SyncPushPoint(std::move(msg));
  }
}

void WorkerTestFixture::SendEmptyMessage(
    const std::chrono::seconds time_delta) {
  const auto message{[&] {
    AdjustWorker::DriversPositionsMessage result;
    result.created = std::chrono::system_clock::now() + time_delta;
    return result;
  }()};

  SyncPushMessage(message);
}

NTaxi::NGraph2::TPositionOnGraph WorkerTestFixture::GetCurrentDriverPosition(
    const DriverIdKey& driver_id) {
  auto msg = std::make_unique<AdjustWorker::DriverPositionMessage>();
  msg->driver_id = driver_id;
  // This signal will be ignored because timestamp is 0. And anyway this method
  // is only for tests.
  msg->signal.latitude = 0 * ::geometry::lat;
  msg->signal.longitude = 0 * ::geometry::lon;
  msg->signal.timestamp = std::chrono::system_clock::from_time_t(0);
  msg->special_action = ::yaga::internal::SpecialAction::kForceMatch;

  worker_->TestPushNextSignal(*msg);

  return worker_->GetCurrentDriverPosition(driver_id);
}

TEST_F(WorkerTestFixture, TestStatistics) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    SendTrack(driver_id, TracksCollection::kStatisticsTrack);

    auto stats = GetWorker().GetStatistics();

    EXPECT_GE(stats.main.out_of_order.Load(), 1);
    EXPECT_GE(stats.main.frozen_time.Load(), 2);
    EXPECT_GE(stats.main.rejected.Load(), 2);
  });
}

TEST_F(WorkerTestFixture, TestStart) {
  RunInCoro([this]() { ASSERT_TRUE(GetWorkerTask().IsValid()); });
}

TEST_F(WorkerTestFixture, TestAdjust) {
  using namespace driver_id::literals;
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    SendTrack(driver_id, TracksCollection::kSimpleTrack1);

    auto pos = GetCurrentDriverPosition(driver_id);

    ASSERT_FALSE(pos.IsUndefined());

    auto coords = Graph()->GetCoords(pos);

    // This track is mostly along the road, so adjustment result should be near
    // it's end.
    ASSERT_NEAR(coords.Lon,
                TracksCollection::GetTrack<TracksCollection::kSimpleTrack1>()
                    .back()
                    .longitude.value(),
                kNearPointsThreashold);
    ASSERT_NEAR(coords.Lat,
                TracksCollection::GetTrack<TracksCollection::kSimpleTrack1>()
                    .back()
                    .latitude.value(),
                kNearPointsThreashold);

    // Check validity of edge_positions and adjust_tracks channels.

    // at least answer for last point sent into adjust_track  should have
    // exactly one point
    const auto fit = GetWorkerOutputStorage().data.find(driver_id);
    ASSERT_NE(GetWorkerOutputStorage().data.end(), fit);
    EXPECT_EQ(fit->second.current_positions.back().size(), 1);
  });
}

/// Test that tracking object is not discarded
TEST_F(WorkerTestFixture, TestTrackingObject) {
  RunInCoro([this]() {
    DriverIdKey driver_id{::yaga::statistics::PipelineTracking::kTrackingUuid,
                          ::yaga::statistics::PipelineTracking::kTrackingDbid};
    SendTrack(driver_id, TracksCollection::kSimpleTrack1);

    auto pos = GetCurrentDriverPosition(driver_id);

    ASSERT_FALSE(pos.IsUndefined());

    auto coords = Graph()->GetCoords(pos);

    // This track is mostly along the road, so adjustment result should be near
    // it's end.
    ASSERT_NEAR(coords.Lon,
                TracksCollection::GetTrack<TracksCollection::kSimpleTrack1>()
                    .back()
                    .longitude.value(),
                kNearPointsThreashold);
    ASSERT_NEAR(coords.Lat,
                TracksCollection::GetTrack<TracksCollection::kSimpleTrack1>()
                    .back()
                    .latitude.value(),
                kNearPointsThreashold);
  });
}

TEST_F(WorkerTestFixture, TestDiscardOld) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardOldSavedPositionSeconds(1);
    SendTrack(driver_id, TracksCollection::kDiscardOldSavedPosTrack);

    const auto stats = GetWorker().GetStatistics();
    // Will reset state for every point except last one
    EXPECT_EQ(
        stats.reset_as_too_old,
        TracksCollection::GetTrack<TracksCollection::kDiscardOldSavedPosTrack>()
                .size() -
            1);
  });
}

TEST_F(WorkerTestFixture, TestDiscardOldDisabled) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardOldSavedPositionSeconds(400000);  // set to 4 days.
    SendTrack(driver_id, TracksCollection::kDiscardOldSavedPosTrack);

    const auto stats = GetWorker().GetStatistics();
    // Will reset state for every point except last one
    EXPECT_EQ(0, stats.reset_as_too_old);
  });
}

TEST_F(WorkerTestFixture, TestDiscardFuture) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardFutureSeconds(600);
    SendTrack(driver_id, TracksCollection::kDiscardFuturePosTrack);

    const auto stats = GetWorker().GetStatistics();
    // Should discard every point
    EXPECT_EQ(
        stats.discarded_from_the_future,
        TracksCollection::GetTrack<TracksCollection::kDiscardFuturePosTrack>()
            .size());
  });
}

TEST_F(WorkerTestFixture, TestDiscardFutureDisabled) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardFutureSeconds(0);  // disable it
    SendTrack(driver_id, TracksCollection::kDiscardFuturePosTrack);

    const auto stats = GetWorker().GetStatistics();
    // Should discard no point
    EXPECT_EQ(0, stats.discarded_from_the_future);
  });
}

TEST_F(WorkerTestFixture, TestDiscardTooOldMessagesDiscards) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardTooOldSeconds(5);
    using namespace std::chrono_literals;
    SendEmptyMessage(-1000s);

    const auto stats = GetWorker().GetStatistics();
    // Message very old, we should discard it
    EXPECT_GT(stats.discarded_messages, 0);
  });
}

TEST_F(WorkerTestFixture, TestDiscardTooOldMessagesDoNotDiscards) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardTooOldSeconds(5);
    using namespace std::chrono_literals;
    SendEmptyMessage(0s);

    const auto stats = GetWorker().GetStatistics();
    // Fresh message, we should not discard it
    EXPECT_EQ(stats.discarded_messages, 0);
  });
}

TEST_F(WorkerTestFixture, TestDiscardTooOldMessagesDisabled) {
  RunInCoro([this]() {
    DriverIdKey driver_id{TestDriverId};
    GetWorker().SetDiscardTooOldSeconds(0);
    using namespace std::chrono_literals;
    SendEmptyMessage(-10000s);

    const auto stats = GetWorker().GetStatistics();
    // Message very old, but feature disabled, we should not discard it
    EXPECT_EQ(stats.discarded_messages, 0);
  });
}

TEST_F(WorkerTestFixture, TestCleanOldTracks) {
  using namespace std::chrono_literals;
  RunInCoro([this]() {
    auto current_time = ::utils::datetime::Now();

    DriverIdKey driver_id{TestDriverId};
    DriverIdKey another_driver_id{::driver_id::DriverUuid("test_uuid2"),
                                  ::driver_id::DriverDbid("test_dbid2")};
    ASSERT_NE(driver_id, another_driver_id);

    GetWorker().SetPeriodicCleaningInterval(100min);

    // send any data
    SendTrack(driver_id, TracksCollection::kSimpleTrack1);
    SendTrack(another_driver_id, TracksCollection::kStatisticsTrack);
    EXPECT_EQ(2, GetWorker().DriversCount());

    // now, set clean interval and move 'now' forward
    GetWorker().SetPeriodicCleaningInterval(1min);

    ::utils::datetime::MockNowSet(current_time + 20min);

    // cleaning will activate on next position only, so send position
    // for one of the drivers
    SendTrack(driver_id, TracksCollection::kSimpleTrack1);

    const auto stats = GetWorker().GetStatistics();
    // we should have cleaned old records for both drivers
    EXPECT_EQ(stats.cleaned_records, 2);
    // but one driver should have been added back by last call of
    // SendTrack
    EXPECT_EQ(1, GetWorker().DriversCount());

    ::utils::datetime::MockNowUnset();
  });
}

///////////////////////////////////////////////////////////////////////////
// Test switching adjust types
TEST_F(WorkerTestFixture, TestSwitchingAdjustTypes) {
  // Add new adjust types to vector "types" in order that
  // they appear in enum and add new track with greater time
  namespace NYS = NTaxi::NYagaSelector;
  using AdjustType = AdjustWorker::EAdjustType;
  const std::vector<NYS::TSelectorSettings> settings{
      {NYS::TYagaAdjustSettings{}},
      {NYS::TNearestEdgesSettings{}},
      {NYS::TYagaPredictSettings{}},
      {NYS::TMapPredictSettings{}},
      {NYS::TGuidanceSettings{}}};

  const std::vector<AdjustType> main_types{
      AdjustType::kYagaAdjust, AdjustType::kNearestEdgesAdjust,
      AdjustType::kYagaPredict, AdjustType::kMapPredict,
      AdjustType::kGuidanceAdjust};

  const std::vector<AdjustType> exp_types = main_types;

  ASSERT_TRUE(main_types.size() == exp_types.size());

  auto get_settings = [&](const AdjustType type) {
    return settings[static_cast<size_t>(type)];
  };

  // Check that exactly one paticular matcher processed signals
  auto check = [&](const AdjustType main_type,
                   const AdjustType experimental_type,
                   const TracksCollection::TrackName track_name) {
    DriverIdKey driver_id{TestDriverId};
    auto common_values = internal::Experiments::Values{};
    const auto initial_stats = GetWorker().GetStatistics();

    // Set init matcher type
    common_values.main = get_settings(main_type);
    common_values.experimental = get_settings(experimental_type);
    GetExperiments().SetResult(common_values);

    SendTrack(driver_id, track_name);

    // Check statistics
    const auto current_stats = GetWorker().GetStatistics();

    auto check_impl =
        [](const AdjustType type,
           const statistics::AdjustmentStatistics::ChannelStatistics& previous,
           const statistics::AdjustmentStatistics::ChannelStatistics& current) {
          switch (type) {
            case AdjustType::kYagaAdjust: {
              EXPECT_GT(current.yaga_adjust, previous.yaga_adjust);
              EXPECT_EQ(current.yaga_predict, previous.yaga_predict);
              EXPECT_EQ(current.nearest_edges_adjust,
                        previous.nearest_edges_adjust);
              EXPECT_EQ(current.map_predict, previous.map_predict);
              break;
            }
            case AdjustType::kYagaPredict: {
              EXPECT_EQ(current.yaga_adjust, previous.yaga_adjust);
              EXPECT_GT(current.yaga_predict, previous.yaga_predict);
              EXPECT_EQ(current.nearest_edges_adjust,
                        previous.nearest_edges_adjust);
              EXPECT_EQ(current.map_predict, previous.map_predict);
              break;
            }
            case AdjustType::kNearestEdgesAdjust: {
              EXPECT_EQ(current.yaga_adjust, previous.yaga_adjust);
              EXPECT_EQ(current.yaga_predict, previous.yaga_predict);
              EXPECT_GT(current.nearest_edges_adjust,
                        previous.nearest_edges_adjust);
              EXPECT_EQ(current.map_predict, previous.map_predict);
              break;
            }
            case AdjustType::kMapPredict: {
              EXPECT_EQ(current.yaga_adjust, previous.yaga_adjust);
              EXPECT_EQ(current.yaga_predict, previous.yaga_predict);
              EXPECT_EQ(current.nearest_edges_adjust,
                        previous.nearest_edges_adjust);
              EXPECT_GT(current.map_predict, previous.map_predict);
              break;
            }
            default:
              ASSERT_NO_FATAL_FAILURE();
          }
        };
    check_impl(main_type, initial_stats.main, current_stats.main);
    check_impl(experimental_type, initial_stats.experimental,
               current_stats.experimental);
  };
  for (const auto init_main : main_types) {
    for (const auto init_exp : exp_types) {
      for (const auto other_main : main_types) {
        for (const auto other_exp : exp_types) {
          RunInCoro([init_main, init_exp, other_main, other_exp, &check]() {
            /// Initial adjustment
            check(init_main, init_exp,
                  TracksCollection::kFirstTrackForSwitchingMatcherTypes);

            /// Change Settings and adjust again
            check(other_main, other_exp,
                  TracksCollection::kSecondTrackForSwitchingMatcherTypes);
          });
        }
      }
    }
  }
}

///////////////////////////////////////////////////////////////////////////
// Test consumers

using ConsumerVariationTypes = ::testing::Types<IntTypeWrapper<1>>;

TYPED_TEST_SUITE(WorkerConsumerTestFixture, ConsumerVariationTypes);

template <int ThrowIn>
struct StdThrowingConsumer : public yaga::internal::AdjustmentConsumer {
  template <int member_number>
  void ThrowIfTested() {
    if constexpr (ThrowIn == member_number) {
      throw std::logic_error("test_exception");
    }
  }

  virtual void ProcessCurrentBestPositions(
      const yaga::internal::DriverIdKey&,
      std::shared_ptr<yaga::internal::Pipeline>,
      const std::vector<yaga::internal::THypotheses>&) override {
    ThrowIfTested<1>();
  }
};

TYPED_TEST(WorkerConsumerTestFixture, TestStdConsumerException) {
  this->RunInCoro([this]() {
    auto consumer = std::make_shared<StdThrowingConsumer<TypeParam::Value>>();
    this->GetWorker().AddAdjustmentConsumer(consumer);
    yaga::internal::DriverIdKey driver_id{WorkerTestFixture::TestDriverId};
    ASSERT_NO_THROW(
        this->SendTrack(driver_id, TracksCollection::kSimpleTrack1););
    ASSERT_TRUE(this->GetWorkerTask().IsValid());
  });
}

// ThrowIn - throw exception in method number X
template <int ThrowIn>
struct IntThrowingConsumer : public yaga::internal::AdjustmentConsumer {
  template <int member_number>
  void ThrowIfTested() {
    if constexpr (ThrowIn == member_number) {
      throw 5;
    }
  }
  virtual void ProcessCurrentBestPositions(
      const yaga::internal::DriverIdKey&,
      std::shared_ptr<yaga::internal::Pipeline>,
      const std::vector<internal::THypotheses>&) override {
    ThrowIfTested<1>();
  }
};

TYPED_TEST(WorkerConsumerTestFixture, TestIntConsumerException) {
  this->RunInCoro([this]() {
    auto consumer = std::make_shared<IntThrowingConsumer<TypeParam::Value>>();
    this->GetWorker().AddAdjustmentConsumer(consumer);
    yaga::internal::DriverIdKey driver_id{WorkerTestFixture::TestDriverId};
    ASSERT_NO_THROW(
        this->SendTrack(driver_id, TracksCollection::kSimpleTrack1););
    ASSERT_TRUE(this->GetWorkerTask().IsValid());
  });
}

template <int CountIn>
struct CountingConsumer : public yaga::internal::AdjustmentConsumer {
  size_t count{0};
  template <int member_number>
  constexpr void CountIfTested() {
    if constexpr (CountIn == member_number) {
      count++;
    }
  }

  virtual void ProcessCurrentBestPositions(
      const yaga::internal::DriverIdKey&,
      std::shared_ptr<yaga::internal::Pipeline>,
      const std::vector<yaga::internal::THypotheses>&) override {
    CountIfTested<1>();
  }
};

TYPED_TEST(WorkerConsumerTestFixture, TestCountingConsumer) {
  this->RunInCoro([this]() {
    auto consumer = std::make_shared<CountingConsumer<TypeParam::Value>>();
    this->GetWorker().AddAdjustmentConsumer(consumer);
    yaga::internal::DriverIdKey driver_id{WorkerTestFixture::TestDriverId};
    this->SendTrack(driver_id, TracksCollection::kSimpleTrack1);
    ASSERT_GE(consumer->count, 0);
  });
}

}  // namespace yaga::test
