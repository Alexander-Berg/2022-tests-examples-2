#include <statistics/stat_counter.hpp>

#include <atomic>
#include <functional>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/utest/utest.hpp>

#include <taxi_config/variables/CARDSTORAGE_FALLBACK_CONFIG.hpp>

using namespace std::chrono_literals;

using Config =
    taxi_config::cardstorage_fallback_config::CardstorageFallbackConfig;

namespace cardstorage::tests {

namespace {

const int kMinimumEvents = 10;
const auto kInterval = 10s;
const auto kReadPeriod = 1s;
const auto kWritePeriod = 1s;

dynamic_config::StorageMock MakeConfig(
    std::function<void(Config&)> config_editor =
        [](Config&) { /* use defaults */ }) {
  Config config;
  config.fallback_rate = 0.5;
  config.minimum_events = kMinimumEvents;
  config.observation_interval_sec = kInterval;
  config.read_period_sec = kReadPeriod;
  config.write_period_sec = kWritePeriod;
  config.cleanup_period_sec = 30s;
  config.cleanup_threshold_sec = 20s;
  config_editor(config);
  return {{taxi_config::CARDSTORAGE_FALLBACK_CONFIG, config}};
}

}  // namespace

class MockStatCounter : public statistics::StatisticsCounter {
 public:
  using RequestRecord = statistics::RequestRecord;

  explicit MockStatCounter(const dynamic_config::Source& config_source)
      : StatisticsCounter(config_source) {
    Start();
  }

  ~MockStatCounter() { Stop(); }

  void SetDbRecords(const std::vector<RequestRecord>& new_stored_records) {
    stored_records = new_stored_records;
  }

  virtual std::vector<RequestRecord> ReadRecords() const override {
    read_records_called++;
    return stored_records;
  }

  virtual void WriteRecords(
      const std::vector<RequestRecord>& records) override {
    write_records_called++;
    records_written += records.size();
    for (const auto& record : records) {
      stored_records.push_back(record);
    }
  }

  virtual void DeleteOldRecords(
      std::chrono::system_clock::time_point) override {
    cleanup_called++;
  }

  using StatisticsCounter::CleanupSync;
  using StatisticsCounter::ReadSync;
  using StatisticsCounter::WriteSync;

 public:
  mutable std::atomic<std::uint64_t> read_records_called{0};
  std::atomic<std::uint64_t> write_records_called{0};
  std::atomic<std::uint64_t> records_written{0};
  std::atomic<std::uint64_t> cleanup_called{0};
  std::vector<RequestRecord> stored_records;
};

UTEST(TestStatCounter, TestMinimumEvents) {
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());
  for (int i = 0; i < kMinimumEvents - 1; ++i) {
    stat_counter.PutFailure("test");
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
  }
  stat_counter.PutFailure("test");
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestFallbackRate) {
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());
  for (int i = 0; i < kMinimumEvents; ++i) {
    stat_counter.PutSuccess("test");
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
  }
  for (int i = 0; i < kMinimumEvents - 1; ++i) {
    stat_counter.PutFailure("test");
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
  }
  // Here we reach 0.5 ratio
  stat_counter.PutFailure("test");
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestInterval) {
  utils::datetime::MockNowSet({});
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());

  for (int i = 0; i < kMinimumEvents; ++i) {
    stat_counter.PutFailure("test");
  }
  ASSERT_FALSE(stat_counter.CheckStatus("test"));  // 10/10 failed events
  utils::datetime::MockSleep(kInterval);
  // still 10/10 failed events, because they are not old yet
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
  for (int i = 0; i < kMinimumEvents / 2; ++i) {
    stat_counter.PutFailure("test");
    stat_counter.PutSuccess("test");
  }
  // 15/20 failed events now
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
  // Make first 10 failed event old now
  utils::datetime::MockSleep(kInterval / 10);
  // 5/10 failed event now, but it still fits failure rate (0.5)
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
  // 5/11 events, normal mode
  stat_counter.PutSuccess("test");
  ASSERT_TRUE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestReadPeriod) {
  const auto now = utils::datetime::Now();
  std::vector<statistics::RequestRecord> db_records;
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());

  stat_counter.ReadSync();
  for (int i = 0; i < kMinimumEvents; ++i) {
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
    db_records.push_back(
        {"test", now - std::chrono::seconds(kMinimumEvents - i - 1), 1, 1});
    stat_counter.SetDbRecords(db_records);
    stat_counter.ReadSync();
  }
  // ReadStatistics shall be called kMinimumEvents + once on start
  ASSERT_EQ(stat_counter.read_records_called, kMinimumEvents + 1);
  // We have read kMinimumEvents events from db and now can check status
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestWritePeriod) {
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());

  stat_counter.WriteSync();
  for (int i = 0; i < kMinimumEvents / 2; ++i) {
    ASSERT_TRUE(stat_counter.CheckStatus("test1"));
    ASSERT_TRUE(stat_counter.CheckStatus("test2"));
    stat_counter.PutSuccess("test1");
    stat_counter.PutFailure("test1");
    stat_counter.PutSuccess("test2");
    stat_counter.PutFailure("test2");
    stat_counter.WriteSync();
  }
  // Enough records to calculate status
  ASSERT_FALSE(stat_counter.CheckStatus("test1"));
  ASSERT_FALSE(stat_counter.CheckStatus("test2"));
  ASSERT_EQ(stat_counter.write_records_called, kMinimumEvents / 2);
  // Records were collapsed into one, because they have the same timestamp
  ASSERT_EQ(stat_counter.records_written, kMinimumEvents);
}

