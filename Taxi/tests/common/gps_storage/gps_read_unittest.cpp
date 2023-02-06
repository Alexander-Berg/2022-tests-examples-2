#include <gtest/gtest.h>
#include <chrono>

#include <clients/adjusting/fallback/route_adjust_fallback.hpp>
#include <clients/graphite.hpp>
#include <common/gps_storage/gps_read.hpp>
#include <common/gps_storage/gps_storage_common.hpp>
#include <common/gps_storage/mock_redis_wrapper.hpp>
#include <common/gps_storage/mock_s3mds.hpp>
#include <common/gps_storage/utils.hpp>
#include <common/test_config.hpp>
#include <handlers/base_geotracks.hpp>

static config::Config cfg(config::DocsMapForTest());

static LogExtra log_extra;
static clients::Graphite graphite;
static TimeStorage ts("test_ts");

using MockAdjust = clients::route_adjust::ClientFallback;

TEST(gps_archive, TestReadGps) {
  // ASSERT_EQ(2*2,5);

  MockRedisWrapper mock_redis;
  MockS3API mock_s3;

  // from = Time.at(1483228740).utc => 2016-12-31 23:59:00 UTC
  // to = Time.parse('2017-01-01 00:00:08Z').to_i=> 1483228808
  std::chrono::system_clock::time_point tfrom =
      std::chrono::system_clock::from_time_t(1483228740);
  std::chrono::system_clock::time_point tto =
      std::chrono::system_clock::from_time_t(1483228808);

  // the test data is formed in the following way:
  //
  //------------|--------|-|--------------|----|----|--------------------
  //           s3    |   s3                redis  |
  //                 |    requested interval      |
  //
  const auto s1 = MakeBinaryPointWithTime("2017-01-01T00:00:01.040611Z");
  const auto s2 = MakeBinaryPointWithTime("2017-01-01T00:00:02.09042Z");
  const auto s3 = MakeBinaryPointWithTime("2017-01-01T00:00:09.19042Z");
  const auto s4 = MakeBinaryPointWithTime("2017-01-01T00:00:19.19042Z");

  mock_redis.hashes()["data/0/42/20170101/0"] = {
      {"000001", s1},  // inside
      {"000002", s2},  // inside
      {"000009", s3},  // outside
      {"000009", s4}   // outside
  };

  const int ns3bucket =
      (int)std::chrono::duration_cast<geohistory::utils::BucketDuration>(
          std::chrono::seconds(86400 - 40))
          .count();

  const std::string ss0time = "2016-12-31T23:58:20.325689Z";
  const std::string ss1time = "2016-12-31T23:59:20.325689Z";
  const std::string ss2time = "2016-12-31T23:59:25.325689Z";

  mock_s3.data["data/0/42/20161231/" + std::to_string(ns3bucket)] =
      MakeBinaryRouteWithTimes({ss0time, ss1time, ss2time});

  const std::string ss3time = "2016-12-30T23:59:20.325689Z";
  const std::string ss4time = "2016-12-30T23:59:25.325689Z";

  mock_s3.data["data/0/42/20161230/" + std::to_string(ns3bucket)] =
      MakeBinaryRouteWithTimes({ss3time, ss4time});

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GEOTRACKS_READER_TOO_OLD_FOR_REDIS_PERIOD_HOURS",
                    1000 * 1000);
  config::Config cfg(docs_map);
  Context ctx{cfg, graphite, log_extra, ts};

  MockAdjust mock_adjust;

  utils::Async test_async(1, "test_async");

  auto res = gps_storage::Read(
      mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
      gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
  ASSERT_EQ(res.size(), 6u);

  // should include all the points inside the interval
  // and the points directly before and after the interval
  // (as long as they fit the requested hours)
  // so for the range of  2016-12-31 23:59:00 UTC -- 2017-01-01 00:00:08Z
  // it should include:
  // from s3:
  // ss0 (2016-12-31T23:58:20)  -- directly before
  // ss1 (23:59:20)             -- inside
  // ss2 (23:59:25)
  // from redis:
  // s1 (2017-01-01T00:00:01)
  // s2 (00:00:02)
  // s3 (00:00:09)             --directly after
  ASSERT_EQ(res.begin()->second.update, gps_storage::point::UnmarshallPoint(
                                            MakeBinaryPointWithTime(ss0time))
                                            .update);
  ASSERT_EQ((--res.end())->second.update,
            gps_storage::point::UnmarshallPoint(s3).update);
}

