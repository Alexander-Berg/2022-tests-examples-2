#include "common/gps_storage/gps_archive.hpp"
#include <gtest/gtest.h>
#include <clients/graphite.hpp>
#include <common/test_config.hpp>
#include <config/geotracks_settings.hpp>
#include "common/gps_storage/mock_redis_wrapper.hpp"
#include "common/gps_storage/mock_s3mds.hpp"

namespace gps_storage {
// using LatestHash = std::unordered_map<std::string, long long>;
using ProcessRedisBucketFun =
    std::function<std::future<bool>(const std::string&)>;
using WaitTerminationFun = std::function<bool(std::chrono::nanoseconds)>;
namespace detail {
RedisScanStat ForScannedRedisItems(const RedisWrapper& redis,
                                   unsigned int shard, const std::string& query,
                                   const std::string& worker_id,
                                   const ProcessRedisBucketFun& func,
                                   const WaitTerminationFun& wait_termination,
                                   const config::GeotracksSettings& cfg,
                                   LogExtra& log_extra);

std::chrono::nanoseconds DelayAfterJobBatch(
    int64_t completed_jobs, int64_t estimated_remaining_jobs,
    std::chrono::nanoseconds elapsed_time,
    std::chrono::nanoseconds remaining_time);
}  // namespace detail
}  // namespace gps_storage

static config::Config cfg(config::DocsMapForTest());

TEST(gps_archive, TestFindBucketsToArchive) {
  MockRedisWrapper mock_redis{};

  mock_redis.hashes() = {
      {"some_item", {}},
      {"data/0/42/20170101/0", {}},
      {"lock/0/42/20170101/0",
       {}},  // will be good to check, but mock redis can't do regexp
      {"latest", {{"42", "0"}}}};

  std::vector<std::string> items;
  const auto f = [&items](const std::string& s) {
    items.push_back(s);
    std::promise<bool> p;
    p.set_value(true);
    return p.get_future();
  };
  const auto wait_termination = [](std::chrono::nanoseconds) { return false; };
  LogExtra le{};
  const auto& geotracks_settings = cfg.Get<config::GeotracksSettings>();
  gps_storage::detail::ForScannedRedisItems(mock_redis, 0, "data*",
                                            "test_worker", f, wait_termination,
                                            geotracks_settings, le);
  ASSERT_EQ(items.size(), 1u);
  ASSERT_EQ(items.front(), "data/0/42/20170101/0");
}

namespace gps_storage {
namespace detail {
std::future<bool> TryLockAndArchiveBucket(
    const RedisWrapper& redis, const clients::s3api::Client& s3api,
    const std::string& worker_id, const std::string& key,
    const geohistory::utils::TimePoint& latest, const handlers::Context&,
    ArchiverStats*);
}  // namespace detail
}  // namespace gps_storage
TEST(gps_archive, TestLockBucket1) {
  MockRedisWrapper mock_redis{};

  const std::string data =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";
  const std::string bin_data =
      gps_storage::point::MarshallRoute(std::vector<gps_storage::GpsPointType>{
          gps_storage::point::FromJsonString(data)});
  mock_redis.hashes() = {{"data/0/42/20110101/1", {{"000001", bin_data}}}};

  MockS3API mock_s3;
  gps_storage::ArchiverStats stats = {};
  LogExtra le;
  clients::Graphite graphite;
  handlers::Context ctx{cfg, graphite, le};
  bool result = gps_storage::detail::TryLockAndArchiveBucket(
                    mock_redis, mock_s3, "ChtulhuOne", "data/0/42/20110101/1",
                    {}, ctx, &stats)
                    .get();
  ASSERT_EQ(result, true);
  ASSERT_NE(mock_s3.data.find("data/0/42/20110101/1"), mock_s3.data.end());
  ASSERT_EQ(mock_redis.hashes().find("data/0/42/20110101/1"),
            mock_redis.hashes().end());
}

