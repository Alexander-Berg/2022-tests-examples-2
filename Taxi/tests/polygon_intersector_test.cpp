#include <fstream>

#include <userver/formats/json/serialize.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <models/polygon_intersector.hpp>

namespace tests {
struct PolygonIntersectorTest : public ::testing::Test {
  models::BoostVectorPolygon CreatePolygon(
      std::initializer_list<models::BoostPoint> points) {
    models::BoostVectorPolygon new_polygon;
    for (const auto& point : points) {
      new_polygon.outer().push_back(point);
    }
    return new_polygon;
  }

  void AddPolygon(std::initializer_list<models::BoostPoint> points) {
    input_polygons_.emplace_back(models::InputPolygon{
        CreatePolygon(points), std::to_string(input_polygons_.size())});
  }

  // Uncomment if you want to read polygons from a json file that comes as
  // response for /admin/v1/point/download handle of taxi-admin-surger
  // TODO: replace std::ifstream with fs::blocking (but should still work)
  /*void ReadFromPointsJsonFile(const std::string& path) {
    std::ifstream json_stream;
    json_stream.open(path);
    auto json_value = formats::json::FromStream(json_stream);
    auto items_json = json_value["items"];
    for (const auto& point_json : items_json) {
      std::string position_id = point_json["position_id"].As<std::string>();
      if (point_json.HasMember("polygon")) {
        models::BoostVectorPolygon new_polygon;
        auto polygon_points_json = point_json["polygon"]["points"];
        for (const auto& polygon_point_json : polygon_points_json) {
          new_polygon.outer().emplace_back(
              models::BoostPoint(polygon_point_json[0].As<double>(),
                                 polygon_point_json[1].As<double>()));
        }
        input_polygons_.emplace_back(
            models::InputPolygon{std::move(new_polygon), position_id});
      }
    }
  }*/

  std::vector<models::InputPolygon> input_polygons_;
};

// Polygons that were failing in testing
UTEST_F(PolygonIntersectorTest, TrickyMultiPolygon) {
  models::bg::model::multi_polygon<models::BoostVectorPolygon> multi_polygon;
  models::BoostVectorPolygon first =
      CreatePolygon({{37.438251354078311, 55.773504033844766},
                     {37.436640248357946, 55.773777940680908},
                     {37.432126456167822, 55.772834012810385},
                     {37.428148999999991, 55.772705000000002},
                     {37.42669699999999, 55.772660000000002},
                     {37.448907999999989, 55.779656999999986},
                     {37.461776999999984, 55.782983999999999},
                     {37.467489999999998, 55.782684999999987},
                     {37.468108000000001, 55.782228000000003},
                     {37.469510999999983, 55.780760999999984},
                     {37.469075000000004, 55.779161999999985},
                     {37.468422000000004, 55.77789199999998},
                     {37.467972000000003, 55.777065999999991},
                     {37.467638999999991, 55.776943999999986},
                     {37.451182472040195, 55.775017683772923},
                     {37.450834999999984, 55.775328999999999},
                     {37.448360999999977, 55.776229000000001},
                     {37.436640252725816, 55.77377793778593}});
  multi_polygon.push_back(first);
  models::BoostVectorPolygon second =
      CreatePolygon({{37.427964000000003, 55.775252999999992},
                     {37.411535999999984, 55.783546999999999},
                     {37.414588999999978, 55.789597999999984},
                     {37.447771999999986, 55.794333999999992},
                     {37.449471999999986, 55.793738999999988},
                     {37.454542000000004, 55.791823999999991},
                     {37.479275000000001, 55.778537},
                     {37.487409999999983, 55.77319399999999},
                     {37.472050999999993, 55.768385999999992},
                     {37.469572999999997, 55.768179000000003},
                     {37.45591906689522, 55.770500322857629},
                     {37.453400999999985, 55.773030000000006},
                     {37.450834999999984, 55.775328999999999},
                     {37.448360999999977, 55.776229000000001},
                     {37.436640252725816, 55.77377793778593}});
  models::bg::model::multi_polygon<models::BoostVectorPolygon> res;
  ASSERT_NO_THROW(models::bg::difference(multi_polygon, second, res));
}

UTEST_F(PolygonIntersectorTest, SimpleTest) {
  AddPolygon({{2, 2}, {4, 7}, {7, 2}});
  AddPolygon({{5, 4}, {6, 8}, {9, 8}});

  auto result = models::polygon_intersector::GetNonOverlappingPolygons(
      input_polygons_, models::polygon_intersector::ValidationPolicy::kThrow);
  ASSERT_EQ(result.size(), 3);
}

UTEST_F(PolygonIntersectorTest, SimpleEnclosedTest) {
  AddPolygon({{2, 2}, {4, 7}, {7, 2}});
  AddPolygon({{5, 4}, {6, 8}, {9, 8}});
  AddPolygon({{1, 1}, {5, 10}, {11, 10}, {11, 1}});

  auto result = models::polygon_intersector::GetNonOverlappingPolygons(
      input_polygons_, models::polygon_intersector::ValidationPolicy::kThrow);
  ASSERT_EQ(result.size(), 4);
}

// Polygons that were failing in testing
UTEST_F(PolygonIntersectorTest, TrickyPolygons) {
  AddPolygon({{37.4267, 55.7727},
              {37.4489, 55.7797},
              {37.4618, 55.783},
              {37.4675, 55.7827},
              {37.4681, 55.7822},
              {37.4695, 55.7808},
              {37.4691, 55.7792},
              {37.4684, 55.7779},
              {37.468, 55.7771},
              {37.4676, 55.7769},
              {37.4327, 55.7729},
              {37.4281, 55.7727},
              {37.4267, 55.7727}});

  AddPolygon({{37.428, 55.7753},
              {37.4115, 55.7835},
              {37.4146, 55.7896},
              {37.4478, 55.7943},
              {37.4495, 55.7937},
              {37.4545, 55.7918},
              {37.4793, 55.7785},
              {37.4874, 55.7732},
              {37.4721, 55.7684},
              {37.4696, 55.7682},
              {37.4559, 55.7705},
              {37.4534, 55.773},
              {37.4508, 55.7753},
              {37.4484, 55.7762},
              {37.4366, 55.7738},
              {37.428, 55.7753}});
  ASSERT_NO_THROW(models::polygon_intersector::GetNonOverlappingPolygons(
      input_polygons_, models::polygon_intersector::ValidationPolicy::kThrow));
}

}  // namespace tests
