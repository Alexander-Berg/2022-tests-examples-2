#include <channels/edge_positions/edge_positions.hpp>
#include <channels/edge_positions/test_traits.hpp>

#include <lowlevel/fb_serialization_test.hpp>

#include <gtest/gtest.h>

namespace geobus::lowlevel {

std::string DoSerializeEdgePositions(const EdgePositions& edge_positions,
                                     bool enable_legacy, bool compress);

TEST(GeobusEdgePositions, One) {
  EdgePositions expected_pos;
  expected_pos.timestamp = std::chrono::system_clock::now();
  expected_pos.positions.emplace_back(EdgePosition{
      {OptionEdgePosition{10, 10, 1, .5f, .5f, 180, -1.0, 16.6},
       OptionEdgePosition{11, 11, 2, .5f, .5f, 180, -2.0, 16.6}},
      types::DriverId{"1_01234"},
      expected_pos.timestamp,
  });
  expected_pos.positions.emplace_back(EdgePosition{
      {OptionEdgePosition{12, 12, 3, .5f, .5f, 180, -3.0, 16.6},
       OptionEdgePosition{13, 13, 4, .5f, .5f, 180, -4.0, 16.6}},
      types::DriverId{"1_56789"},
      expected_pos.timestamp,
  });

  const std::string& data = SerializeEdgePositions(expected_pos);
  ASSERT_FALSE(data.empty());

  const auto& actual_pos = DeserializeEdgePositions(data);

  EXPECT_EQ(std::chrono::system_clock::to_time_t(expected_pos.timestamp),
            std::chrono::system_clock::to_time_t(actual_pos.timestamp));

  EXPECT_EQ(expected_pos.positions.size(), actual_pos.positions.size());
  for (size_t i = 0; i < expected_pos.positions.size(); ++i) {
    const auto& expected_driver = expected_pos.positions[i];
    const auto& actual_driver = actual_pos.positions[i];

    EXPECT_EQ(expected_driver.driver_dbid_uuid, actual_driver.driver_dbid_uuid);

    EXPECT_EQ(std::chrono::system_clock::to_time_t(expected_driver.timestamp),
              std::chrono::system_clock::to_time_t(actual_driver.timestamp));

    EXPECT_EQ(expected_driver.options.size(), actual_driver.options.size());

    for (size_t j = 0; j < expected_driver.options.size(); ++j) {
      const auto& expected_op = expected_driver.options[j];
      const auto& actual_op = actual_driver.options[j];

      EXPECT_NEAR(expected_op.longitude, actual_op.longitude, 0.0003);
      EXPECT_NEAR(expected_op.latitude, actual_op.latitude, 0.0003);
      EXPECT_EQ(expected_op.persistent_edge, actual_op.persistent_edge);
      EXPECT_NEAR(expected_op.edge_displacement, actual_op.edge_displacement,
                  0.00001f);
      EXPECT_NEAR(expected_op.probability, actual_op.probability, 0.005f);
      EXPECT_NEAR(expected_op.speed, actual_op.speed, 0.005f);
      EXPECT_EQ(expected_op.direction, actual_op.direction);
      EXPECT_EQ(expected_op.log_likelihood, actual_op.log_likelihood);
    }
  }
}

TEST(GeobusEdgePositions, OneNoLegacy) {
  EdgePositions expected_pos;
  expected_pos.timestamp = std::chrono::system_clock::now();
  expected_pos.positions.emplace_back(EdgePosition{
      {OptionEdgePosition{10, 10, 1, .5f, .5f, 180, -1.0, 16.6},
       OptionEdgePosition{11, 11, 2, .5f, .5f, 180, -2.0, 16.6}},
      types::DriverId{"1_01234"},
      expected_pos.timestamp,
  });
  expected_pos.positions.emplace_back(EdgePosition{
      {OptionEdgePosition{12, 12, 3, .5f, .5f, 180, -3.0, 16.6},
       OptionEdgePosition{13, 13, 4, .5f, .5f, 180, -4.0, 16.6}},
      types::DriverId{"1_56789"},
      expected_pos.timestamp,
  });

  // false = do not write legacy attribute
  // true = use compression
  const std::string& data = DoSerializeEdgePositions(expected_pos, false, true);
  ASSERT_FALSE(data.empty());

  const auto& actual_pos = DeserializeEdgePositions(data);

  EXPECT_EQ(std::chrono::system_clock::to_time_t(expected_pos.timestamp),
            std::chrono::system_clock::to_time_t(actual_pos.timestamp));

  EXPECT_EQ(expected_pos.positions.size(), actual_pos.positions.size());
  for (size_t i = 0; i < expected_pos.positions.size(); ++i) {
    const auto& expected_driver = expected_pos.positions[i];
    const auto& actual_driver = actual_pos.positions[i];

    EXPECT_EQ(expected_driver.driver_dbid_uuid, actual_driver.driver_dbid_uuid);

    EXPECT_EQ(std::chrono::system_clock::to_time_t(expected_driver.timestamp),
              std::chrono::system_clock::to_time_t(actual_driver.timestamp));

    EXPECT_EQ(expected_driver.options.size(), actual_driver.options.size());

    for (size_t j = 0; j < expected_driver.options.size(); ++j) {
      const auto& expected_op = expected_driver.options[j];
      const auto& actual_op = actual_driver.options[j];

      EXPECT_NEAR(expected_op.longitude, actual_op.longitude, 0.0003);
      EXPECT_NEAR(expected_op.latitude, actual_op.latitude, 0.0003);
      EXPECT_EQ(expected_op.persistent_edge, actual_op.persistent_edge);
      EXPECT_NEAR(expected_op.edge_displacement, actual_op.edge_displacement,
                  0.00001f);
      EXPECT_NEAR(expected_op.probability, actual_op.probability, 0.005f);
      EXPECT_NEAR(expected_op.speed, actual_op.speed, 0.005f);
      EXPECT_EQ(expected_op.direction, actual_op.direction);
      EXPECT_EQ(expected_op.log_likelihood, actual_op.log_likelihood);
    }
  }
}

namespace edge_positions {

INSTANTIATE_TYPED_TEST_SUITE_P(DriverEdgePositionTest,
                               FlatbuffersSerializationTest,
                               types::DriverEdgePosition);

}

}  // namespace geobus::lowlevel
