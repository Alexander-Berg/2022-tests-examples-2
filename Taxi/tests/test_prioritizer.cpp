#include <exception>
#include <fstream>
#include <functional>
#include <numeric>
#include <string>

#include <boost/filesystem.hpp>
#include <experiments3/priorities.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include "models/feature.hpp"
#include "utils/feature_compare/prioritizer.hpp"

namespace {

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(filename);
  if (!f.is_open()) {
    throw std::runtime_error("Couldn't open file");
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

const boost::filesystem::path kTestFilePath(__FILE__);
const std::string kTestDataDir =
    kTestFilePath.parent_path().string() + "/static";

using layers::utils::feature_compare::PriorityValue;

}  // namespace

TEST(TestPrioritizer, BadFeatureCounts) {
  auto cfg_value =
      Parse(LoadJsonFromFile(kTestDataDir + "/layers_priorities.json"),
            formats::parse::To<experiments3::layers_priorities::Value>{});

  const std::unordered_map<std::string, size_t> feature_counts_with_zero = {
      {"drive", 2},
      {"scooters", 2},
      {"masstransit", 1},
      {"userplaces", 0},
  };

  const std::unordered_map<std::string, size_t> feature_counts_all_zero = {
      {"drive", 0},
      {"scooters", 0},
      {"masstransit", 0},
      {"userplaces", 0},
  };

  try {
    layers::utils::feature_compare::Prioritizer p(
        cfg_value.extra.at("city").extra.at("discovery"),
        feature_counts_with_zero);
    // expecting exception
    ASSERT_TRUE(false);
  } catch (const std::runtime_error& err) {
    ASSERT_TRUE(true);
  }

  try {
    layers::utils::feature_compare::Prioritizer p(
        cfg_value.extra.at("city").extra.at("discovery"),
        feature_counts_all_zero);
    // expecting exception
    ASSERT_TRUE(false);
  } catch (const std::runtime_error& err) {
    ASSERT_TRUE(true);
  }
}

TEST(TestPrioritizer, General) {
  auto cfg_value =
      Parse(LoadJsonFromFile(kTestDataDir + "/layers_priorities.json"),
            formats::parse::To<experiments3::layers_priorities::Value>{});

  layers::models::PointFeature f1;
  f1.provider = "drive";
  f1.subtype = layers::models::SubType::kObject;
  f1.id = "drive_car_1";

  layers::models::PointFeature f2;
  f2.provider = "drive";
  f2.subtype = layers::models::SubType::kCluster;
  f2.id = "drive_cluster_1";

  layers::models::PointFeature f3;
  f3.provider = "scooters";
  f3.subtype = layers::models::SubType::kObject;
  f3.id = "scooter_1";

  layers::models::PointFeature f4;
  f4.provider = "scooters";
  f4.subtype = layers::models::SubType::kCluster;
  f4.id = "scooter_cluster_1";
  f4.prioritizer_meta_["yolo"] = 42;

  layers::models::PointFeature f5;
  f5.provider = "masstransit";
  f5.subtype = layers::models::SubType::kObject;
  f5.id = "stop_1";

  layers::models::PointFeature f6;
  f6.provider = "userplaces";
  f6.subtype = layers::models::SubType::kObject;
  f6.id = "home";

  const std::unordered_map<std::string, size_t> feature_counts = {
      {"drive", 2},
      {"scooters", 2},
      {"masstransit", 1},
      {"userplaces", 1},
  };
  layers::utils::feature_compare::Prioritizer p(
      cfg_value.extra.at("city").extra.at("discovery"), feature_counts);
  const std::unordered_map<std::string, size_t> multipliers = {
      {"drive", 9},
      {"scooters", 6},
      {"masstransit", 30},
      {"userplaces", 12},
  };
  auto priority = [&multipliers](const auto& f) {
    return multipliers.at(f.provider) * (std::hash<std::string>{}(f.id) % 1000);
  };

  // userplaces provider has the highest priority
  ASSERT_TRUE(p.IsFirstGreater(f6, f1));
  ASSERT_TRUE(p.IsFirstGreater(f6, f2));
  ASSERT_TRUE(p.IsFirstGreater(f6, f3));
  ASSERT_TRUE(p.IsFirstGreater(f6, f4));
  ASSERT_TRUE(p.IsFirstGreater(f6, f5));
  // drive cluster has higher priority than drive object
  ASSERT_TRUE(p.IsFirstGreater(f2, f1));
  // drive cluster has higher priority than scooters object
  ASSERT_TRUE(p.IsFirstGreater(f2, f3));
  // drive cluster has higher priority than masstransit object
  ASSERT_TRUE(p.IsFirstGreater(f2, f5));
  // scooters cluster has higher priority than masstransit object
  ASSERT_TRUE(p.IsFirstGreater(f4, f5));
  // scooters cluster has higher priority than scooters object
  ASSERT_TRUE(p.IsFirstGreater(f4, f3));
  // scooters cluster has higher priority than drive object
  ASSERT_TRUE(p.IsFirstGreater(f4, f1));

  // check with hash
  // drive object vs scooters object
  ASSERT_EQ(p.IsFirstGreater(f1, f3), priority(f1) > priority(f3));
  // drive object vs masstransit object
  ASSERT_EQ(p.IsFirstGreater(f1, f5), priority(f1) > priority(f5));
  // scooters object vs masstransit object
  ASSERT_EQ(p.IsFirstGreater(f3, f5), priority(f3) > priority(f5));
  // scooters cluster vs drive cluster
  ASSERT_EQ(p.IsFirstGreater(f4, f2), priority(f4) > priority(f2));

  EXPECT_EQ(p.GetFullTuple(f1).at(2), 322);
  EXPECT_EQ(p.GetFullTuple(f4).at(2), 42);
}
