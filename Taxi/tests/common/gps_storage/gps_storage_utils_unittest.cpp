#include <gtest/gtest.h>

#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/range/numeric.hpp>

#include <chrono>
#include <fstream>

#include <clients/adjusting/fallback/route_adjust_fallback.hpp>
#include <clients/graphite.hpp>
#include <common/gps_storage/gps_storage_common.hpp>
#include <common/gps_storage/track_filter.hpp>
#include <common/test_config.hpp>
#include <config/geoservice_config.hpp>
#include <httpclient/client.hpp>
#include <threads/async.hpp>
#include <utils/helpers/json.hpp>
#include <utils/time.hpp>
#include <utils/uuid4.hpp>

static config::Config cfg(config::DocsMapForTest());

using MockAdjust = clients::route_adjust::ClientFallback;

TEST(gps_archive, TestBuckePathParseTime) {
  const auto bp = gps_storage::utils::BucketPath{"data", "db", "driver_id",
                                                 "20170102", "21"};
  const auto t = bp.GetBucketTime();
  const auto tt = std::chrono::system_clock::to_time_t(t);

  boost::posix_time::ptime pt{
      boost::gregorian::date{2017, 01, 02},
      boost::posix_time::seconds(
          21 * geohistory::utils::BucketDuration::period::num)};
  ASSERT_EQ(tt, PTimeToTime(pt));
  ASSERT_EQ(geohistory::utils::GetHourCount(t), 21);
}

TEST(gps_archive, TestFbConversions) {
  gps_storage::GpsPointType p;
  p.latitude = 0.42;
  p.longitude = 42;
  p.bearing = 0.01;
  p.speed = 1.0;
  p.update = std::chrono::duration_cast<gps_storage::GpsPointType::duration>(
                 std::chrono::system_clock::now().time_since_epoch())
                 .count();
  p.guided_latitude = 0.43;
  p.guided_longitude = 43;
  p.cost = 1.1;
  p.status = 4;
  p.distance = 42.42;
  p.order_status = 7;

  const auto bin = gps_storage::point::MarshallPoint(p);
  gps_storage::GpsPointType restored = gps_storage::point::UnmarshallPoint(bin);
  ASSERT_EQ(p, restored);
}

TEST(gps_archive, TestFbConversionsErr) {
  const std::string uuid = utils::generators::Uuid4();
  std::string wrong_data = "This is definitely not a flatbuffer";
  ASSERT_THROW(gps_storage::point::UnmarshallPoint(wrong_data),
               std::runtime_error);
}

static std::string Load(const std::string& filename) {
  std::string full_name = std::string(SOURCE_DIR) + "/tests/data/" + filename;
  std::ifstream file(full_name, std::ios::binary | std::ios::ate);
  std::streamsize size = file.tellg();
  file.seekg(0, std::ios::beg);
  std::vector<char> buffer(size);
  file.read(buffer.data(), size);
  return std::string(buffer.begin(), buffer.end());
}

TEST(gps_archive, TestLoadRealData) {
  const auto data = Load("test_route.fb");
  const auto result = gps_storage::point::UnmarshallRoute(data);

  // check size
  ASSERT_EQ(result.size(), 10u);

  // check some element in the middle
  ASSERT_NEAR(result[1].latitude, 55.7751, 0.0001);
  ASSERT_EQ(result[1].update, 1505926728000000ll);
  ASSERT_EQ(result[1].status, 1);

  // test_route.fb was created before order_status was added, should default to
  // 0
  ASSERT_EQ(result[1].order_status, 0);
}

namespace gps_storage {
Line PreprocessData(
    const gps_storage::GpsGetResult& points,
    const boost::optional<double>& epsilon,
    const boost::optional<gps_storage::line_filter::FilterParams>&
        filter_params);

Line PostprocessData(const gps_storage::GpsGetResult& points,
                     const handlers::Context& context,
                     const boost::optional<double>& epsilon,
                     const boost::optional<AdjustParams>& adjust_params);
}  // namespace gps_storage

