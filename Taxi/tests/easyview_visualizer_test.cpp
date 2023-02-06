#include "easyview_visualizer_test.hpp"

namespace tests {
EasyviewVisualizer::EasyviewVisualizer(const std::string& path) {
  constexpr fs::blocking::OpenMode mode{
      fs::blocking::OpenFlag::kWrite,
      fs::blocking::OpenFlag::kCreateIfNotExists,
      fs::blocking::OpenFlag::kTruncate};
  try {
    file_ = fs::blocking::CFile{path, mode, boost::filesystem::perms::all_all};
  } catch (std::runtime_error& ex) {
    throw std::runtime_error(fmt::format(
        "Failed to open the dump file for write \"{}\": {}", path, ex.what()));
  }
}

void EasyviewVisualizer::SetColor(Color col) { cur_color_ = col; }

void EasyviewVisualizer::WritePointColor() {
  std::string point_color_yson(
      fmt::format("{{\"color\"=\"rgba({}, {}, {}, {})\"}}", cur_color_.red,
                  cur_color_.green, cur_color_.blue, kAlpha));
  file_.Write(fmt::format("{{\"_pointstyle\"={}}};\n", point_color_yson));
}

void EasyviewVisualizer::WriteLineColor() {
  std::string line_color_yson(fmt::format(
      "{{\"color\"=\"rgba({}, {}, {}, {})\"}}", cur_color_.red - kEdgeDarkening,
      cur_color_.green - kEdgeDarkening, cur_color_.blue - kEdgeDarkening,
      kAlpha));
  file_.Write(fmt::format("{{\"_linestyle\"={}}};\n", line_color_yson));
}

EasyviewVisualizer::Color EasyviewVisualizer::GenerateColor() {
  std::uniform_int_distribution<unsigned int> dist(kColorMin, kColorMax);
  Color col;
  col.red = dist(rd_);
  col.green = dist(rd_);
  col.blue = dist(rd_);
  return col;
}

void EasyviewVisualizer::WriteLine(const NTaxi::NGraph2::TPoint& start,
                                   const NTaxi::NGraph2::TPoint& end) {
  file_.Write(
      fmt::format("{{\"start_lon\"={};\"start_lat\"={};\"end_lon\"={};\"end_"
                  "lat\"={}}};\n",
                  start.Lon, start.Lat, end.Lon, end.Lat));
}

void EasyviewVisualizer::WritePolygon(const models::Polygon& polygon) {
  SetColor(GenerateColor());
  WritePointColor();
  std::string polygon_points;
  std::string appendix = "";
  for (const auto& point : polygon.points) {
    polygon_points.append(
        fmt::format("{}[{};{}]", appendix, point.Lon, point.Lat));
    appendix = ";";
  }
  file_.Write(fmt::format("{{\"polygon\"=[{}]}};\n", polygon_points));
  WriteLineColor();
  for (const auto& edge : polygon.real_edges) {
    WriteLine(edge.edge_start, edge.edge_end);
    // Fixed points coordinates for testing
    /*file_.Write(
        fmt::format("{{\"start_lon\"={};\"start_lat\"={};\"end_lon\"={};\"end_"
                    "lat\"={};\"fixed_lon\"={};\"fixed_lat\"={}}};\n",
                    edge.edge_start.Lon, edge.edge_start.Lat, edge.edge_end.Lon,
                    edge.edge_end.Lat, edge.nearest_fixed_point.Lon,
                    edge.nearest_fixed_point.Lat));*/
  }
  // Fixed points coordinates for testing
  /*file_.Write(fmt::format(
      "{{\"polygon\"=[{}]\"fixed_lon\"={};\"fixed_lat\"={}}};\n",
      polygon_points, polygon.fixed_point.Lon, polygon.fixed_point.Lat));*/
}

void EasyviewVisualizer::WriteEdge(const models::NearestEdge& edge) {
  const auto& points = edge.nearest_fixed_points;
  const auto& id = points[0].position_id;
  if (fixed_points_colors_.find(id) == fixed_points_colors_.end()) {
    fixed_points_colors_.insert({id, GenerateColor()});
  }
  SetColor(fixed_points_colors_[id]);
  WriteLineColor();
  WriteLine(models::ToGraphPoint(edge.start), models::ToGraphPoint(edge.end));
}

}  // namespace tests
