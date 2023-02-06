#include <userver/rcu/rcu.hpp>
#include <userver/utest/utest.hpp>

#include <eventus/mappers/set_polygon_groups_mapper.hpp>
#include <eventus/order_event.hpp>

namespace eventus::mappers {

namespace {

using namespace eventus::polygons;

class TestPolygonGroupsForPointGetter
    : public eventus::polygons::PolygonGroupsGetterBase {
 public:
  TestPolygonGroupsForPointGetter(PolygonsPack polygons_pack) {
    polygons_pack_.Assign(polygons_pack);
  }

 private:
  rcu::ReadablePtr<PolygonsPack> GetPolygonsPack() const override {
    return polygons_pack_.Read();
  }
  rcu::Variable<PolygonsPack> polygons_pack_;
};

PolygonsPack ToPolygonsPack(std::vector<PolygonPack> vec) {
  PolygonsPack res;
  for (auto p : vec) {
    res.emplace(p.identity, p);
  }
  return res;
}

eventus::mappers::Event GetEventWithPoints(
    std::vector<double> src, std::vector<std::vector<double>> dst) {
  eventus::mappers::Event res({});
  res.Set(eventus::order_event::keys::kSourceGeopoint, src);
  res.Set(eventus::order_event::keys::kDestinationsGeopoint, dst);
  return res;
}

void MakeMapperTest(std::vector<PolygonPack> pack_vec,
                    std::vector<double> src_point,
                    std::vector<std::vector<double>> dst_points,
                    std::unordered_set<std::string> src_groups_expected,
                    std::unordered_set<std::string> dst_groups_expected) {
  PolygonsPack pack = ToPolygonsPack(pack_vec);
  auto getter = TestPolygonGroupsForPointGetter(pack);

  auto mapper = eventus::mappers::SetPolygonGroupsMapper({}, getter);

  auto event = GetEventWithPoints(src_point, dst_points);

  mapper.Map(event);

  ASSERT_EQ(event.Get<std::unordered_set<std::string>>("source_polygon_groups"),
            src_groups_expected);
  ASSERT_EQ(
      event.Get<std::unordered_set<std::string>>("destination_polygon_groups"),
      dst_groups_expected);
}

}  // namespace

UTEST(PolygonGroupsMapper, TestMapper1) {
  std::vector<PolygonPack> pack_vec{PolygonPack{
      "a", {"a", "b"}, {"polygon_1", {{1.0, -0.5}, {-1.0, -0.5}, {0.0, 1.0}}}}};

  std::vector<double> src_point = {0.0, 0.0};
  std::vector<std::vector<double>> dst_points = {{0.0, 0.0}};

  auto src_groups = std::unordered_set<std::string>{"a", "b"};
  auto dst_groups = std::unordered_set<std::string>{"a", "b"};

  MakeMapperTest(pack_vec, src_point, dst_points, src_groups, dst_groups);
}

UTEST(PolygonGroupsMapper, TestMapper2) {
  std::vector<PolygonPack> pack_vec{PolygonPack{
      "a", {"a", "b"}, {"polygon_1", {{1.0, -0.5}, {-1.0, -0.5}, {0.0, 1.0}}}}};

  std::vector<double> src_point = {10.0, 10.0};
  std::vector<std::vector<double>> dst_points = {{10.0, 10.0}};

  auto src_groups = std::unordered_set<std::string>{};
  auto dst_groups = std::unordered_set<std::string>{};

  MakeMapperTest(pack_vec, src_point, dst_points, src_groups, dst_groups);
}

UTEST(PolygonGroupsMapper, TestMapper3) {
  std::vector<PolygonPack> pack_vec{
      PolygonPack{
          "a", {"a"}, {"polygon_1", {{1.0, -0.5}, {-1.0, -0.5}, {0.0, 1.0}}}},
      PolygonPack{
          "b", {"b"}, {"polygon_1", {{2.0, 9.0}, {-2.0, 9.0}, {0.0, 11.0}}}}};

  std::vector<double> src_point = {0.0, 0.0};
  std::vector<std::vector<double>> dst_points = {{0.0, 0.0}, {0.0, 10.0}};

  auto src_groups = std::unordered_set<std::string>{"a"};
  auto dst_groups = std::unordered_set<std::string>{"b"};

  MakeMapperTest(pack_vec, src_point, dst_points, src_groups, dst_groups);
}

UTEST(PolygonGroupsMapper, TestMapper4) {
  std::vector<PolygonPack> pack_vec{
      PolygonPack{
          "a", {"a"}, {"polygon_1", {{1.0, -0.5}, {-1.0, -0.5}, {0.0, 1.0}}}},
      PolygonPack{
          "b", {"b"}, {"polygon_1", {{2.0, -1.0}, {-2.0, -1.0}, {0.0, 1.0}}}}};

  std::vector<double> src_point = {0.0, 0.0};
  std::vector<std::vector<double>> dst_points = {{0.0, 0.0}};

  auto src_groups = std::unordered_set<std::string>{"a", "b"};
  auto dst_groups = std::unordered_set<std::string>{"a", "b"};

  MakeMapperTest(pack_vec, src_point, dst_points, src_groups, dst_groups);
}

}  // namespace eventus::mappers