std::chrono::system_clock::time_point GetMidnight(
    geohistory::utils::TimePoint t) {
  namespace sc = std::chrono;
  namespace pt = boost::posix_time;
  time_t tnow = sc::system_clock::to_time_t(t);
  tm date = {};
  gmtime_r(&tnow, &date);
  date.tm_hour = 0;
  date.tm_min = 0;
  date.tm_sec = 0;
  pt::ptime pmidnight = pt::ptime_from_tm(date);
  return std::chrono::system_clock::from_time_t(PTimeToTime(pmidnight));
}

TEST(gps_archive, TestSkipReadRedis) {
  struct FailingMockRedisWrapper : MockRedisWrapper {
    Request Hgetall(const std::string&) const override {
      throw std::runtime_error("should not call it");
    }
  };
  MockS3API mock_s3;
  FailingMockRedisWrapper mock_redis;
  Context ctx{cfg, graphite, log_extra, ts};
  MockAdjust mock_adjust;
  utils::Async test_async(1, "test_async");
  // from =  Time.at(1483228799).utc => 2016-12-31 23:59:59 UTC
  // to = Time.at(1483228811).utc => 2017-01-01 00:00:11 UTC
  std::chrono::system_clock::time_point tfrom =
      std::chrono::system_clock::from_time_t(1483228799);
  std::chrono::system_clock::time_point tto =
      std::chrono::system_clock::from_time_t(1483228811);
  ASSERT_NO_THROW(gps_storage::Read(
      mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
      gps_storage::TrackProcessType::kPreprocessNoFilter, ctx));
}

TEST(gps_archive, TestReadRedisSorted) {
  MockRedisWrapper mock_redis;
  MockS3API mock_s3;

  gps_storage::GpsPointType p1, p2;
  const auto midnight = GetMidnight(std::chrono::system_clock::now());
  p1.update =
      std::chrono::duration_cast<gps_storage::GpsPointType::duration>(
          (midnight + geohistory::utils::BucketDuration(14)).time_since_epoch())
          .count();
  p2.update =
      std::chrono::duration_cast<gps_storage::GpsPointType::duration>(
          (midnight + geohistory::utils::BucketDuration(13)).time_since_epoch())
          .count();

  SetPointsToMockRedis(mock_redis, "0", "42", {p1, p2});

  std::chrono::system_clock::time_point tfrom{
      midnight + geohistory::utils::BucketDuration(1)};
  std::chrono::system_clock::time_point tto{
      midnight + geohistory::utils::BucketDuration(15)};

  Context ctx{cfg, graphite, log_extra, ts};
  MockAdjust mock_adjust;
  utils::Async test_async(1, "test_async");
  auto res = gps_storage::Read(
      mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
      gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);

  ASSERT_EQ(res.size(), 2u);
}

TEST(gps_archive, TestReadGpsSimplify) {
  MockRedisWrapper mock_redis;
  MockS3API mock_s3;  // should not be used

  // make 3 point with the same coordinates
  // should contain only two (first and last) after simplification

  const std::string s1 = MakeBinaryPointWithTime("2017-01-01T00:00:01.040611Z");
  const std::string s2 = MakeBinaryPointWithTime("2017-01-01T00:00:02.09042Z");
  const std::string s3 = MakeBinaryPointWithTime("2017-01-01T00:00:09.19042Z");

  mock_redis.hashes()["data/0/42/20170101/0"] = {
      {"000001", s1},  //
      {"000002", s2},  //
      {"000009", s3}   //
  };

  // from =  Time.at(1483228799).utc => 2016-12-31 23:59:59 UTC
  // to = Time.at(1483228811).utc => 2017-01-01 00:00:11 UTC
  std::chrono::system_clock::time_point tfrom =
      std::chrono::system_clock::from_time_t(1483228799);
  std::chrono::system_clock::time_point tto =
      std::chrono::system_clock::from_time_t(1483228811);

  MockAdjust mock_adjust;
  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GEOTRACKS_READER_TOO_OLD_FOR_REDIS_PERIOD_HOURS",
                    1000 * 1000);
  config::Config cfg(docs_map);
  Context ctx{cfg, graphite, log_extra, ts};
  utils::Async test_async(1, "test_async");
  {
    // without simplification
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 3u);  // should contain all 3 points
  }

  {
    // with simplification
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessSimplify |
            gps_storage::TrackProcessType::kPreprocessNoFilter,
        ctx);
    ASSERT_EQ(res.size(), 2u);  // should throw out the middlog_extra point
    ASSERT_EQ(
        res.begin()->second.update,  // and log_extraave both boundary points
        gps_storage::point::UnmarshallPoint(s1).update);
    ASSERT_EQ((--res.end())->second.update,
              gps_storage::point::UnmarshallPoint(s3).update);
  }
}

