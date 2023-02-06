#include <test/time_helpers.h>
#include <geobus/channels/timelefts/timelefts.hpp>
#include <geobus/channels/timelefts/timelefts_generator.hpp>
#include <lowlevel/fb_serialization_test.hpp>
#include "lowlevel.hpp"
#include "test_traits.hpp"

#include <gtest/gtest.h>

namespace geobus::lowlevel {

TEST(GeobusTimelefts, TestParse) {
  std::vector<types::Timelefts> expected = {types::Timelefts(
      helpers::time::CropTo<std::chrono::milliseconds>(
          std::chrono::system_clock::now()),
      helpers::time::CropTo<std::chrono::milliseconds>(
          std::chrono::system_clock::now()),
      types::TrackingType::kRouteTracking, types::DriverId("1_01234"),
      "route_id_1",
      ::geometry::Position(::geometry::Longitude(29), ::geometry::Latitude(29)),
      {types::TimeleftData(std::chrono::seconds(10),
                           types::Distance(500 * geometry::meter),
                           ::geometry::Position(::geometry::Longitude(30),
                                                ::geometry::Latitude(30)),
                           "order_id_1", "point_id_1", "service_id_1"),
       types::TimeleftData(std::chrono::seconds(200),
                           types::Distance(1000 * geometry::meter),
                           ::geometry::Position(::geometry::Longitude(30.0005),
                                                ::geometry::Latitude(30.0005)),
                           "order_id_2", "point_id_1", "service_id_2")},
      1)};

  const std::string& data = timeleft::SerializeMessage({expected});

  statistics::PayloadStatistics<timeleft::ParseInvalidStats> stats;
  auto actual = timeleft::ParseData(data, stats);

  test::DataTypeTestTraits<types::Timelefts>::TestElementsAreEqual(
      expected.begin(), expected.end(), actual.begin(), actual.end());
}

TEST(GeobusTimeleft, TestTimeleftWithUnknownDestination) {
  generators::TimeleftsGenerator generator;

  types::Timelefts correct = generator.CreateElement(5);
  correct.tracking_type = types::TrackingType::kUnknownDestination;
  correct.timeleft_data.resize(1);
  correct.timeleft_data.back().time_distance_left->time =
      std::chrono::seconds{0};
  correct.timeleft_data.back().time_distance_left->distance =
      geometry::Distance{0};
  correct.timeleft_data.back().service_id = "service_id";
  correct.timeleft_data.back().destination_position = geometry::Position{};
  EXPECT_TRUE(correct.IsValid());

  types::Timelefts incorrect1 = generator.CreateElement(6);
  incorrect1.tracking_type = types::TrackingType::kUnknownDestination;
  incorrect1.timeleft_data.resize(1);
  incorrect1.timeleft_data.back().time_distance_left->time =
      std::chrono::seconds{0};
  incorrect1.timeleft_data.back().time_distance_left->distance =
      geometry::Distance{0};
  incorrect1.timeleft_data.back().service_id = "";
  incorrect1.timeleft_data.back().destination_position = geometry::Position{};
  EXPECT_FALSE(incorrect1.IsValid());

  types::Timelefts incorrect2 = generator.CreateElement(7);
  incorrect2.tracking_type = types::TrackingType::kUnknownDestination;
  incorrect2.timeleft_data = std::vector<types::TimeleftData>{};
  EXPECT_FALSE(incorrect2.IsValid());
}

namespace timeleft {

INSTANTIATE_TYPED_TEST_SUITE_P(TimeleftsSerializationTest,
                               FlatbuffersSerializationTest, types::Timelefts);

}  // namespace timeleft
}  // namespace geobus::lowlevel
