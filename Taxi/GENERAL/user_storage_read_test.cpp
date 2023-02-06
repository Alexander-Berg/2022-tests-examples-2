#include <gtest/gtest.h>

#include "user_storage_read.hpp"

#include <common/gps_storage/mock_s3mds.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <geohistory/user_position.hpp>

namespace geohistory {
namespace user {
namespace detail {

int GetHourFromPath(const std::string& path);

}  //  namespace detail
}  //  namespace user
}  //  namespace geohistory

TEST(GenerateRedisBuckets, DayRange) {
  geohistory::utils::TimePoint to, from;
  // 2018-01-10T10:24:00+00:00
  from = std::chrono::system_clock::from_time_t(1515579840);
  // 2018-10-05T12:49:00+00:00
  to = std::chrono::system_clock::from_time_t(1538743740);
  auto res = geohistory::user::GenerateRedisBuckets(from, to, "123");
  ASSERT_EQ(res.size(), static_cast<size_t>(6435));
  EXPECT_EQ(res.begin()->GetRedisBucketName(), "history:20180110:10:123");
  EXPECT_EQ(res.rbegin()->GetRedisBucketName(), "history:20181005:12:123");
}

TEST(GenerateRedisBuckets, OneDay) {
  geohistory::utils::TimePoint to, from;
  // 2018-01-10T10:24:00+00:00
  from = std::chrono::system_clock::from_time_t(1515579840);
  // 2018-01-10T13:39:00+00:00
  to = std::chrono::system_clock::from_time_t(1515591540);
  auto res = geohistory::user::GenerateRedisBuckets(from, to, "123");
  ASSERT_EQ(res.size(), static_cast<size_t>(4));
  EXPECT_EQ(res.begin()->GetRedisBucketName(), "history:20180110:10:123");
  EXPECT_EQ(res.rbegin()->GetRedisBucketName(), "history:20180110:13:123");
}

TEST(RemoveExtraHeadTail, AllCases) {
  const auto get_t = [](int t) {
    return std::chrono::system_clock::from_time_t(t);
  };
  models::UserPosition p1;
  p1.timestamp = get_t(1);

  models::UserPosition p2;
  p2.timestamp = get_t(4);

  models::UserPosition p3;
  p3.timestamp = get_t(8);

  models::UserPosition p4;
  p4.timestamp = get_t(12);

  models::UserPosition p5;
  p5.timestamp = get_t(16);

  models::UserPosition p6;
  p6.timestamp = get_t(20);
  geohistory::user::UserTrack data1 = {
      p1, p2, p3, p4, p5, p6,
  };

  // 1 4 8 12 16 20 /  (3 14) -> 1 4 8 12 16
  // check when there is no exact match
  geohistory::user::RemoveExtraHeadTail(data1, get_t(3), get_t(14));
  ASSERT_EQ(data1.size(), 5u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(1));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(16));

  // 1 4 8 12 16/  (1 16) -> 1 4 8 12 16
  // check when it's head or tail
  geohistory::user::RemoveExtraHeadTail(data1, get_t(1), get_t(16));

  ASSERT_EQ(data1.size(), 5u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(1));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(16));

  // 1 4 8 12 16  / (0,99) ->  1 4 8 12 16
  // check when it's before/after head/tail
  geohistory::user::RemoveExtraHeadTail(data1, get_t(0), get_t(99));

  ASSERT_EQ(data1.size(), 5u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(1));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(16));

  // 1 4 8 12 16  / (4,12) ->  4 8 12
  // check when there is an exact match
  geohistory::user::RemoveExtraHeadTail(data1, get_t(4), get_t(12));

  ASSERT_EQ(data1.size(), 3u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(4));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(12));

  // 4 8 12   / (0,0) ->  4
  // check when it's empty and before head
  geohistory::user::RemoveExtraHeadTail(data1, get_t(0), get_t(0));

  ASSERT_EQ(data1.size(), 1u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(4));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(4));

  // 4  / (99, 99 ) ->  4
  // check when it's empty and after tail
  geohistory::user::RemoveExtraHeadTail(data1, get_t(99), get_t(99));

  ASSERT_EQ(data1.size(), 1u);
  EXPECT_EQ(data1.begin()->timestamp, get_t(4));
  EXPECT_EQ(data1.rbegin()->timestamp, get_t(4));
}

static clients::Graphite graphite;
static LogExtra log_extra;

