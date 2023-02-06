#include <gtest/gtest.h>

#include <chrono>
#include <optional>
#include <string>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/datetime.hpp>

#include "api_base/utils.hpp"

// example: 1970-01-15T06:56:07.000
static const std::string kTimeFormat = api_over_db::utils::kTimeFormat;
static const std::string kExampleTimeFormat = "%Y-%m-%dT%H:%M:%E3S";

const std::string kExampleTimeString = "1970-01-15T06:56:07.000";
const auto kExampleTime = ::utils::datetime::Stringtime(
    kExampleTimeString, "UTC", kExampleTimeFormat);

const storages::postgres::io::detail::Point kExamplePoint{3.14, 3.14};
const storages::postgres::io::detail::Polygon kExamplePolygon{
    {{1, 0},
     {0.309017, 0.951057},
     {-0.809017, 0.587785},
     {-0.809017, -0.587785},
     {0.309017, -0.951057}}};

TEST(ApiOverDbUtils, ConvertTimeToJson) {
  auto formatted_time_string =
      ::utils::datetime::Timestring(kExampleTime, "UTC", kTimeFormat);
  auto time_json =
      api_over_db::utils::ConvertToJson(kExampleTime, {}).ExtractValue();
  ASSERT_TRUE(time_json.IsString());
  EXPECT_EQ(formatted_time_string, time_json.As<std::string>());
}

TEST(ApiOverDbUtils, ParseTimeFromJson) {
  auto time_ref = kExampleTime;

  auto time_json =
      api_over_db::utils::ConvertToJson(time_ref, {}).ExtractValue();
  std::chrono::system_clock::time_point time;
  api_over_db::utils::ParseJson(time, time_json);
  EXPECT_EQ(time_ref, time);
}

TEST(ApiOverDbUtils, ParseOptionalTimeFromJson) {
  auto time_ref = kExampleTime;
  auto time_json =
      api_over_db::utils::ConvertToJson(time_ref, {}).ExtractValue();
  std::optional<std::chrono::system_clock::time_point> time;
  api_over_db::utils::ParseJson(time, time_json);
  ASSERT_TRUE(bool(time));
  EXPECT_EQ(time_ref, *time);
}

TEST(ApiOverDbUtils, ParseOptionalNullTimeFromJson) {
  auto time_json = formats::json::ValueBuilder{}.ExtractValue();
  std::optional<std::chrono::system_clock::time_point> time;
  api_over_db::utils::ParseJson(time, time_json);
  EXPECT_FALSE(bool(time));

  auto missing_time_json =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  api_over_db::utils::ParseJson(time, time_json["missing_field"]);
  EXPECT_FALSE(bool(time));
}

TEST(ApiOverDbUtils, ParsePointFromJson) {
  auto point_ref = kExamplePoint;
  auto point_json =
      api_over_db::utils::ConvertToJson(point_ref, {}).ExtractValue();
  storages::postgres::io::detail::Point point;
  api_over_db::utils::ParseJson(point, point_json);
  EXPECT_EQ(point_ref, point);
}

TEST(ApiOverDbUtils, ParsePolygonFromJson) {
  auto polygon_ref = kExamplePolygon;
  auto polygon_json =
      api_over_db::utils::ConvertToJson(polygon_ref, {}).ExtractValue();
  storages::postgres::io::detail::Polygon polygon;
  api_over_db::utils::ParseJson(polygon, polygon_json);
  EXPECT_EQ(polygon_ref, polygon);
}

TEST(ApiOverDbUtils, SetNestedImplTest) {
  {
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    static constexpr auto fields = {"field"};
    api_over_db::utils::SetNestedImpl(builder, fields.begin(), fields.end(), 1);
    auto value = builder.ExtractValue();
    EXPECT_EQ(1, value["field"].As<int>());
  }

  {
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    static constexpr auto fields = {"field", "subfield", "subsubfield"};
    api_over_db::utils::SetNestedImpl(builder, fields.begin(), fields.end(), 1);
    auto value = builder.ExtractValue();
    EXPECT_EQ(1, value["field"]["subfield"]["subsubfield"].As<int>());
  }
}

TEST(ApiOverDbUtils, SetNestedTest) {
  {
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    static constexpr auto fields = {"field", "subfield", "subsubfield"};
    api_over_db::utils::SetNested(builder, fields, 1, {});
    auto value = builder.ExtractValue();
    EXPECT_EQ(1, value["field"]["subfield"]["subsubfield"].As<int>());
  }
  {
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    static constexpr auto fields = {"field", "subfield", "subsubfield"};
    auto field_value = std::make_optional<int>(1);
    api_over_db::utils::SetNested(builder, fields, field_value, {});
    auto value = builder.ExtractValue();
    EXPECT_EQ(1, value["field"]["subfield"]["subsubfield"].As<int>());
  }
  {
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    static constexpr auto fields = {"field", "subfield", "subsubfield"};
    auto field_value = std::optional<int>{};
    api_over_db::utils::SetNested(builder, fields, field_value, {});
    auto value = builder.ExtractValue();
    EXPECT_TRUE(value["field"]["subfield"]["subsubfield"].IsMissing());
  }
}