TEST(gps_archive, TestLockBucketAsync) {
  MockRedisWrapper mock_redis{};

  const std::string data =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";
  const std::string bin_data =
      gps_storage::point::MarshallRoute(std::vector<gps_storage::GpsPointType>{
          gps_storage::point::FromJsonString(data)});
  mock_redis.hashes() = {{"data/0/42/20110101/1", {{"000001", bin_data}}}};

  struct AsyncMockS3API : public MockS3API {
    mutable std::condition_variable cv;
    mutable std::mutex m;
    mutable std::thread thread;
    virtual void PutObject(const std::string& k, std::string&& v,
                           const RequestCompleteCallback& h,
                           const LogExtra& log_extra) const override {
      m.lock();
      std::thread t([this, h, k, v, log_extra]() mutable {
        std::unique_lock<std::mutex> l(m, std::adopt_lock);
        cv.wait(l);
        MockS3API::PutObject(k, std::move(v), h, log_extra);
      });
      thread = std::move(t);
    }
  };

  AsyncMockS3API mock_s3;
  LogExtra le;
  clients::Graphite graphite;
  handlers::Context ctx{cfg, graphite, le};
  gps_storage::detail::TryLockAndArchiveBucket(
      mock_redis, mock_s3, "ChtulhuOne", "data/0/42/20110101/1", {}, ctx,
      nullptr);

  // mock_s3 blocks, so we should  have the following state:
  // bucket present
  ASSERT_NE(mock_redis.hashes().find("data/0/42/20110101/1"),
            mock_redis.hashes().end());
  // there is a lock
  ASSERT_NE(mock_redis.values().find("lock/0/42/20110101/1"),
            mock_redis.values().end());

  // wait for the s3 mock to finish
  std::unique_lock<std::mutex> l(mock_s3.m);
  l.unlock();
  mock_s3.cv.notify_all();
  mock_s3.thread.join();

  // now all should be complete:
  // data got to mds
  ASSERT_NE(mock_s3.data.find("data/0/42/20110101/1"), mock_s3.data.end());
  // no bucket and no lock in redis
  ASSERT_EQ(mock_redis.hashes().find("data/0/42/20110101/1"),
            mock_redis.hashes().end());
  ASSERT_EQ(mock_redis.values().find("lock/0/42/20110101/1"),
            mock_redis.values().end());
}

struct FailMockS3API : public MockS3API {
  virtual std::string PutObject(const std::string& /*path*/,
                                std::string&& /*data*/,
                                const LogExtra&) const override {
    throw utils::http::HttpServerException{502};
  }

  virtual void PutObject(const std::string&, std::string&&,
                         const RequestCompleteCallback& h,
                         const LogExtra&) const override {
    h(clients::s3api::Result{502, ""});
  }
};

TEST(gps_archive, TestLockBucketFail1) {
  MockRedisWrapper mock_redis{};

  const std::string data =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";
  const std::string bin_data =
      gps_storage::point::MarshallRoute(std::vector<gps_storage::GpsPointType>{
          gps_storage::point::FromJsonString(data)});
  mock_redis.hashes() = {{"data/0/42/20110101/1", {{"000001", bin_data}}}};

  FailMockS3API mock_s3;
  LogExtra le;
  clients::Graphite graphite;
  handlers::Context ctx{cfg, graphite, le};
  /*bool result =*/gps_storage::detail::TryLockAndArchiveBucket(
      mock_redis, mock_s3, "ChtulhuOne", "data/0/42/20110101/1", {}, ctx,
      nullptr);
  // ASSERT_EQ(result, false);
  ASSERT_EQ(mock_s3.data.find("data/0/42/20110101/1"), mock_s3.data.end());
  ASSERT_NE(mock_redis.hashes().find("data/0/42/20110101/1"),
            mock_redis.hashes().end());
}

