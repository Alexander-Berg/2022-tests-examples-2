#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/filesystem.hpp>
#include <fstream>

#include <json/value.h>
#include <common/test_config.hpp>
#include <models/configs.hpp>
#include <utils/datetime.hpp>
#include <utils/scope_guard.hpp>

#include <caches/partially_async_base.hpp>
#include <utils/test_file_utils.hpp>

#pragma clang diagnostic ignored "-Winconsistent-missing-override"

using ::testing::_;
using ::testing::DoAll;
using ::testing::Eq;
using ::testing::InSequence;
using ::testing::Return;
using ::testing::SetArgReferee;

using TimePoint = std::chrono::system_clock::time_point;

namespace caches {

namespace {

struct TestData {
  int x;
};

class TestCache : public PartiallyAsyncBase<TestData> {
 public:
  static constexpr const char* kName = "TestCache";

  TestCache(const utils::Async& async, const std::string& dump_folder,
            const utils::DataProvider<config::Config>& config)
      : PartiallyAsyncBase(kName, async, kUpdateInterval, kLastUpdateCorrection,
                           kRunAsyncUpdateInterval, dump_folder, config),
        db_val_(0) {}

  void SetDbVal(int val) { db_val_.store(val); }

  bool TriggerCleanUpdateFromDisk(Data& data, TimePoint& updated_at,
                                  const utils::AsyncStatus& status,
                                  TimeStorage& ts, LogExtra& log_extra) {
    return CleanUpdateFromDisk(data, updated_at, status, ts, log_extra);
  }

  void TriggerSaveToDisk(const Data& data, TimePoint dump_time,
                         const utils::AsyncStatus& status, TimeStorage& ts,
                         LogExtra& log_extra) {
    SaveToDisk(data, dump_time, status, ts, log_extra);
  }

  ~TestCache() noexcept override {}

  void UpdateData(Data& data, UpdateType /*type*/,        //
                  TimePoint /*now*/, TimePoint /*from*/,  //
                  const utils::AsyncStatus& /*status*/,   //
                  TimeStorage& /*ts*/, LogExtra& /*log_extra*/) const final {
    auto val = db_val_.load();
    if (val >= 0) {
      data.x = val;
    }
  }

  virtual Cursor UpdateDataPartialy(Data& /*data*/,                        //
                                    const Cursor& /*cursor*/,              //
                                    size_t /*limit*/,                      //
                                    const utils::AsyncStatus& /*status*/,  //
                                    TimeStorage& /*ts*/,                   //
                                    LogExtra& /*log_extra*/) const final {
    return {};
  }

  size_t DumpVersion(LogExtra&) const final { return 0; }

  void SaveToStream(const Data& data, std::ostream& os,
                    const utils::AsyncStatus& status, TimeStorage&,
                    LogExtra&) const final {
    if (status.interrupted()) {
      throw std::runtime_error("saving interrupted");
    }
    boost::archive::binary_oarchive arch(os);
    arch << data.x;
  }

  void ReadFromStream(Data& data, std::istream& is, const utils::AsyncStatus&,
                      TimeStorage&, LogExtra&) const final {
    boost::archive::binary_iarchive arch(is);
    arch >> data.x;
  }

 private:
  std::atomic<int> db_val_;

  static constexpr std::chrono::seconds kUpdateInterval{5};
  static constexpr std::chrono::seconds kLastUpdateCorrection{10};
  static constexpr std::chrono::minutes kRunAsyncUpdateInterval{15};
};

class TestConfig : public utils::DataProvider<config::Config> {
 public:
  TestConfig(config::DocsMap docs_map = config::DocsMapForTest())
      : docs_map_(docs_map) {}

  UnsafePtr GetUnsafe() const final {
    return std::make_shared<config::Config>(docs_map_);
  }

 private:
  config::DocsMap docs_map_;
};

}  // namespace

TEST(PartiallyAsyncBase, DumpTest) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();
  bfs::create_directories(directory);
  utils::ScopeGuard cleanup(
      [directory]() { utils::ClearDirectory(directory); });

  const utils::Async async(1, "test-pool");

  TestConfig test_config;
  TestCache cache(async, directory.native(), test_config);

  TimeStorage ts{"test-ts"};
  LogExtra log_extra;

  // no dump on disk
  {
    cache.SetDbVal(10);
    cache.DoUpdate(utils::AsyncStatus{}, ts, clients::Graphite{}, log_extra);
    auto data = cache.Get();
    ASSERT_NE(static_cast<std::shared_ptr<const TestData>>(data).get(),
              nullptr);
    ASSERT_EQ(data->x, 10);
  }

  // save dump
  {
    utils::AsyncStatus status;
    cache.TriggerSaveToDisk(TestData{5}, TimePoint(std::chrono::seconds(2)),
                            status, ts, log_extra);
    auto f1 = directory / "dump_1970-01-01T00:00:02+0000_version_0";
    ASSERT_EQ(utils::ListDirectory(directory),
              (std::set<std::string>({f1.native()})));
  }