TEST(ReadFromS3, TestReading) {
  const auto get_t = [](int t) {
    return std::chrono::system_clock::from_time_t(t);
  };

  const std::vector<models::UserPosition> positions1 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-01T00:00:01+00:00
       std::chrono::system_clock::from_time_t(1538352001),
       5},
      {{33.5, 20.2},
       "user_id",
       // 2018-10-01T00:16:40+00:00
       std::chrono::system_clock::from_time_t(1538353000),
       4},
      {{30, 21.5},
       "user_id",
       // 2018-10-01T00:33:20+00:00
       std::chrono::system_clock::from_time_t(1538354000),
       3}};

  const std::vector<models::UserPosition> positions2 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-01T01:00:00+00:00
       std::chrono::system_clock::from_time_t(1538355600),
       5},
      {{33.5, 20.2},
       "user_id",
       // 2018-10-01T01:16:40+00:00
       std::chrono::system_clock::from_time_t(1538356600),
       4},
      {{30, 21.5},
       "user_id",
       // 2018-10-01T01:33:20+00:00
       std::chrono::system_clock::from_time_t(1538357600),
       3}};

  const std::vector<models::UserPosition> positions3 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-01T02:00:01+00:00
       std::chrono::system_clock::from_time_t(1538359201),
       5},
      {{33.5, 20.2},
       "user_id",
       // 2018-10-01T02:16:40+00:00
       std::chrono::system_clock::from_time_t(1538360200),
       4},
      {{30, 21.5},
       "user_id",
       // 2018-10-01T02:33:20+00:00
       std::chrono::system_clock::from_time_t(1538361200),
       3}};
  const std::vector<models::UserPosition> positions4 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-02T00:12:00+00:00
       std::chrono::system_clock::from_time_t(1538481600),
       5}};
  const std::vector<models::UserPosition> positions5 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-03T00:10:00+00:00
       std::chrono::system_clock::from_time_t(1538560800),
       5}};
  const std::vector<models::UserPosition> positions6 = {
      {{42, 0.4283726124352},
       "user_id",
       // 2018-10-03T00:14:00+00:00
       std::chrono::system_clock::from_time_t(1538575200),
       5}};

  MockS3API mock_s3;
  config::Config cfg(config::DocsMapForTest());
  handlers::Context ctx{cfg, graphite, log_extra};

  mock_s3.data["history/id/20181001/00"] =
      geohistory::user::SerializeTrack(positions1);
  mock_s3.data["history/id/20181001/01"] =
      geohistory::user::SerializeTrack(positions2);
  mock_s3.data["history/id/20181001/02"] =
      geohistory::user::SerializeTrack(positions3);
  mock_s3.data["history/id/20181002/12"] =
      geohistory::user::SerializeTrack(positions4);
  mock_s3.data["history/id/20181003/10"] =
      geohistory::user::SerializeTrack(positions5);
  mock_s3.data["history/id/20181003/14"] =
      geohistory::user::SerializeTrack(positions6);

  // 2018-10-01T00:00:00 to 2018-10-01T02:46:40
  auto answer = geohistory::user::ReadFromS3(
      mock_s3, "id", std::chrono::system_clock::from_time_t(1538352000),
      std::chrono::system_clock::from_time_t(1538362000), ctx);
  ASSERT_EQ(answer.size(), 9u);
  EXPECT_EQ(answer.begin()->timestamp, get_t(1538352001));
  EXPECT_EQ(answer.rbegin()->timestamp, get_t(1538361200));
  const double kAbsPointError = 1e-5;
  const auto& pos = *answer.begin();
  EXPECT_EQ(pos.accuracy, positions1[0].accuracy);
  EXPECT_EQ(pos.user_id, "");
  EXPECT_EQ(pos.accuracy, positions1[0].accuracy);
  EXPECT_NEAR(pos.lon, positions1[0].lon, kAbsPointError);
  EXPECT_NEAR(pos.lat, positions1[0].lat, kAbsPointError);

  // 2018-10-01T01:00:00 to 2018-10-01T02:00:00
  answer = geohistory::user::ReadFromS3(
      mock_s3, "id", std::chrono::system_clock::from_time_t(1538355600),
      std::chrono::system_clock::from_time_t(1538359199), ctx);
  ASSERT_EQ(answer.size(), 3u);
  EXPECT_EQ(answer.begin()->timestamp, get_t(1538355600));
  EXPECT_EQ(answer.rbegin()->timestamp, get_t(1538357600));

  // 2018-10-01T01:16:40 to 2018-10-03T10:00:00
  answer = geohistory::user::ReadFromS3(
      mock_s3, "id", std::chrono::system_clock::from_time_t(1538356600),
      std::chrono::system_clock::from_time_t(1538560800), ctx);
  ASSERT_EQ(answer.size(), 7u);
  EXPECT_EQ(answer.begin()->timestamp, get_t(1538356600));
  EXPECT_EQ(answer.rbegin()->timestamp, get_t(1538560800));

  // 2018-10-01T01:13:20 to 2018-10-03T10:00:00
  answer = geohistory::user::ReadFromS3(
      mock_s3, "id", std::chrono::system_clock::from_time_t(1538356400),
      std::chrono::system_clock::from_time_t(1538560800), ctx);
  ASSERT_EQ(answer.size(), 8u);
  EXPECT_EQ(answer.begin()->timestamp, get_t(1538355600));
  EXPECT_EQ(answer.rbegin()->timestamp, get_t(1538560800));
}

TEST(GetHourFromPath, NormalCase) {
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/07"), 7);
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/10"), 10);
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/12"), 12);
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/00"), 0);
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/23"), 23);
}

TEST(GetHourFromPath, ErrorCase) {
  EXPECT_EQ(geohistory::user::detail::GetHourFromPath("history/123/20181001/7"),
            -1);
  EXPECT_EQ(geohistory::user::detail::GetHourFromPath("history/123/20181001/"),
            -1);
  EXPECT_EQ(
      geohistory::user::detail::GetHourFromPath("history/123/20181001/-7"), -1);
}
