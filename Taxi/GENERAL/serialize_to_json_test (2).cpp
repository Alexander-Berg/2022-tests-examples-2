#include <geometry/position_as_object.hpp>
#include <gpssignal/gps_signal.hpp>
#include <gpssignal/serialization/gps_signal.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace gpssignal {

class JsonSerializationFixture : public ::gpssignal::test::GpsSignalTestPlugin,
                                 public ::testing::Test {};

template <typename T>
struct JsonTestCase {
  std::string json_string;
  T reference_object;
  bool should_parse_throw{false};
};

template <typename T>
void PrintTo(const JsonTestCase<T>& data, std::ostream* os) {
  *os << data.json_string;
}

/////////////////////////////////////////////////////////////////////////////
// GpsSignal
/////////////////////////////////////////////////////////////////////////////
using JsonGpsSignalTestCase = JsonTestCase<GpsSignal>;
using JsonSignalTestCase = JsonTestCase<GpsSignal>;

struct JsonSerializationGpsSignalCases
    : public ::gpssignal::test::GpsSignalTestPlugin,
      public ::testing::TestWithParam<JsonGpsSignalTestCase> {
  static std::vector<JsonGpsSignalTestCase> Data;
};

// clang-format off
std::vector<JsonGpsSignalTestCase> JsonSerializationGpsSignalCases::Data{{
  {R"json({"lon": 17.0, "lat": 19.0, "timestamp" : 0})json", GpsSignal{17 * lon, 19 * lat}, false},
  /// Current implementation of Parse for std::optional doesn't treat
  /// null as std::nullopt - instead it's an error.
  {R"json({"lon": 17.0, "lat": 19.0, "speed" : 1.0, "timestamp" : 20 })json",
    GpsSignal{17 * lon, 19 * lat, 
      Speed::from_value(1.0),
      std::nullopt, std::nullopt,
      std::chrono::system_clock::from_time_t(20) },
    false
  },
  {R"json({"acd": 17.0, "def": 19.0})json", GpsSignal{}, true},
  {"[17.0, 19.0, 20.0]", GpsSignal{}, true},
}};
// clang-format on

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializeGpsSignalCycle) {
  GpsSignal ref_pos = CreateGpsSignal(10);
  auto json_object = formats::json::ValueBuilder(ref_pos).ExtractValue();
  auto value_pos = json_object.As<GpsSignal>();
  TestGpsSignalsAreClose(ref_pos, value_pos);
}

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializeGpsPartialSignalCycle) {
  GpsSignal ref_pos = CreateGpsSignal(12);
  ref_pos.speed = std::nullopt;
  auto json_object = formats::json::ValueBuilder(ref_pos).ExtractValue();
  auto value_pos = json_object.As<GpsSignal>();
  TestGpsSignalsAreClose(ref_pos, value_pos);
}

/// Test that optional and absent are not in JSON
TEST_F(JsonSerializationFixture, SerializeAbsentMembers) {
  GpsSignal data{10 * geometry::lat, 10 * geometry::lon};
  auto json_object = formats::json::ValueBuilder(data).ExtractValue();
  EXPECT_TRUE(json_object[kSpeed].IsMissing());
  EXPECT_TRUE(json_object[kAccuracy].IsMissing());
  EXPECT_TRUE(json_object[kDirection].IsMissing());
}

TEST_P(JsonSerializationGpsSignalCases, Parse) {
  const auto& json = formats::json::FromString(GetParam().json_string);

  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(json.As<GpsSignal>());
  } else {
    GpsSignal value = json.As<GpsSignal>();
    TestGpsSignalsAreClose(GetParam().reference_object, value);
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonGpsSignal, JsonSerializationGpsSignalCases,
    ::testing::ValuesIn(JsonSerializationGpsSignalCases::Data));

}  // namespace gpssignal
