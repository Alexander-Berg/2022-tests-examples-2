#include <clients/yamaps/request_state/request_state_google.hpp>
#include <clients/yamaps/request_state/request_state_mapbox.hpp>
#include <taxi_config/variables/GOOGLE_MAPS_TEXT_FORMATS.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace {
const std::string kMapboxResponseString_short = R"(
{"type":"FeatureCollection","query":[85.8628,74.2975],"features":[{"id":"region.11409709195006330","type":"Feature","place_type":["region"],"relevance":1,"properties":{"wikidata":"Q6563","short_code":"RU-KYA"},"text":"Krasnoyarsk Krai","place_name":"Krasnoyarsk Krai, Russia","bbox":[75.9839953082319,51.7730110009209,114.019082926266,81.280310499986],"center":[91.66667,59.88333],"geometry":{"type":"Point","coordinates":[91.66667,59.88333]},"context":[{"id":"country.299986422520","wikidata":"Q159","short_code":"ru","text":"Russia"}]},{"id":"country.299986422520","type":"Feature","place_type":["country"],"relevance":1,"properties":{"wikidata":"Q159","short_code":"ru"},"text":"Russia","place_name":"Russia","bbox":[19.5969411136635,41.1852530000125,179.9,81.8714744998741],"center":[96.6697054604756,61.9945734073292],"geometry":{"type":"Point","coordinates":[96.6697054604756,61.9945734073292]}}],"attribution":"NOTICE: © 2021 Mapbox and its suppliers. All rights reserved. Use of this data is subject to the Mapbox Terms of Service (https://www.mapbox.com/about/maps/). This response and the information it contains may not be retained. POI(s) provided by Foursquare."}
  )";

