#include <cgeohash/cgeohash.hpp>
#include <sstream>
#include <testing/source_path.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/utest/utest.hpp>

namespace cgeohash_test {

struct TestCase {
  double lat, lon;
  std::string hash;
  std::vector<std::string> neighbors;
};

}  // namespace cgeohash_test

namespace formats::parse {

cgeohash_test::TestCase Parse(const formats::json::Value& value,
                              formats::parse::To<cgeohash_test::TestCase>) {
  cgeohash_test::TestCase result;
  result.lat = value["lat"].As<double>();
  result.lon = value["lon"].As<double>();
  result.hash = value["hash"].As<std::string>();
  result.neighbors = value["neighbors"].As<std::vector<std::string>>();
  return result;
}

}  // namespace formats::parse

namespace cgeohash_test {

TEST(TestGeohash, generated_hashes) {
  for (int precision = 11; precision <= 12; ++precision) {
    std::stringstream ss;
    ss << utils::CurrentSourcePath("src/cgeohash/tests/static")
       << "/hashes_precision_" << precision << ".json";
    std::vector<TestCase> test_cases =
        formats::json::blocking::FromFile(ss.str()).As<decltype(test_cases)>();
    ASSERT_TRUE(!test_cases.empty());
    for (auto& elem : test_cases) {
      std::string hash;
      cgeohash::encode(elem.lat, elem.lon, precision, hash);
      ASSERT_EQ(elem.hash, hash);
      auto decoded = cgeohash::decode_bbox(hash);
      ASSERT_TRUE(elem.lat <= decoded.maxlat);
      ASSERT_TRUE(elem.lat >= decoded.minlat);
      ASSERT_TRUE(elem.lon <= decoded.maxlon);
      ASSERT_TRUE(elem.lon >= decoded.minlon);

      auto decoded_fast = cgeohash::decode_bbox_fast(hash);
      ASSERT_TRUE(elem.lat <= decoded_fast.maxlat);
      ASSERT_TRUE(elem.lat >= decoded_fast.minlat);
      ASSERT_TRUE(elem.lon <= decoded_fast.maxlon);
      ASSERT_TRUE(elem.lon >= decoded_fast.minlon);
      auto neighbor_it = elem.neighbors.begin();
      for (int k = 0; k < 3; ++k) {
        for (int m = 0; m < 3; ++m) {
          ASSERT_EQ(*neighbor_it, cgeohash::neighbor(hash, k - 1, m - 1));
          ASSERT_EQ(*neighbor_it, cgeohash::neighbor_fast(hash, k - 1, m - 1));
          ++neighbor_it;
        }
      }
    }
  }
}

TEST(TestCGeohash, handmade_hashes) {
  int precision = 3;

  struct TestCase {
    double lon, lat;
    std::string hash, south_hash, north_hash, west_hash, east_hash;
  };

  TestCase test_1 = {23.203125, 55.546875, "u9b", "u98", "ud0", "u3z", "u9c"};
  TestCase test_2 = {156.796875, -4.921875, "rrp", "rqz", "rrr", "rrn", "rx0"};
  std::vector<TestCase> cases = {test_1, test_2};

  for (auto& test : cases) {
    std::string test_hash;
    cgeohash::encode(test.lat, test.lon, precision, test_hash);
    ASSERT_EQ(test.hash, test_hash);

    auto decoded = cgeohash::decode(test.hash);
    auto decoded_fast = cgeohash::decode_fast(test.hash);
    ASSERT_EQ(decoded.latitude, test.lat);
    ASSERT_EQ(decoded.longitude, test.lon);
    ASSERT_EQ(decoded_fast.latitude, test.lat);
    ASSERT_EQ(decoded_fast.longitude, test.lon);

    ASSERT_EQ(test.north_hash, cgeohash::neighbor(test.hash, 1, 0));
    ASSERT_EQ(test.south_hash, cgeohash::neighbor(test.hash, -1, 0));
    ASSERT_EQ(test.east_hash, cgeohash::neighbor(test.hash, 0, 1));
    ASSERT_EQ(test.west_hash, cgeohash::neighbor(test.hash, 0, -1));
    ASSERT_EQ(test.north_hash, cgeohash::neighbor_fast(test.hash, 1, 0));
    ASSERT_EQ(test.south_hash, cgeohash::neighbor_fast(test.hash, -1, 0));
    ASSERT_EQ(test.east_hash, cgeohash::neighbor_fast(test.hash, 0, 1));
    ASSERT_EQ(test.west_hash, cgeohash::neighbor_fast(test.hash, 0, -1));
  }
}

}  // namespace cgeohash_test
