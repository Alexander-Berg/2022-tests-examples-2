#include <userver/utest/utest.hpp>

#include <blender/estimations.hpp>

namespace {

// real numbers for some iphone model
constexpr double kUnitWidth = 54.5;
constexpr double kMDashWidth = 14.48;
constexpr double kNDashWidth = 9.008;
constexpr double kMDashCoeff = 0.1;
constexpr double kMaxLinesInTitle = 3;

void TestEstimation(const std::string& title, int expected_min_cells) {
  EXPECT_EQ(
      blender::EstimateMinCells(title, kUnitWidth, kMDashWidth, kNDashWidth,
                                kMDashCoeff, kMaxLinesInTitle),
      expected_min_cells);
}

void TestEstimationV2(const std::string& title, int expected_min_cells) {
  EXPECT_EQ(
      blender::EstimateMinCellsV2(title, kUnitWidth, kMDashWidth, kNDashWidth,
                                  kMDashCoeff, kMaxLinesInTitle),
      expected_min_cells);
}

}  // namespace

TEST(EstimateMinCells, Simple) {
  TestEstimation("Домой", 1);
  TestEstimation("На работу", 2);
  TestEstimation("Садовническая", 3);
  TestEstimation("Толстого", 2);
  TestEstimation("Константинопольская набережная, 82", 4);
  TestEstimation("Великая Константинопольская набережная, 82", 4);
  TestEstimation("О Великая Константинопольская набережная, 82", 6);

  TestEstimationV2("Домой", 1);
  TestEstimationV2("На работу", 2);
  TestEstimationV2("Садовническая", 3);
  TestEstimationV2("Толстого", 2);
  TestEstimationV2("Константинопольская набережная, 82", 4);
  TestEstimationV2("Великая Константинопольская набережная, 82", 4);
  TestEstimationV2("О Великая Константинопольская набережная, 82", 4);

  auto min_width = blender::EstimateMinCellsV2("пристань Нижний Новгород", 54.5,
                                               14.48, 9.008, 0.5, 2);
  EXPECT_EQ(min_width, 4);
}

TEST(EstimateMinCells, Split) {
  TestEstimation("Льва Толстого, 16", 2);
  TestEstimation("Льва Толстого, 16, строение 1", 3);
}