UTEST(TestStatCounter, TestLocalStatsCleanup) {
  const auto now = utils::datetime::Now();
  auto config_storage =
      MakeConfig([](Config& config) { config.observation_interval_sec = 0s; });
  MockStatCounter stat_counter(config_storage.GetSource());

  stat_counter.SetDbRecords({{"test", now - std::chrono::seconds(8), 1, 1},
                             // Outdated records
                             {"test", now - std::chrono::seconds(7), 1, 1},
                             {"test", now - std::chrono::seconds(3), 1, 1},
                             {"test", now - std::chrono::seconds(2), 1, 1},
                             {"test", now - std::chrono::seconds(1), 1, 1},
                             {"test", now, 0, 1}});  // valid record

  stat_counter.ReadSync();

  for (int i = 0; i < 5; ++i) {
    stat_counter.PutFailure("test");
    stat_counter.PutSuccess("test");
  }
  // Outdated records shall be ignored: 5/11 (OK)
  ASSERT_TRUE(stat_counter.CheckStatus("test"));
  // Check that after records which were outside of kCleanupPeriod are removed
  // it's still 5/11 (OK)
  ASSERT_TRUE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestDbAndLocal) {
  const auto now = utils::datetime::Now();
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());

  std::vector<statistics::RequestRecord> db_records;
  for (int i = 0; i < kMinimumEvents / 2; i++) {
    db_records.push_back(
        {"test", now - std::chrono::seconds(kMinimumEvents / 2 - i), 1, 1});
  }
  stat_counter.SetDbRecords(db_records);

  for (int i = 0; i < kMinimumEvents / 2; i++) {
    // Not enough events for minimum_events
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
    stat_counter.PutFailure("test");
    stat_counter.ReadSync();
  }
  ASSERT_FALSE(stat_counter.CheckStatus("test"));
}

UTEST(TestStatCounter, TestReadAndWrite) {
  auto config_storage = MakeConfig();
  MockStatCounter stat_counter(config_storage.GetSource());

  stat_counter.ReadSync();
  stat_counter.WriteSync();
  for (unsigned i = 0; i < kMinimumEvents; i++) {
    // Not enough events for minimum_events
    ASSERT_TRUE(stat_counter.CheckStatus("test"));
    stat_counter.PutFailure("test");

    stat_counter.ReadSync();
    stat_counter.WriteSync();
  }
  stat_counter.ReadSync();
  stat_counter.WriteSync();

  ASSERT_FALSE(stat_counter.CheckStatus("test"));
}

}  // namespace cardstorage::tests
