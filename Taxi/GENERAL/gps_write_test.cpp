#include "gps_write.hpp"
#include <hiredis/hiredis.h>

#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <handler_util/errors.hpp>
#include <handlers/context.hpp>
#include "clients/graphite.hpp"
#include "common/gps_storage/gps_point.hpp"
#include "common/gps_storage/utils.hpp"
#include "handlers/base.hpp"
#include "mock_redis_wrapper.hpp"
#include "mock_s3mds.hpp"
#include "utils/time.hpp"

namespace gps_storage {
namespace write_detail {
RedisWrapper::Request WriteToRedis(
    const RedisWrapper& redis, const utils::DriverId& driver_id,
    std::string&& data, std::chrono::system_clock::time_point entry_time,
    const handlers::Context& context);
}  // namespace write_detail
}  // namespace gps_storage

static clients::Graphite graphite;
static TimeStorage ts("test_ts");
static LogExtra log_extra;

TEST(gps_archive, TestWrite) {
  config::Config cfg(config::DocsMapForTest());
  MockRedisWrapper mock_redis{};

  boost::posix_time::ptime pt{boost::gregorian::date{2017, 01, 02},
                              boost::posix_time::seconds(1)};
  const auto now = std::chrono::system_clock::from_time_t(PTimeToTime(pt));

  const std::string data =
      "{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-02T00:"
      "00:01.325689Z\"}";

  LogExtra le;

  handlers::Context ctx{cfg, graphite, log_extra};

  gps_storage::write_detail::WriteToRedis(
      mock_redis, gps_storage::utils::DriverId{"0", "42"}, std::string(data),
      now, ctx)
      .Get();
  ASSERT_EQ(mock_redis.hashes().size(), 1u);
  ASSERT_FALSE(mock_redis.values()["latest"].empty());

  gps_storage::write_detail::WriteToRedis(
      mock_redis, gps_storage::utils::DriverId{"0", "42"}, std::string(data),
      now + std::chrono::seconds(1), ctx)
      .Get();

  // should write to the same bucket
  ASSERT_EQ(mock_redis.hashes()["data/0/42/20170102/0"].size(), 2u);

  const auto large_time_delta = std::chrono::hours(10);
  gps_storage::write_detail::WriteToRedis(
      mock_redis, gps_storage::utils::DriverId{"0", "42"}, std::string(data),
      now + large_time_delta, ctx)
      .Get();

  // new bucket
  ASSERT_EQ(mock_redis.hashes().size(), 2u);
  ASSERT_EQ(mock_redis.hashes()["data/0/42/20170102/0"].size(), 2u);

  const auto nb = std::chrono::duration_cast<geohistory::utils::BucketDuration>(
                      large_time_delta)
                      .count();
  ASSERT_EQ(
      mock_redis.hashes()["data/0/42/20170102/" + std::to_string(nb)].size(),
      1u);

  gps_storage::write_detail::WriteToRedis(
      mock_redis, gps_storage::utils::DriverId{"0", "42"}, std::string(data),
      now + std::chrono::hours(24), ctx)
      .Get();
  ASSERT_EQ(mock_redis.hashes()["data/0/42/20170103/0"].size(), 1u);  // new day
}

TEST(gps_archive, TestWriteFromThePast) {
  MockRedisWrapper mock_redis{};
  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GEOTRACKS_ARCHIVER_DELAY_ARCHIVE_PERIOD", 1);
  config::Config cfg(docs_map);
  mock_redis.hashes()["last_positions"]["0/42"] = "10000 1 2";
  mock_redis.values()["latest"] = "10000";
  const auto driver_id = gps_storage::utils::DriverId{"0", "42"};
  gps_storage::GpsPointType p;
  std::chrono::system_clock::time_point time =
      std::chrono::system_clock::time_point(std::chrono::seconds(1));
  LogExtra le;
  handlers::Context ctx{cfg, graphite, log_extra};
  ASSERT_THROW(gps_storage::write_detail::WriteToRedis(
                   mock_redis, driver_id,
                   std::string(gps_storage::point::MarshallPoint(p)), time, ctx)
                   .Get(),
               BadRequest);

  mock_redis.hashes()["last_positions"]["0/43"] = "10 1 2";
  mock_redis.values()["latest"] = "10";
  const auto driver_id2 = gps_storage::utils::DriverId{"0", "43"};
  ASSERT_NO_THROW(gps_storage::write_detail::WriteToRedis(
                      mock_redis, driver_id2,
                      std::string(gps_storage::point::MarshallPoint(p)), time,
                      ctx)
                      .Get());
}