const std::string kMapboxResponseString_long = R"(
{"type":"FeatureCollection","query":[-87.921434,42.166602],"features":[{"id":"address.7372524404295074","type":"Feature","place_type":["address"],"relevance":1,"properties":{"accuracy":"point"},"text":"North Milwaukee Avenue","place_name":"804 North Milwaukee Avenue, Riverwoods, Illinois 60015, United States","center":[-87.922024,42.1665104],"geometry":{"type":"Point","coordinates":[-87.922024,42.1665104]},"address":"804","context":[{"id":"neighborhood.11275566002450510","text":"Lake Cook Road"},{"id":"postcode.13903677306297990","text":"60015"},{"id":"place.9932572081213780","text":"Riverwoods"},{"id":"district.15884047929545260","wikidata":"Q484263","text":"Lake County"},{"id":"region.10854263468358810","wikidata":"Q1204","short_code":"US-IL","text":"Illinois"},{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"neighborhood.11275566002450510","type":"Feature","place_type":["neighborhood"],"relevance":1,"properties":{},"text":"Lake Cook Road","place_name":"Lake Cook Road, Riverwoods, Illinois 60015, United States","bbox":[-87.947193646,42.135078011,-87.890555226,42.183581866],"center":[-87.9115,42.1504],"geometry":{"type":"Point","coordinates":[-87.9115,42.1504]},"context":[{"id":"postcode.13903677306297990","text":"60015"},{"id":"place.9932572081213780","text":"Riverwoods"},{"id":"district.15884047929545260","wikidata":"Q484263","text":"Lake County"},{"id":"region.10854263468358810","wikidata":"Q1204","short_code":"US-IL","text":"Illinois"},{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"postcode.13903677306297990","type":"Feature","place_type":["postcode"],"relevance":1,"properties":{},"text":"60015","place_name":"Riverwoods, Illinois 60015, United States","bbox":[-87.9410483382594,42.1447529977254,-87.8208911156442,42.203825900052],"center":[-87.88,42.2],"geometry":{"type":"Point","coordinates":[-87.88,42.2]},"context":[{"id":"place.9932572081213780","text":"Riverwoods"},{"id":"district.15884047929545260","wikidata":"Q484263","text":"Lake County"},{"id":"region.10854263468358810","wikidata":"Q1204","short_code":"US-IL","text":"Illinois"},{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"place.9932572081213780","type":"Feature","place_type":["place"],"relevance":1,"properties":{},"text":"Riverwoods","place_name":"Riverwoods, Illinois, United States","bbox":[-87.922873959,42.152946182,-87.874461001,42.192872716],"center":[-87.897,42.1675],"geometry":{"type":"Point","coordinates":[-87.897,42.1675]},"context":[{"id":"district.15884047929545260","wikidata":"Q484263","text":"Lake County"},{"id":"region.10854263468358810","wikidata":"Q1204","short_code":"US-IL","text":"Illinois"},{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"district.15884047929545260","type":"Feature","place_type":["district"],"relevance":1,"properties":{"wikidata":"Q484263"},"text":"Lake County","place_name":"Lake County, Illinois, United States","bbox":[-88.199763,42.152293,-87.759076,42.495637],"center":[-88.015061,42.323656],"geometry":{"type":"Point","coordinates":[-88.015061,42.323656]},"context":[{"id":"region.10854263468358810","wikidata":"Q1204","short_code":"US-IL","text":"Illinois"},{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"region.10854263468358810","type":"Feature","place_type":["region"],"relevance":1,"properties":{"wikidata":"Q1204","short_code":"US-IL"},"text":"Illinois","place_name":"Illinois, United States","bbox":[-91.5130799991365,36.9702970055306,-87.0117177165746,42.553081292589],"center":[-89.2749461071049,40.1492928594],"geometry":{"type":"Point","coordinates":[-89.2749461071049,40.1492928594]},"context":[{"id":"country.19678805456372290","wikidata":"Q30","short_code":"us","text":"United States"}]},{"id":"country.19678805456372290","type":"Feature","place_type":["country"],"relevance":1,"properties":{"wikidata":"Q30","short_code":"us"},"text":"United States","place_name":"United States","bbox":[-179.9,18.8163608007951,-66.8847646185949,71.4202919997506],"center":[-97.9222112121185,39.3812661305678],"geometry":{"type":"Point","coordinates":[-97.9222112121185,39.3812661305678]}}],"attribution":"NOTICE: © 2021 Mapbox and its suppliers. All rights reserved. Use of this data is subject to the Mapbox Terms of Service (https://www.mapbox.com/about/maps/). This response and the information it contains may not be retained. POI(s) provided by Foursquare."}
)";

}  // namespace

TEST(TestMapbox_short, TestMapboxGeoObjectParse_short) {
  const std::string json_string = "";
  auto json_resp = formats::json::FromString(kMapboxResponseString_short);
  namespace gmtf = taxi_config::google_maps_text_formats;
  gmtf::TextTypeFormat st_format;
  st_format.required_fields = {"street", "house", "postal_code"};
  st_format.format = "{street} {house}, {postal_code}";
  std::unordered_map<std::string, gmtf::CountryTextFormats> map_format;
  auto& gb_formats = map_format["RU"];
  gb_formats.short_text = {st_format};
  gmtf::VariableType gm_st_format(map_format);
  auto geo_object = clients::yamaps::ParseMapboxGeoObject(
      json_resp["features"][0], gm_st_format);
  ASSERT_EQ(geo_object.country, "Russia");
  ASSERT_EQ(geo_object.city, "Krasnoyarsk Krai");
  ASSERT_EQ(geo_object.country_code, "RU");
  ASSERT_TRUE(::geometry::AreClosePositions(
      geo_object.point,
      ::geometry::Position::FromGeojsonArray({91.6667, 59.8833})));
  ASSERT_EQ(geo_object.short_text, "");
  ASSERT_EQ(geo_object.full_text, "Krasnoyarsk Krai, Russia");
  ASSERT_EQ(geo_object.description, "Krasnoyarsk Krai, Russia");
  ASSERT_EQ(geo_object.postal_code.value_or(""), "");
  ASSERT_EQ(geo_object.street, "");
  ASSERT_EQ(geo_object.house, "");
}

TEST(TestMapbox_long, TestMapboxGeoObjectParse_long) {
  const std::string json_string = "";
  auto json_resp = formats::json::FromString(kMapboxResponseString_long);
  namespace gmtf = taxi_config::google_maps_text_formats;
  gmtf::TextTypeFormat st_format;
  st_format.required_fields = {"street", "house", "postal_code"};
  st_format.format = "{street} {house}, {postal_code}";
  std::unordered_map<std::string, gmtf::CountryTextFormats> map_format;
  auto& gb_formats = map_format["US"];
  gb_formats.short_text = {st_format};
  gmtf::VariableType gm_st_format(map_format);
  auto geo_object = clients::yamaps::ParseMapboxGeoObject(
      json_resp["features"][0], gm_st_format);
  ASSERT_EQ(geo_object.country, "United States");
  ASSERT_EQ(geo_object.city, "Riverwoods");
  ASSERT_EQ(geo_object.country_code, "US");
  ASSERT_TRUE(::geometry::AreClosePositions(
      geo_object.point,
      ::geometry::Position::FromGeojsonArray({-87.922, 42.1665})));
  ASSERT_EQ(geo_object.short_text, "North Milwaukee Avenue 804, 60015");
  ASSERT_EQ(
      geo_object.full_text,
      "804 North Milwaukee Avenue, Riverwoods, Illinois 60015, United States");
  ASSERT_EQ(geo_object.description, "Riverwoods, United States");
  ASSERT_EQ(geo_object.postal_code.value_or(""), "60015");
  ASSERT_EQ(geo_object.street, "North Milwaukee Avenue");
  ASSERT_EQ(geo_object.house, "804");
}
