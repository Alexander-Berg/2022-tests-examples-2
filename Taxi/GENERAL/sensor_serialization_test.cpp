#include <vector>

#include <gtest/gtest.h>

#include <fts-universal-signal/sensor.hpp>
#include <fts-universal-signal/serialization/sensor.hpp>

using namespace fts_universal_signal;

namespace {

std::string Convert(const std::vector<unsigned char>& data) {
  return std::string(data.begin(), data.end());
}

std::vector<unsigned char> Convert(const std::string& data) {
  return std::vector<unsigned char>(data.begin(), data.end());
}

}  // namespace

TEST(JsonSerializationSensor, SerializeDeserialize) {
  Sensor sensor{"key", Convert("data")};
  auto json_object = formats::json::ValueBuilder(sensor).ExtractValue();
  auto result_sensor = json_object.As<Sensor>();
  ASSERT_EQ(sensor.key, result_sensor.key);
  ASSERT_EQ(sensor.data, result_sensor.data);
}

TEST(JsonSerializationSensor, SerializeToBase64) {
  Sensor sensor{"key", Convert("data")};
  auto json_object = formats::json::ValueBuilder(sensor).ExtractValue();
  ASSERT_EQ(json_object["data"].As<std::string>(), "ZGF0YQ==");
}

TEST(JsonSerializationSensor, DeserializeFromBase64) {
  auto json_object = formats::json::ValueBuilder();
  json_object["key"] = "key";
  json_object["data"] = "ZGF0YQ==";
  auto value = json_object.ExtractValue();
  auto sensor = value.As<Sensor>();
  ASSERT_EQ(Convert(sensor.data), "data");
}