TEST(gps_archive, TestLockBucketFailTooManyErrors) {
  class CountingMockRedisWrapper : public MockRedisWrapper {
   public:
    mutable int hget_count = 0;
    virtual Request Hgetall(const std::string& key) const override {
      hget_count++;
      return MockRedisWrapper::Hgetall(key);
    }
  };
  CountingMockRedisWrapper mock_redis{};

  const std::string data =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";
  const std::string bin_data =
      gps_storage::point::MarshallRoute(std::vector<gps_storage::GpsPointType>{
          gps_storage::point::FromJsonString(data)});
  mock_redis.hashes() = {{"data/0/42/20110101/1", {{"000001", bin_data}}},
                         {"data/0/43/20110101/1", {{"000001", bin_data}}},
                         {"data/0/44/20110101/1", {{"000001", bin_data}}},
                         {"data/0/45/20110101/1", {{"000001", bin_data}}},
                         {"data/0/46/20110101/1", {{"000001", bin_data}}},
                         {"data/0/47/20110101/1", {{"000001", bin_data}}},
                         {"data/0/48/20110101/1", {{"000001", bin_data}}},
                         {"data/0/49/20110101/1", {{"000001", bin_data}}},
                         {"data/0/4A/20110101/1", {{"000001", bin_data}}}};

  FailMockS3API mock_s3;

  LogExtra le{};

  const auto f = [&](const std::string& s) {
    LogExtra le;
    clients::Graphite graphite;
    handlers::Context ctx{cfg, graphite, le};
    return gps_storage::detail::TryLockAndArchiveBucket(
        mock_redis, mock_s3, "ChtulhuOne", s, {}, ctx, nullptr);
  };
  const auto wait_termination = [](std::chrono::nanoseconds) { return false; };

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GEOTRACKS_ARCHIVER_ERRORS_GIVEUP_COUNT", 5);
  docs_map.Override("GEOTRACKS_ARCHIVER_MAX_ASYNC_TASKS", 2);
  config::Config cfg(docs_map);

  const auto& geotracks_settings = cfg.Get<config::GeotracksSettings>();
  ASSERT_ANY_THROW(gps_storage::detail::ForScannedRedisItems(
      mock_redis, 0, "data*", "test_worker", f, wait_termination,
      geotracks_settings, le));

  ASSERT_EQ(mock_s3.data.find("data/0/42/20110101/1"), mock_s3.data.end());
  ASSERT_NE(mock_redis.hashes().find("data/0/42/20110101/1"),
            mock_redis.hashes().end());

  // no less than GEOTRACKS_ARCHIVER_ERRORS_GIVEUP_COUNT,
  // multiple of GEOTRACKS_ARCHIVER_MAX_ASYNC_TASKS
  ASSERT_EQ(mock_redis.hget_count, 6);
}

TEST(gps_archive, TestLockAndArchiveBucket) {
  MockRedisWrapper mock_redis{};

  const std::string data0 =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";
  const std::string data1 =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:03.325689Z\"}";

  const auto p0 = gps_storage::point::FromJsonString(data0);
  const auto p1 = gps_storage::point::FromJsonString(data1);

  const std::string bin_data0 = gps_storage::point::MarshallRoute(
      std::vector<gps_storage::GpsPointType>{p0});
  const std::string bin_data1 = gps_storage::point::MarshallRoute(
      std::vector<gps_storage::GpsPointType>{p1});
  mock_redis.hashes() = {
      {"data/0/42/20110101/1", {{"000001", bin_data0}, {"000002", bin_data1}}}};

  MockS3API mock_s3;
  gps_storage::ArchiverStats stats = {};
  LogExtra le;
  clients::Graphite graphite;
  handlers::Context ctx{cfg, graphite, le};
  bool result = gps_storage::detail::TryLockAndArchiveBucket(
                    mock_redis, mock_s3, "ChtulhuOne", "data/0/42/20110101/1",
                    {}, ctx, &stats)
                    .get();
  ASSERT_EQ(result, true);
  ASSERT_NE(mock_s3.data.find("data/0/42/20110101/1"), mock_s3.data.end());

  const auto zresult = mock_s3.data.find("data/0/42/20110101/1")->second;
  const auto r = gps_storage::point::UnmarshallRoute(zresult);

  // The original track has 2 points (data0 and data)
  // The simplified track should also have 2 point
  // The filtered track should have only one point
  // (since the point coordinates are the same and there is only one segment,
  // so it can not be removed completely).
  // This is how we know indirectly that the track was filtered
  ASSERT_EQ(r.size(), 1u);
}

TEST(gps_archive, TestCalculateDelays) {
  using nanoseconds = std::chrono::nanoseconds;
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                0, 0, nanoseconds(0), nanoseconds(0)));
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                0, 5, nanoseconds(100), nanoseconds(1000)));
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                10, 0, nanoseconds(1000), nanoseconds(1000)));
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                2, 5, nanoseconds(200), nanoseconds(0)));
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                1, 1, nanoseconds(500), nanoseconds(500)));
  ASSERT_EQ(nanoseconds(0), gps_storage::detail::DelayAfterJobBatch(
                                1, 1, nanoseconds(600), nanoseconds(400)));
  ASSERT_EQ(nanoseconds(400), gps_storage::detail::DelayAfterJobBatch(
                                  1, 1, nanoseconds(100), nanoseconds(900)));
  ASSERT_EQ(nanoseconds(200), gps_storage::detail::DelayAfterJobBatch(
                                  10, 20, nanoseconds(100), nanoseconds(800)));
}
