#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/engine/run_in_coro.hpp>

#include <candidates/geoindexes/kdtree/kdtree.hpp>
#include <candidates/processors/dummy/dummy.hpp>
#include <candidates/result_storages/dummy/dummy.hpp>
#include <models/geometry/serialize.hpp>
#include <userver/server/handlers/exceptions.hpp>

namespace {

using DummyProcessor = candidates::processors::Dummy;
using DummyStorage = candidates::result_storages::Dummy;
using StorageResult = candidates::result_storages::Result;
using candidates::GeoMember;
using models::geometry::Point;

auto CreateEnvironment() {
  return candidates::Environment{dynamic_config::GetDefaultSnapshot()};
}

class KDTreeGeoIndexTest : public ::testing::Test {
 protected:
  void SetUp() override {
    std::vector<candidates::GeoMember> members = {
        {Point(92.865575, 55.986885), "id1"},
        {Point(39.051504, 45.033745), "id2"},
        {Point(30.370960, 60.050888), "id3"},
        {Point(30.206501, 59.999286), "id4"},
        {Point(24.876888, 59.445591), "id5"},
        {Point(37.811739, 55.324163), "id6"},
        {Point(39.539579, 52.627610), "id7"},
        {Point(24.151080, 56.880285), "id8"},
        {Point(30.322031, 59.955284), "id9"},
        {Point(30.515912, 59.831577), "id10"},
        {Point(83.080449, 54.991660), "id11"},
        {Point(44.459404, 40.189564), "id12"},
        {Point(44.524996, 40.191471), "id13"},
        {Point(37.735815, 55.910961), "id14"},
        {Point(49.109904, 55.819350), "id15"},
        {Point(37.647127, 55.769408), "id16"},
        {Point(30.386680, 59.924346), "id17"},
        {Point(24.735324, 59.425072), "id18"},
        {Point(39.905697, 59.247612), "id19"},
        {Point(92.827186, 55.981922), "id20"},
        {Point(20.559154, 54.731014), "id21"},
        {Point(40.094509, 47.418810), "id22"},
        {Point(82.979266, 54.992008), "id23"},
        {Point(37.332883, 55.692754), "id24"},
        {Point(44.490443, 40.019954), "id25"},
        {Point(60.543896, 56.823917), "id26"},
        {Point(37.685597, 55.878708), "id27"},
        {Point(65.545306, 57.148598), "id28"},
        {Point(47.283096, 56.106177), "id29"},
        {Point(82.596553, 49.947420), "id30"},
        {Point(30.290262, 59.827178), "id31"},
        {Point(37.713778, 55.655304), "id32"},
        {Point(76.963387, 43.238302), "id33"}};
    geoindex_ =
        std::make_shared<candidates::geoindexes::KdTree>(std::move(members));
    search_point_ = Point(37.603439, 55.731470);  // Gorky park
  }

 public:
  std::shared_ptr<candidates::geoindexes::GeoIndex> geoindex_;
  Point search_point_;
};

formats::json::Value PrepareSearchParams(Point point, uint32_t max_distance) {
  formats::json::ValueBuilder params(formats::json::Type::kObject);
  params["point"] = models::geometry::SerializeJson(point);
  params["max_distance"] = max_distance;
  return params.ExtractValue();
}

formats::json::Value PrepareSearchParams(Point tl, Point br) {
  formats::json::ValueBuilder params(formats::json::Type::kObject);
  params["tl"] = models::geometry::SerializeJson(tl);
  params["br"] = models::geometry::SerializeJson(br);
  return params.ExtractValue();
}

}  // namespace

UTEST_F(KDTreeGeoIndexTest, SampleZeroDistance) {
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  const auto params = PrepareSearchParams(search_point_, 0);
  geoindex_->Search(params, environment, processor);
  EXPECT_EQ(storage.Get().size(), 0);
}

UTEST_F(KDTreeGeoIndexTest, SampleShortDistance) {
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  const auto params = PrepareSearchParams(search_point_, 12000);
  geoindex_->Search(params, environment, processor);
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0].member.position, Point(37.647127, 55.769408));
  EXPECT_EQ(result[1].member.position, Point(37.713778, 55.655304));
}

UTEST_F(KDTreeGeoIndexTest, SampleLongDistance) {
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  const auto params = PrepareSearchParams(search_point_, 10000000);
  geoindex_->Search(params, environment, processor);
  ASSERT_EQ(storage.Get().size(), 33);
}

UTEST_F(KDTreeGeoIndexTest, NoMaxDistance) {
  formats::json::ValueBuilder params(formats::json::Type::kObject);
  params["point"] = models::geometry::SerializeJson(search_point_);
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  ASSERT_NO_THROW(
      geoindex_->Search(params.ExtractValue(), environment, processor));
  EXPECT_EQ(storage.Get().size(), 33);
}

UTEST_F_MT(KDTreeGeoIndexTest, NoPoint, 2) {
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  EXPECT_THROW(geoindex_->Search({}, environment, processor),
               server::handlers::ClientError);
}

UTEST_F_MT(KDTreeGeoIndexTest, Viewport, 2) {
  DummyStorage storage(100);
  DummyProcessor processor(storage);
  const auto& environment = CreateEnvironment();
  const auto params =
      PrepareSearchParams({37.647000, 55.655000}, {37.714000, 55.770000});
  geoindex_->Search(params, environment, processor);
  auto result = storage.Get();
  ASSERT_EQ(result.size(), 2);
  std::sort(result.begin(), result.end(),
            [](const StorageResult& lobj, const StorageResult& robj) {
              if (lobj.member.position.lon != robj.member.position.lon)
                return lobj.member.position.lon < robj.member.position.lon;
              return lobj.member.position.lat < robj.member.position.lat;
            });
  EXPECT_EQ(result[0].member.position, Point(37.647127, 55.769408));
  EXPECT_EQ(result[1].member.position, Point(37.713778, 55.655304));
}

class KDTreeSearchParams
    : public ::testing::TestWithParam<
          std::pair<std::string, std::optional<uint32_t>>> {};

TEST_P(KDTreeSearchParams, Parse) {
  const auto& [data, max_distance] = GetParam();
  const candidates::geoindexes::detail::SearchParams params(
      formats::json::FromString(data));
  EXPECT_EQ(max_distance, params.max_distance);
}

INSTANTIATE_TEST_SUITE_P(
    Serial, KDTreeSearchParams,
    ::testing::Values(
        std::make_pair("{\"point\":[1.0, 1.0]}", std::nullopt),
        std::make_pair("{\"point\":[1.0, 1.0],\"max_distance\":13}", 13),
        std::make_pair("{\"point\":[1.0, 1.0],\"max_route_distance\":13}", 13),
        std::make_pair("{\"point\":[1.0, 1.0],\"max_distance\":13,"
                       "\"max_route_distance\":88}",
                       13),
        std::make_pair("{\"point\":[1.0, 1.0],\"max_distance\":88,"
                       "\"max_route_distance\":13}",
                       13)));
