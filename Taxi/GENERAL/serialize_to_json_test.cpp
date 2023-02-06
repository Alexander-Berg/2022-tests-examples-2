#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <geometry/position.hpp>
#include <geometry/position_as_array.hpp>
#include <geometry/position_as_object.hpp>
#include <geometry/serialization/bounding_box.hpp>
#include <geometry/serialization/cartesian_polygon.hpp>
#include <geometry/serialization/position.hpp>
#include <geometry/serialization/position_as_array.hpp>
#include <geometry/serialization/position_as_object.hpp>
#include <geometry/serialization/viewport.hpp>
#include <geometry/test/geometry_plugin_test.hpp>

namespace geometry {

class JsonSerializationFixture : public ::geometry::test::GeometryTestPlugin,
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
// Position
/////////////////////////////////////////////////////////////////////////////

using JsonPositionTestCase = JsonTestCase<Position>;

struct JsonSerializationPositionCases
    : public ::geometry::test::GeometryTestPlugin,
      public ::testing::TestWithParam<JsonPositionTestCase> {
  static std::vector<JsonPositionTestCase> Data;
};

// clang-format off
std::vector<JsonPositionTestCase> JsonSerializationPositionCases::Data{{
  // correct array representation
  {"[17.0, 19.0]", Position{17 * lon, 19 * lat}, false},
  // incorrect array representation
  {"[17.0, 19.0, 20.0]", Position{}, true},
  {"[17.0]", Position{}, true}, // no lat
  {"[17.0, null]", Position{}, true}, // nul as lat
  // correct string representations
  {R"json({"pos": "17.0,19.0"})json", Position{17 * lon, 19 * lat}, false},
  {R"json({"pos": "17.0 19.0"})json", Position{17 * lon, 19 * lat}, false},
  {R"json({"pos": "17.0,,19.0"})json", Position{17 * lon, 19 * lat}, false},
  {R"json({"pos": "17.0, , 19.0"})json", Position{17 * lon, 19 * lat}, false},
  // incorrect string representations
  {R"json({"pos": "17.0"})json", Position{}, true}, // only one token
  {R"json({"pos": ",17.0"})json", Position{}, true}, // no lon
  {R"json({"pos": " 17.0"})json", Position{}, true}, // no lon
  {R"json({"pos": ""})json", Position{}, true}, // empty string
  {R"json({"pos": " "})json", Position{}, true}, // no data
  {R"json({"pos": ", "})json", Position{}, true}, // no data
  {R"json({"pos": ",,"})json", Position{}, true}, // no data
  {R"json({"pos": "_,x,"})json", Position{}, true}, // garbage
  {R"json({"pos": "17.0,,19.0,"})json", Position{}, true}, // extra separator
  {R"json({"pos": "17.0,,19.0,,20.0"})json", Position{}, true}, // extra token
  // correct dict representations
  {R"json({"lon": 17.0, "lat": 19.0})json", Position{17 * lon, 19 * lat}, false},
  // incorrect dict representation
  {R"json({"acd": 17.0, "def": 19.0})json", Position{}, true},
  // nowhere-positions
  {R"json({"pos": null})json", Position::Nowhere(), false},
}};
// clang-format on

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializePositionCycle) {
  Position ref_pos = CreatePosition(10);
  auto json_object = formats::json::ValueBuilder(ref_pos).ExtractValue();
  auto value_pos = json_object.As<Position>();
  TestPositionsAreClose(ref_pos, value_pos);
}

TEST_F(JsonSerializationFixture, PositionStringView) {
  Position ref{17 * lon, 19 * lat};
  {  // space-separated
    std::string data{"17.0 19.0"};
    Position parsed = Parse(data, formats::parse::To<Position>{});
    TestPositionsAreClose(ref, parsed);
  }
  {  // comma-separated
    std::string data{"17.0,19.0"};
    Position parsed = Parse(data, formats::parse::To<Position>{});
    TestPositionsAreClose(ref, parsed);
  }
  {  // incorrect
    std::string data{"17.0,19.0,20.0"};
    EXPECT_ANY_THROW(Parse(data, formats::parse::To<Position>{}));
  }
}

TEST_F(JsonSerializationFixture, NowherePosition) {
  auto reference = Position::Nowhere();
  ASSERT_TRUE(!reference.IsFinite());

  auto json = formats::json::ValueBuilder(reference).ExtractValue();

  auto observation = json.As<Position>();

  EXPECT_TRUE(!observation.IsFinite());
}

TEST_P(JsonSerializationPositionCases, Parse) {
  auto json = formats::json::FromString(GetParam().json_string);

  if (json.IsObject() && json.HasMember("pos")) {
    json = json["pos"];
  }

  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(json.As<Position>());
  } else {
    Position value = json.As<Position>();
    TestPositionsAreClose(GetParam().reference_object, value);
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonPosition, JsonSerializationPositionCases,
    ::testing::ValuesIn(JsonSerializationPositionCases::Data));

/////////////////////////////////////////////////////////////////////////////
// PositionAsObject
/////////////////////////////////////////////////////////////////////////////