TEST(gps_archive, TestReadEmpty) {
  MockRedisWrapper mock_redis;
  MockS3API mock_s3;
  MockAdjust mock_adjust;
  // from =  Time.at(1483228799).utc => 2016-12-31 23:59:59 UTC
  // to = Time.at(1483228811).utc => 2017-01-01 00:00:11 UTC
  std::chrono::system_clock::time_point tfrom =
      std::chrono::system_clock::from_time_t(1483228799);
  std::chrono::system_clock::time_point tto =
      std::chrono::system_clock::from_time_t(1483228811);

  utils::Async test_async(1, "test_async");
  Context ctx{cfg, graphite, log_extra, ts};
  {
    // without simplification
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 0u);
  }

  {
    // with simplification
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 0u);
  }
}

TEST(gps_archive, TestReadEmptyReq) {
  MockRedisWrapper mock_redis;
  MockS3API mock_s3;
  MockAdjust mock_adjust;
  // from =  Time.at(1483228799).utc => 2016-12-31 23:59:59 UTC
  // to = Time.at(1483228811).utc => 2017-01-01 00:00:11 UTC

  Context ctx{cfg, graphite, log_extra, ts};
  utils::Async test_async(1, "test_async");
  gps_storage::ReadContext rctx{mock_redis, mock_s3, &mock_adjust, test_async,
                                ctx};
  {
    // without simplification
    auto res = gps_storage::ReadMultiple(
        {}, gps_storage::TrackProcessType::kPreprocessNoFilter, rctx);
    ASSERT_EQ(res.size(), 0u);
  }
}

TEST(gps_archive, TestSegmentEnds) {
  MockRedisWrapper mock_redis;
  MockS3API mock_s3;  // should not be used

  // make 3 point with the same coordinates
  // should contain only two (first and last) after simplification
  const std::string s1str =
      ("{\"A\":0,\"L\":57,\"O\":41,\"P\":42,\"R\":\"\",\"U\":\"2017-01-01T00:"
       "00:"
       "01.040611Z\"}");
  const std::string s2str =
      "{\"A\":0,\"L\":57,\"O\":41.01,\"P\":42,\"R\":\"\",\"U\":\"2017-01-01T00:"
      "00:"
      "02.09042Z\"}";

  const std::string s1time = "2017-01-01T00:00:01.040611Z";
  const std::string s2time = "2017-01-01T00:00:02.09042Z";
  const auto s1 = MakePoint(57, 41, s1time);
  const auto s2 = MakePoint(57, 41.01, s2time);

  mock_s3.data["data/0/42/20170101/0"] = MakeBinaryRoute({s1, s2});

  SetPointsToMockRedis(
      mock_redis, "0", "42",
      {// new segment start because of the time difference
       MakePoint(57, 41, "2017-01-01T02:00:09.19042Z"),
       // new segment start because of the space difference ("O")
       MakePoint(57, 51, "2017-01-01T02:00:10.19042Z"),
       // segment ends beacause it's the last point
       MakePoint(57, 51, "2017-01-01T02:00:11.19042Z")});

  // from =  Time.at(1483228799).utc => 2016-12-31 23:59:59 UTC
  // to = Time.at(1483236012).utc => 2017-01-01 02:00:12 UTC
  std::chrono::system_clock::time_point tfrom =
      std::chrono::system_clock::from_time_t(1483228799);
  std::chrono::system_clock::time_point tto =
      std::chrono::system_clock::from_time_t(1483236012);

  MockAdjust mock_adjust;
  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GEOTRACKS_READER_TOO_OLD_FOR_REDIS_PERIOD_HOURS",
                    1000 * 1000);
  config::Config cfg(docs_map);
  utils::Async test_async(1, "test_async");
  Context ctx{cfg, graphite, log_extra, ts};
  {
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 5u);
    int i = 0;
    for (const auto& it : res) {
      bool should_end = false;
      if (i == 1 || i == 2 || i == 4) {
        should_end = true;
      }
      ASSERT_EQ(it.second.end_segment, should_end);
      i++;
    }
  }

  {  // one item is its own end
    mock_s3.data.clear();
    SetPointsToMockRedis(mock_redis, "0", "42",
                         {MakePoint(57, 41, "2017-01-01T02:00:09.19042Z")});
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 1u);
    ASSERT_EQ(res.begin()->second.end_segment, true);
  }

  {  // zero items have no ends
    mock_s3.data.clear();
    SetPointsToMockRedis(mock_redis, "0", "42", std::vector<std::string>{});
    auto res = gps_storage::Read(
        mock_redis, mock_s3, &mock_adjust, test_async, "0", "42", tfrom, tto,
        gps_storage::TrackProcessType::kPreprocessNoFilter, ctx);
    ASSERT_EQ(res.size(), 0u);
  }
}