TEST(gps_archive, TestFilter) {
  std::vector<gps_storage::GpsPointType> points(11);

  // retain, the first one
  points[0] = gps_storage::GpsPointType{0, 0, 1.0, 1.0, 0, 0, 0, 1, 0, 0};
  // remove, not unique
  points[1] = gps_storage::GpsPointType{0, 0, 1.0, 1.0, 0, 0, 0, 1, 1, 0};
  // remove, not unique
  points[2] = gps_storage::GpsPointType{0, 0, 1.0, 1.0, 0, 0, 0, 1, 2, 0};
  // remove, not unique
  points[3] = gps_storage::GpsPointType{0, 0, 1.0, 1.0, 0, 0, 0, 1, 3, 0};

  // retain, first in new status
  points[4] = gps_storage::GpsPointType{0, 0, 1.00001, 1.0, 0, 0, 0, 2, 4, 0};
  points[5] = gps_storage::GpsPointType{0, 0, 1.00002, 1.0, 0, 0, 0, 2, 5, 0};
  points[6] = gps_storage::GpsPointType{0, 0, 1.00203, 1.0, 0, 0, 0, 2, 6, 0};
  points[7] = gps_storage::GpsPointType{0, 0, 1.00004, 1.0, 0, 0, 0, 2, 7, 0};
  points[8] = gps_storage::GpsPointType{0, 0, 1.00005, 1.0, 0, 0, 0, 2, 8, 0};

  points[9] = gps_storage::GpsPointType{0, 0, 2.00001, 1.0, 0, 0, 0, 2, 9, 0};
  points[10] = gps_storage::GpsPointType{0, 0, 2.00002, 1.0, 0, 0, 0, 2, 10, 0};

  gps_storage::line_filter::FilterParams fparams{true, 300, 1000,
                                                 5,    2,   0.000001};

  auto result = gps_storage::line_filter::Filter(points, fparams);

  auto find_p = [&result](int p) -> boost::optional<gps_storage::GpsPointType> {
    auto it = std::find_if(result.begin(), result.end(),
                           [p](const gps_storage::GpsPointType point) {
                             return point.update == p;
                           });
    if (it == result.end()) return boost::none;
    return boost::make_optional(*it);
  };

  ASSERT_TRUE((bool)find_p(0));
  ASSERT_TRUE((bool)find_p(4));

  ASSERT_TRUE((bool)find_p(6) &&
              std::abs(find_p(6)->longitude - 1.00004) < 0.00001);
}

std::vector<gps_storage::GpsPointType> VectorFromTestJson(
    const Json::Value& js) {
  std::vector<gps_storage::GpsPointType> res;
  for (const auto& q : js) {
    gps_storage::GpsPointType p;
    p.longitude = q[0].asFloat();
    p.latitude = q[1].asFloat();
    p.update = std::chrono::duration_cast<gps_storage::GpsPointType::duration>(
                   std::chrono::seconds(q[2].asInt()))
                   .count();
    p.status = q[3].asInt();
    res.push_back(p);
  }
  return res;
}

gps_storage::GpsGetResult MapFromTestJson(const Json::Value& js) {
  gps_storage::GpsGetResult res;
  for (const auto& q : js) {
    gps_storage::GpsPointType p;
    p.longitude = q[1].asFloat();
    p.latitude = q[0].asFloat();
    p.update = q[2].asInt64() * 1000 * 1000;
    p.status = q[3].asInt();
    p.order_status = q[4].asInt();
    res[p.update] = p;
  }
  return res;
}

TEST(gps_archive, TestSimplifyReal) {
  const auto data = Load("long_track.json");
  Json::Value js = utils::helpers::ParseJson(data);
  gps_storage::line_filter::FilterParams fparams{true, 300, 1000,
                                                 5,    3,   0.000001};
  auto result =
      gps_storage::PreprocessData(MapFromTestJson(js), 0.0001, fparams);

  ASSERT_TRUE(result.size() < 5000 && result.size() > 100);
}

TEST(gps_archive, TestPostprocessEmpty) {
  LogExtra le;
  clients::Graphite g;

  auto docs_map = config::DocsMapForTest();
  config::Config cfg(docs_map);

  handlers::Context ctx{cfg, g, le};

  utils::Async async(1, "async", false);
  utils::http::Client http(async, 1, "test_client", false);
  MockAdjust mock_adjust;

  const gps_storage::AdjustParams adjust_params{
      cfg.Get<config::RouteAdjust>().route, mock_adjust};

  auto result = gps_storage::PostprocessData({}, ctx, 0.0001, adjust_params);

  ASSERT_TRUE(result.empty());
}