  // load from dump
  {
    TimePoint now(std::chrono::seconds(3));
    utils::datetime::MockNowSet(now);
    utils::ScopeGuard now_cleanup([]() { utils::datetime::MockNowUnset(); });
    cache.SetDbVal(-1);  // dont update loaded from disk
    TestData d;
    TimePoint updated_at;
    bool res = cache.TriggerCleanUpdateFromDisk(
        d, updated_at, utils::AsyncStatus{}, ts, log_extra);
    ASSERT_TRUE(res);
    ASSERT_EQ(updated_at, now);
    ASSERT_EQ(d.x, 5);
  }
}

TEST(PartiallyAsyncBase, TestInterrupted) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();
  bfs::create_directories(directory);
  utils::ScopeGuard cleanup(
      [directory]() { utils::ClearDirectory(directory); });

  const utils::Async async(1, "test-pool");

  TestConfig test_config;
  TestCache cache(async, directory.native(), test_config);

  TimeStorage ts{"test-ts"};
  LogExtra log_extra;

  // save dump
  {
    utils::AsyncStatus status;
    status.Interrupt();
    cache.TriggerSaveToDisk(TestData{5}, TimePoint(std::chrono::seconds(2)),
                            status, ts, log_extra);
    auto f1 = directory / "dump_1970-01-01T00:00:02+0000_version_0.tmp";
    ASSERT_EQ(utils::ListDirectory(directory),
              (std::set<std::string>({f1.native()})));
  }
}

class MockCache : public PartiallyAsyncBase<int> {
 public:
  static constexpr const char* kName = "MockCache";

  MockCache(const utils::Async& async, const std::string& dump_folder,
            const utils::DataProvider<config::Config>& config)
      : PartiallyAsyncBase(kName, async, kUpdateInterval, kLastUpdateCorrection,
                           kRunAsyncUpdateInterval, dump_folder, config) {}

  ~MockCache() noexcept override {}

  TimePoint TrigerUpdateIncremental(TimePoint now,
                                    const utils::AsyncStatus& status,
                                    TimeStorage& ts, LogExtra& log_extra) {
    return UpdateIncremental(now, status, ts, log_extra);
  }

  MOCK_CONST_METHOD7(UpdateData,
                     void(Data& data, UpdateType, TimePoint, TimePoint,
                          const utils::AsyncStatus&, TimeStorage&, LogExtra&));
  MOCK_CONST_METHOD6(UpdateDataPartialy, Cursor(Data&, const Cursor&, size_t,
                                                const utils::AsyncStatus&,
                                                TimeStorage&, LogExtra&));
  MOCK_CONST_METHOD5(SaveToStream,
                     void(const Data&, std::ostream&, const utils::AsyncStatus&,
                          TimeStorage&, LogExtra&));

  size_t DumpVersion(LogExtra&) const final { return 0; }

  void ReadFromStream(Data&, std::istream&, const utils::AsyncStatus&,
                      TimeStorage&, LogExtra&) const final {
    throw std::runtime_error("unexpected");
  }

  using PartiallyAsyncBase<int>::Cursor;
  using PartiallyAsyncBase<int>::data_;
  using PartiallyAsyncBase<int>::partial_async_update_;
  using PartiallyAsyncBase<int>::async_update_;

 private:
  static constexpr std::chrono::seconds kUpdateInterval{5};
  static constexpr std::chrono::seconds kLastUpdateCorrection{10};
  static constexpr std::chrono::minutes kRunAsyncUpdateInterval{15};
};

config::DocsMap MakeCacheConfig(bool partial_update_enabled,
                                size_t num_docs_to_read) {
  Json::Value default_value;
  default_value["is_dump_enabled"] = true;
  default_value["is_partial_update_enabled"] = partial_update_enabled;
  default_value["partial_update_sleep_sec"] = 0;
  default_value["num_docks_per_update"] = num_docs_to_read;

  Json::Value cache_settings;
  cache_settings["__default__"] = std::move(default_value);

  const std::string path{CONFIG_FALLBACK_DIR "/configs.json"};
  auto result = models::configs::ReadFallback(path);
  result["PARKS_CACHE_SETTINGS"] = std::move(cache_settings);
  return models::configs::JsonToDocsMap(result);
}

MATCHER_P(CursorsEqual, to, "") {
  return (arg.park_id == to.park_id && arg.id == to.id);
}

struct TestCacheData {
  TestCacheData()
      : directory(utils::MakeRandomDumpDirectory()),
        async(1, "test-pool"),
        test_config(MakeCacheConfig(true, 5)),
        cache(async, directory.native(), test_config) {}
  ~TestCacheData() { utils::ClearDirectory(directory); }

  boost::filesystem::path directory;
  const utils::Async async;
  TestConfig test_config;
  MockCache cache;
};