namespace gps_storage {
namespace read_detail {
void RemoveExtraHeadTail(GpsGetResult& result,
                         const geohistory::utils::TimePoint& from,
                         const geohistory::utils::TimePoint& to,
                         GpsPointType::duration offset);
}
}  // namespace gps_storage

TEST(gps_archive, TestRemoveExtraHeadTail) {
  const auto get_t = [](int t) {
    return gps_storage::GpsPointType::duration(t).count();
  };

  gps_storage::GpsPointType p1;
  p1.update = get_t(1);

  gps_storage::GpsPointType p2;
  p1.update = get_t(4);

  gps_storage::GpsPointType p3;
  p1.update = get_t(8);

  gps_storage::GpsPointType p4;
  p1.update = get_t(12);

  gps_storage::GpsPointType p5;
  p1.update = get_t(16);

  gps_storage::GpsPointType p6;
  p1.update = get_t(20);

  gps_storage::GpsGetResult data1 = {
      {get_t(1), p1},  {get_t(4), p2},  {get_t(8), p3},
      {get_t(12), p4}, {get_t(16), p5}, {get_t(20), p6},
  };

  // 1 4 8 12 16 20 /  (3 14) -> 1 4 8 12 16
  // check when there is no exact match
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(3)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(14)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 5u);
  ASSERT_EQ(data1.begin()->first, get_t(1));
  ASSERT_EQ((--data1.end())->first, get_t(16));

  // 1 4 8 12 16/  (1 16) -> 1 4 8 12 16
  // check when it's head or tail
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(1)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(16)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 5u);
  ASSERT_EQ(data1.begin()->first, get_t(1));
  ASSERT_EQ((--data1.end())->first, get_t(16));

  // 1 4 8 12 16  / (0,99) ->  1 4 8 12 16
  // check when it's before/after head/tail
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(0)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(99)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 5u);
  ASSERT_EQ(data1.begin()->first, get_t(1));
  ASSERT_EQ((--data1.end())->first, get_t(16));

  // 1 4 8 12 16  / (4,12) ->  4 8 12
  // check when there is an exact match
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(4)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(12)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 3u);
  ASSERT_EQ(data1.begin()->first, get_t(4));
  ASSERT_EQ((--data1.end())->first, get_t(12));

  // 4 8 12   / (0,0) ->  4
  // check when it's empty and before head
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(0)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(0)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 1u);
  ASSERT_EQ(data1.begin()->first, get_t(4));
  ASSERT_EQ((--data1.end())->first, get_t(4));

  // 4  / (99, 99 ) ->  4
  // check when it's empty and after tail
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(99)},
      geohistory::utils::TimePoint{gps_storage::GpsPointType::duration(99)},
      gps_storage::GpsPointType::duration(0));

  ASSERT_EQ(data1.size(), 1u);
  ASSERT_EQ(data1.begin()->first, get_t(4));
  ASSERT_EQ((--data1.end())->first, get_t(4));

  data1 = {
      {get_t(1000000), gps_storage::GpsPointType()},
      {get_t(5000000), gps_storage::GpsPointType()},
      {get_t(6000000), gps_storage::GpsPointType()},
      {get_t(65000000), gps_storage::GpsPointType()},
      {get_t(120000000), gps_storage::GpsPointType()},
      {get_t(124000000), gps_storage::GpsPointType()},
      {get_t(127000000), gps_storage::GpsPointType()},
      {get_t(180000000), gps_storage::GpsPointType()},
  };
  // 1 5 6 65 120 124 127 180 / (65, 66) -> 5 6 65 120 124 127
  // all * 10^6
  // check offset
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{
          gps_storage::GpsPointType::duration(65000000)},
      geohistory::utils::TimePoint{
          gps_storage::GpsPointType::duration(66000000)},
      std::chrono::minutes(1));

  ASSERT_EQ(data1.size(), 6u);
  ASSERT_EQ(data1.begin()->first, get_t(5000000));
  ASSERT_EQ((--data1.end())->first, get_t(127000000));
  // 5 6 65 120 124 127 / (65, 66) -> 6 65 120 124
  // all * 10^6
  // check offset
  gps_storage::read_detail::RemoveExtraHeadTail(
      data1,
      geohistory::utils::TimePoint{
          gps_storage::GpsPointType::duration(65000000)},
      geohistory::utils::TimePoint{
          gps_storage::GpsPointType::duration(66000000)},
      std::chrono::seconds(58));

  ASSERT_EQ(data1.size(), 4u);
  ASSERT_EQ(data1.begin()->first, get_t(6000000));
  ASSERT_EQ((--data1.end())->first, get_t(124000000));
}