using JsonPositionAsObjectTestCase = JsonTestCase<PositionAsObject>;

struct JsonSerializationPositionAsObjectCases
    : public ::geometry::test::GeometryTestPlugin,
      public ::testing::TestWithParam<JsonPositionAsObjectTestCase> {
  static std::vector<JsonPositionAsObjectTestCase> Data;
};

// clang-format off
std::vector<JsonPositionAsObjectTestCase> JsonSerializationPositionAsObjectCases::Data{{
  {R"json({"lon": 17.0, "lat": 19.0})json", PositionAsObject{17 * lon, 19 * lat}, false},
  {R"json({"acd": 17.0, "def": 19.0})json", PositionAsObject{}, true}
}};
// clang-format on

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializePositionAsObjectCycle) {
  PositionAsObject ref_pos{CreatePosition(10)};
  auto json_object = formats::json::ValueBuilder(ref_pos).ExtractValue();
  auto value_pos = json_object.As<PositionAsObject>();
  TestPositionsAreClose(ref_pos.GetUnderlying(), value_pos.GetUnderlying());
}

TEST_P(JsonSerializationPositionAsObjectCases, Parse) {
  auto json = formats::json::FromString(GetParam().json_string);

  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(json.As<PositionAsObject>());
  } else {
    PositionAsObject value = json.As<PositionAsObject>();
    TestPositionsAreClose(GetParam().reference_object.GetUnderlying(),
                          value.GetUnderlying());
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonPositionAsObject, JsonSerializationPositionAsObjectCases,
    ::testing::ValuesIn(JsonSerializationPositionAsObjectCases::Data));

/////////////////////////////////////////////////////////////////////////////
// Viewport
/////////////////////////////////////////////////////////////////////////////
using JsonViewportTestCase = JsonTestCase<Viewport>;

struct JsonSerializationViewportCases
    : public ::geometry::test::GeometryTestPlugin,
      public ::testing::TestWithParam<JsonViewportTestCase> {
  static std::vector<JsonViewportTestCase> Data;
};

std::vector<JsonViewportTestCase> JsonSerializationViewportCases::Data{{
    {R"json({})json", Viewport{}, true},
    {R"json({"tl": [17.0, 19.0]})json",
     Viewport{Position{17 * lon, 19 * lat}, Position{}}, true},
    {R"json({"br": [17.0, 19.0], "tl": {"lan": 17.0, "lot": 19.0}})json",
     Viewport{Position{17 * lon, 19 * lat}, Position{17 * lon, 19 * lat}},
     true},
    {R"json({"br": [17.0, 19.0], "br": {"lat": 17.0, "lon": 19.0}})json",
     Viewport{Position{17 * lon, 19 * lat}, Position{19 * lon, 17 * lat}},
     true},
    {R"json({"tl": [17.0, 19.0], "br": {"lat": 17.0, "lon": 19.0}})json",
     Viewport{Position{17 * lon, 19 * lat}, Position{19 * lon, 17 * lat}},
     false},
    {R"json({"tl": [17.0, 19.0], "br": "17.0, 19.0"})json",
     Viewport{Position{17 * lon, 19 * lat}, Position{17 * lon, 19 * lat}},
     false},
}};

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializeViewportCycle) {
  Viewport ref_vp = CreateViewport(13, 42);
  auto json_object = formats::json::ValueBuilder(ref_vp).ExtractValue();
  auto value_vp = json_object.As<Viewport>();
  TestViewportsAreClose(ref_vp, value_vp);
}

TEST_P(JsonSerializationViewportCases, Parse) {
  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(
        formats::json::FromString(GetParam().json_string).As<Viewport>());
  } else {
    auto value =
        formats::json::FromString(GetParam().json_string).As<Viewport>();
    TestViewportsAreClose(GetParam().reference_object, value);
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonViewport, JsonSerializationViewportCases,
    ::testing::ValuesIn(JsonSerializationViewportCases::Data));

/////////////////////////////////////////////////////////////////////////////
// BoundingBox
/////////////////////////////////////////////////////////////////////////////
using JsonBoundingBoxTestCase = JsonTestCase<BoundingBox>;

struct JsonSerializationBoundingBoxCases
    : public ::geometry::test::GeometryTestPlugin,
      public ::testing::TestWithParam<JsonBoundingBoxTestCase> {
  static std::vector<JsonBoundingBoxTestCase> Data;
};

std::vector<JsonBoundingBoxTestCase> JsonSerializationBoundingBoxCases::Data{{
    {R"json([])json", BoundingBox{}, true},
    {R"json({})json", BoundingBox{}, true},
    {R"json([1, 2, 2])json", BoundingBox{}, true},
    {R"json([1, 2, "abc", 4])json", BoundingBox{}, true},
    {R"json([17.0, 19.0, 18.0, 20.0])json",
     BoundingBox{Position{17 * lon, 19 * lat}, Position{18 * lon, 20 * lat}},
     false},
    {R"json([17.0, 21.0, 18.0, 20.0])json",
     BoundingBox{Position{17 * lon, 20 * lat}, Position{18 * lon, 21 * lat}},
     false},
}};

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializeBoundingBoxCycle) {
  auto ref_vp = CreateBoundingBox(15, 100);
  auto json_object = formats::json::ValueBuilder(ref_vp).ExtractValue();
  auto value_vp = json_object.As<BoundingBox>();
  TestBoundingBoxesAreClose(ref_vp, value_vp);
}

