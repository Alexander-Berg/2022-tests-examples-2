#pragma once
#include <random>

#include <userver/fs/blocking/c_file.hpp>
#include <userver/utest/utest.hpp>

#include <utils/polygon_calculator.hpp>

#include <models/nearest_edge.hpp>

namespace tests {

// Class for writing polygons info in easyview format, useful for testing
class EasyviewVisualizer {
 public:
  struct Color {
    unsigned int red;
    unsigned int green;
    unsigned int blue;
  };
  EasyviewVisualizer(const std::string& path);
  void WritePolygon(const models::Polygon& polygon);
  void WriteEdge(const models::NearestEdge& edge);
  void SetColor(Color col);
  void WritePointColor();
  void WriteLineColor();
  void WriteLine(const NTaxi::NGraph2::TPoint& start,
                 const NTaxi::NGraph2::TPoint& end);
  Color GenerateColor();

 private:
  fs::blocking::CFile file_;
  std::random_device rd_;
  const unsigned int kEdgeDarkening = 20;
  const unsigned int kColorMin = kEdgeDarkening;
  const unsigned int kColorMax = 200;
  const unsigned int kAlpha = 100;
  std::unordered_map<std::string, Color> fixed_points_colors_;
  Color cur_color_;
};
}  // namespace tests
