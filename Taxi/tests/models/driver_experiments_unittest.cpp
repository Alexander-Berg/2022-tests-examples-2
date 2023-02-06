#include <models/driver_experiments.hpp>

#include <gtest/gtest.h>

struct Driver {
  std::string driver_id;
  std::string park_id;
  std::string taximeter_version;

  Driver(const std::string& driver_id, const std::string& park_id,
         const std::string& taximeter_version)
      : driver_id(driver_id),
        park_id(park_id),
        taximeter_version(taximeter_version) {}
};

struct TestDriverData {
  mongo::BSONObj experiment;
  Driver driver;
  bool expected_result;
};

// clang-format off
std::vector<TestDriverData> driver_tests {
  {
    BSON(
      "name" << "experiment" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    true
  },
  {
    BSON(
      "name" << "experiment" <<
      "driver_id_last_digits" << BSON_ARRAY("3" << "45") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "2017",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "check_taximeter" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << " >= 8.45" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "2017",
      "8.46"
    ),
    true
  },
  {
    BSON(
      "name" << "check_taximeter" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << " ==7.11" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "7.11"
    ),
    true
  },
  {
    BSON(
      "name" << "check_taximeter" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << "<= 7.11" <<
      "active" << false
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "check_park" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1111",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "check_percent" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "percent" << 40.57 <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "check_percent" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "percent" << 40.58 <<
      "active" << true
    ),
    Driver( 
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    true
  },
  {
    BSON(
      "name" << "check_salt" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "percent" << 96.9 << 
      "salt" << "dade2565b4ec41e0a9a2ef08f16737a7" <<
      "active" << true
    ),
    Driver( 
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "check_salt" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "percent" << 97 <<
      "salt" << "dade2565b4ec41e0a9a2ef08f16737a7" << 
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    true
  },
  {
    BSON(
      "name" << "driver_id_percent_fail" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "salt" << "0a704431d84747f2b2e2b346a6c3cbfa" <<
      "active" << true <<
      "driver_id_percent" << BSON("from" << 50 << "to" << 100)
    ),
    Driver(
      "1234567890abcdefghijkl0987654337",
      "1488",
      "8.0"
    ),
    false
  },
  {
    BSON(
      "name" << "driver_id_percent_ok" <<
      "driver_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "parks" << BSON_ARRAY("2017" << "1488") <<
      "version" << ">=7.11" <<
      "salt" << "0a704431d84747f2b2e2b346a6c3cbfa" <<
      "active" << true <<
      "driver_id_percent" << BSON("from" << 0 << "to" << 50)
    ),
    Driver(
      "1234567890abcdefghijkl0987654337",
      "1488",
      "8.0"
    ),
    true
  },
  {
    BSON(
      "name" << "simple_test" <<
      "active" << true
    ),
    Driver(
      "1234567890abcdefghijkl0987654321",
      "1488",
      "8.0"
    ),
    true
  }
};
// clang-format on

class DriverExperiments : public ::testing::TestWithParam<TestDriverData> {};

TEST_P(DriverExperiments, Parametrized) {
  const auto& params = GetParam();
  experiments::DriverExperiment experiment(params.experiment);
  EXPECT_EQ(
      params.expected_result,
      experiment.Check(params.driver.driver_id, params.driver.park_id,
                       ParseTaximeterVersion(params.driver.taximeter_version)));
}

INSTANTIATE_TEST_CASE_P(ExperimentsTest, DriverExperiments,
                        ::testing::ValuesIn(driver_tests), );