TEST_P(JsonSerializationBoundingBoxCases, Parse) {
  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(
        formats::json::FromString(GetParam().json_string).As<BoundingBox>());
  } else {
    auto value =
        formats::json::FromString(GetParam().json_string).As<BoundingBox>();
    TestBoundingBoxesAreClose(GetParam().reference_object, value);
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonBoundingBox, JsonSerializationBoundingBoxCases,
    ::testing::ValuesIn(JsonSerializationBoundingBoxCases::Data));

/////////////////////////////////////////////////////////////////////////////
// CartesianPolygon
/////////////////////////////////////////////////////////////////////////////
using JsonCartesianPolygonTestCase = JsonTestCase<CartesianPolygon>;

struct JsonSerializationCartesianPolygonCases
    : public ::geometry::test::GeometryTestPlugin,
      public ::testing::TestWithParam<JsonCartesianPolygonTestCase> {
  static std::vector<JsonCartesianPolygonTestCase> Data;
};

std::vector<JsonCartesianPolygonTestCase>
    JsonSerializationCartesianPolygonCases::Data{{
        {R"json([])json", CartesianPolygon{}, false},
        {R"json({})json", CartesianPolygon{}, true},
        {R"json([1, 2, 3])json", CartesianPolygon{}, true},
        {R"json([1, 2])json", CreateCartesianPolygon({CartesianPosition{}}),
         true},
        {R"json([[1, 2]])json",
         CreateCartesianPolygon({CartesianPosition{1 * lon, 2 * lat}}), false},
        {R"json([[1, 2], {"lon": 3, "lat": 4}])json",
         CreateCartesianPolygon({CartesianPosition{1 * lon, 2 * lat},
                                 CartesianPosition{3 * lon, 4 * lat}}),
         false},
    }};

/// Test that Serialize + Deserialize produces same data
TEST_F(JsonSerializationFixture, SerializeCartesianPolygonCycle) {
  auto p = CreateCartesianPolygon({CartesianPosition{17 * lon, 19 * lat},
                                   CartesianPosition{18 * lon, 20 * lat},
                                   CartesianPosition{18 * lon, 19 * lat},
                                   CartesianPosition{17 * lon, 19 * lat}});
  auto json_object = formats::json::ValueBuilder(p).ExtractValue();
  auto value_vp = json_object.As<CartesianPolygon>();
  TestCartesianPolygonsAreClose(p, value_vp);
}

/// Test that Deserialization corrects polygon
TEST_F(JsonSerializationFixture, CorrectCartesianPolygon) {
  auto copy_correct = [](CartesianPolygon p) {
    boost::geometry::correct(p);
    return p;
  };

  auto not_circled =
      CreateCartesianPolygon({CartesianPosition{17 * lon, 19 * lat},
                              CartesianPosition{18 * lon, 20 * lat},
                              CartesianPosition{18 * lon, 19 * lat}});
  auto wrong_oriented =
      CreateCartesianPolygon({CartesianPosition{17 * lon, 19 * lat},
                              CartesianPosition{18 * lon, 19 * lat},
                              CartesianPosition{18 * lon, 20 * lat},
                              CartesianPosition{17 * lon, 19 * lat}});
  // copies are not the same as their origins
  auto corrected_circled = copy_correct(not_circled);
  ASSERT_NE(corrected_circled.outer().size(), not_circled.outer().size());
  auto corrected_oriented = copy_correct(wrong_oriented);
  TestPositionsAreClose(corrected_oriented.outer()[2],
                        wrong_oriented.outer()[1]);
  // copies are equal
  TestCartesianPolygonsAreClose(corrected_circled, corrected_oriented);

  // deserialized polygons have been corrected
  TestCartesianPolygonsAreClose(corrected_circled,
                                formats::json::ValueBuilder(not_circled)
                                    .ExtractValue()
                                    .As<CartesianPolygon>());
  TestCartesianPolygonsAreClose(corrected_oriented,
                                formats::json::ValueBuilder(wrong_oriented)
                                    .ExtractValue()
                                    .As<CartesianPolygon>());
}

TEST_P(JsonSerializationCartesianPolygonCases, Parse) {
  if (GetParam().should_parse_throw) {
    EXPECT_ANY_THROW(formats::json::FromString(GetParam().json_string)
                         .As<CartesianPolygon>());
  } else {
    auto value = formats::json::FromString(GetParam().json_string)
                     .As<CartesianPolygon>();
    TestCartesianPolygonsAreClose(GetParam().reference_object, value);
  }
}

INSTANTIATE_TEST_SUITE_P(
    JsonCartesianPolygon, JsonSerializationCartesianPolygonCases,
    ::testing::ValuesIn(JsonSerializationCartesianPolygonCases::Data));

}  // namespace geometry
