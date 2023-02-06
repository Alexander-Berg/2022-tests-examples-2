#include "edge_positions.hpp"

#include <gtest/gtest.h>

TEST(GeobusEdgePositions, One) {
  geobus::EdgePositions expected_pos;
  expected_pos.timestamp = std::chrono::system_clock::now();
  expected_pos.positions.emplace_back(
      models::DriverId("1", "1", "01234"),
      geobus::EdgePosition{expected_pos.timestamp,
                           {geobus::OptionEdgePosition{10, 10, 1, .5f, .5f},
                            geobus::OptionEdgePosition{11, 11, 2, .5f, .5f}}});
  expected_pos.positions.emplace_back(
      models::DriverId("1", "1", "56789"),
      geobus::EdgePosition{expected_pos.timestamp,
                           {geobus::OptionEdgePosition{12, 12, 3, .5f, .5f},
                            geobus::OptionEdgePosition{13, 13, 4, .5f, .5f}}});

  const std::string& data = geobus::SerializeEdgePositions(expected_pos);
  ASSERT_FALSE(data.empty());

  const auto& actual_pos = geobus::DeserializeEdgePositions(data);

  EXPECT_EQ(std::chrono::system_clock::to_time_t(expected_pos.timestamp),
            std::chrono::system_clock::to_time_t(actual_pos.timestamp));

  EXPECT_EQ(expected_pos.positions.size(), actual_pos.positions.size());
  for (size_t i = 0; i < expected_pos.positions.size(); ++i) {
    const auto& expected_driver = expected_pos.positions[i];
    const auto& actual_driver = actual_pos.positions[i];

    EXPECT_TRUE(models::detail::DriverIdEqualTo()(expected_driver.first,
                                                  actual_driver.first));

    EXPECT_EQ(
        std::chrono::system_clock::to_time_t(expected_driver.second.timestamp),
        std::chrono::system_clock::to_time_t(actual_driver.second.timestamp));

    EXPECT_EQ(expected_driver.second.options.size(),
              actual_driver.second.options.size());

    for (size_t j = 0; j < expected_driver.second.options.size(); ++j) {
      const auto& expected_op = expected_driver.second.options[j];
      const auto& actual_op = actual_driver.second.options[j];

      EXPECT_TRUE(utils::geometry::IsSamePoint(expected_op, actual_op));
      EXPECT_EQ(expected_op.persistent_edge, actual_op.persistent_edge);
      EXPECT_NEAR(expected_op.edge_displacement, actual_op.edge_displacement,
                  0.00001f);
      EXPECT_NEAR(expected_op.probability, actual_op.probability, 0.005f);
    }
  }
}
