#include <clients/yamaps/request_state/request_state_google.hpp>
#include <taxi_config/variables/GOOGLE_MAPS_TEXT_FORMATS.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace {
const std::string kGoogleResponseString = R"(
{
  "address_components": [
    {
      "long_name": "17-19",
      "short_name": "17-19",
      "types": [
        "street_number"
      ]
    },
    {
      "long_name": "Regency Street",
      "short_name": "Regency St",
      "types": [
        "route"
      ]
    },
    {
      "long_name": "London",
      "short_name": "London",
      "types": [
        "postal_town"
      ]
    },
    {
      "long_name": "Greater London",
      "short_name": "Greater London",
      "types": [
        "administrative_area_level_2",
        "political"
      ]
    },
    {
      "long_name": "England",
      "short_name": "England",
      "types": [
        "administrative_area_level_1",
        "political"
      ]
    },
    {
      "long_name": "United Kingdom",
      "short_name": "GB",
      "types": [
        "country",
        "political"
      ]
    },
    {
      "long_name": "SW1P 4BY",
      "short_name": "SW1P 4BY",
      "types": [
        "postal_code"
      ]
    }
  ],
  "formatted_address": "17-19 Regency St, London SW1P 4BY, UK",
  "geometry": {
    "location": {
      "lat": 51.4939939,
      "lng": -0.1322235
    },
    "location_type": "ROOFTOP",
    "viewport": {
      "northeast": {
        "lat": 51.4953428802915,
        "lng": -0.130874519708498
      },
      "southwest": {
        "lat": 51.4926449197085,
        "lng": -0.133572480291502
      }
    }
  },
  "place_id": "ChIJ565hgN0EdkgRMhOboIZ7uJ8",
  "plus_code": {
    "compound_code": "FVV9+H4 London, UK",
    "global_code": "9C3XFVV9+H4"
  },
  "types": [
    "cafe",
    "establishment",
    "food",
    "point_of_interest"
  ]
}
  )";
}

TEST(TestGmaps, TestGoogleGeoObjectParse) {
  const std::string json_string = "";
  auto json_resp = formats::json::FromString(kGoogleResponseString);
  namespace gmtf = taxi_config::google_maps_text_formats;
  gmtf::TextTypeFormat st_format;
  st_format.required_fields = {"street", "house", "postal_code"};
  st_format.format = "{street} {house}, {postal_code}";
  std::unordered_map<std::string, gmtf::CountryTextFormats> map_format;
  auto& gb_formats = map_format["GB"];
  gb_formats.short_text = {st_format};
  gmtf::VariableType gm_st_format(map_format);
  auto geo_object =
      clients::yamaps::ParseGoogleGeoObject(json_resp, gm_st_format);
  ASSERT_EQ(geo_object.short_text, "Regency St 17-19, SW1P 4BY");
  ASSERT_EQ(geo_object.description, "London, United Kingdom");
  ASSERT_EQ(geo_object.full_text, "17-19 Regency St, London SW1P 4BY, UK");
  ASSERT_EQ(geo_object.postal_code, "SW1P 4BY");
  ASSERT_EQ(geo_object.house, "17-19");
  ASSERT_EQ(geo_object.street, "Regency St");
  ASSERT_EQ(geo_object.city, "London");
  ASSERT_EQ(geo_object.country, "United Kingdom");
  ASSERT_EQ(geo_object.country_code, "GB");
  ASSERT_TRUE(::geometry::AreClosePositions(
      geo_object.point,
      ::geometry::Position::FromGeojsonArray({-0.1322235, 51.4939939})));
  ASSERT_TRUE(::geometry::AreClosePositions(
      geo_object.geometry_point,
      ::geometry::Position::FromGeojsonArray({-0.1322235, 51.4939939})));
}