TEST(PartiallyAsyncBase, TestPartialCursor) {
  TestCacheData test_data;
  auto& cache = test_data.cache;

  TimeStorage ts{"test-ts"};
  LogExtra log_extra;

  // read batch 1
  {
    InSequence s;
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
    EXPECT_CALL(cache, UpdateDataPartialy(_, CursorsEqual(MockCache::Cursor{}),
                                          5, _, _, _))
        .WillOnce(Return(MockCache::Cursor{"1", "1"}));
    EXPECT_CALL(cache, SaveToStream(_, _, _, _, _)).Times(0);
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
  }

  cache.TrigerUpdateIncremental(TimePoint(std::chrono::seconds(2)),
                                utils::AsyncStatus{}, ts, log_extra);
  ASSERT_TRUE(cache.partial_async_update_.IsValid());
  cache.partial_async_update_.Wait();
  testing::Mock::VerifyAndClearExpectations(&cache);

  // read batch 2. end reached
  {
    InSequence s;
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
    EXPECT_CALL(cache,
                UpdateDataPartialy(_, CursorsEqual(MockCache::Cursor{"1", "1"}),
                                   5, _, _, _))
        .WillOnce(Return(MockCache::Cursor{}));
    EXPECT_CALL(cache, SaveToStream(_, _, _, _, _)).Times(1);
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
  }

  cache.TrigerUpdateIncremental(TimePoint(std::chrono::seconds(2)),
                                utils::AsyncStatus{}, ts, log_extra);
  ASSERT_TRUE(cache.partial_async_update_.IsValid());
  cache.partial_async_update_.Wait();
  testing::Mock::VerifyAndClearExpectations(&cache);

  // start reading from the begining
  {
    InSequence s;
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
    EXPECT_CALL(cache, UpdateDataPartialy(_, CursorsEqual(MockCache::Cursor{}),
                                          5, _, _, _))
        .WillOnce(Return(MockCache::Cursor{"1", "1"}));
    EXPECT_CALL(cache, SaveToStream(_, _, _, _, _)).Times(0);
    EXPECT_CALL(cache, UpdateData(_, _, _, _, _, _, _)).Times(1);
  }

  cache.TrigerUpdateIncremental(TimePoint(std::chrono::seconds(2)),
                                utils::AsyncStatus{}, ts, log_extra);
  ASSERT_TRUE(cache.partial_async_update_.IsValid());
  cache.partial_async_update_.Wait();
  testing::Mock::VerifyAndClearExpectations(&cache);
}

TEST(PartiallyAsyncBase, TestPartialUpdateOverPrevData) {
  TestCacheData test_data;
  auto& cache = test_data.cache;

  TimeStorage ts{"test-ts"};
  LogExtra log_extra;

  int val1 = 1;
  int val2 = 2;
  int val3 = 3;
  cache.data_.Set(1);
  // check that partial full update is done over stored data
  {
    InSequence s;
    EXPECT_CALL(
        cache, UpdateData(Eq(std::ref(val1)), MockCache::UpdateType::Partial, _,
                          _, _, _, _))
        .Times(1);
    EXPECT_CALL(cache, UpdateDataPartialy(Eq(std::ref(val1)),
                                          CursorsEqual(MockCache::Cursor{}), 5,
                                          _, _, _))
        .WillOnce(
            DoAll(SetArgReferee<0>(val2), Return(MockCache::Cursor{"1", "1"})));
    EXPECT_CALL(
        cache, UpdateData(Eq(std::ref(val2)), MockCache::UpdateType::Partial, _,
                          _, _, _, _))
        .Times(1);
  }
  EXPECT_CALL(cache, SaveToStream(_, _, _, _, _)).Times(0);

  cache.TrigerUpdateIncremental(TimePoint(std::chrono::seconds(2)),
                                utils::AsyncStatus{}, ts, log_extra);
  ASSERT_TRUE(cache.partial_async_update_.IsValid());
  cache.partial_async_update_.Wait();
  testing::Mock::VerifyAndClearExpectations(&cache);

  // check that value from partial full update used in next incremental call
  {
    InSequence s;
    EXPECT_CALL(
        cache, UpdateData(Eq(std::ref(val2)), MockCache::UpdateType::Partial, _,
                          _, _, _, _))
        .Times(1);
    EXPECT_CALL(cache,
                UpdateDataPartialy(Eq(std::ref(val2)),
                                   CursorsEqual(MockCache::Cursor{"1", "1"}), 5,
                                   _, _, _))
        .WillOnce(
            DoAll(SetArgReferee<0>(val3), Return(MockCache::Cursor{"2", "2"})));
    EXPECT_CALL(
        cache, UpdateData(Eq(std::ref(val3)), MockCache::UpdateType::Partial, _,
                          _, _, _, _))
        .Times(1);
  }
  EXPECT_CALL(cache, SaveToStream(_, _, _, _, _)).Times(0);

  cache.TrigerUpdateIncremental(TimePoint(std::chrono::seconds(2)),
                                utils::AsyncStatus{}, ts, log_extra);
  ASSERT_TRUE(cache.partial_async_update_.IsValid());
  cache.partial_async_update_.Wait();
  testing::Mock::VerifyAndClearExpectations(&cache);
}

}  // namespace caches
