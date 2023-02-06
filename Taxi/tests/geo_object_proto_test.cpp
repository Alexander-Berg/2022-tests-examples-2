#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include "clients/yamaps/parse_proto.hpp"
#include "proto_address_example.hpp"
#include "proto_org_example.hpp"

#include <taxi_config/variables/YANDEX_MAPS_TEXT_FORMATS.hpp>
#include "taxi_config/yamaps/taxi_config.hpp"

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>

namespace {

using namespace geometry::literals;

const double kEpsilon = 0.000001;

bool PosEqLonLat(const geometry::Position& pos, double lon, double lat) {
  return fabs(pos.GetLatitudeAsDouble() - lat) < kEpsilon &&
         fabs(pos.GetLongitudeAsDouble() - lon) < kEpsilon;
}

}  // namespace

TEST(TestYamaps, TestGeoObjectProtoAddress) {
  std::string proto_str(reinterpret_cast<char*>(kExampleAddress),
                        sizeof(kExampleAddress));
  auto geo_objs = clients::yamaps::ExtractGeoObjectsFromProto(
      proto_str, dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(geo_objs.size(), 1);
  auto& geo_obj = geo_objs[0];
  EXPECT_EQ(geo_obj.description, "mikrorayon Moskovka, Omsk, Russia");
  EXPECT_EQ(geo_obj.oid, "1711089298");
  EXPECT_EQ(geo_obj.kind, clients::yamaps::Kind::kEntrance);
  EXPECT_EQ(geo_obj.precision, clients::yamaps::Precision::kExact);
  EXPECT_EQ(geo_obj.house, "30");
  EXPECT_EQ(geo_obj.city, "Omsk");
  EXPECT_EQ(geo_obj.area, "gorodskoy okrug Omsk");
  EXPECT_EQ(geo_obj.district, "mikrorayon Moskovka");
  EXPECT_EQ(geo_obj.country, "Russia");

  EXPECT_TRUE(PosEqLonLat(geo_obj.point, 73.472336, 54.921681));
  EXPECT_TRUE(PosEqLonLat(geo_obj.geometry_point, 73.472336, 54.921681));
  EXPECT_EQ(geo_obj.street, "Batumskaya ulitsa");
  EXPECT_EQ(
      geo_obj.full_text,
      "Russia, Omsk, mikrorayon Moskovka, Batumskaya ulitsa, 30, entrance 3");
  EXPECT_EQ(geo_obj.short_text, "Batumskaya ulitsa, 30, entrance 3");
  EXPECT_EQ(geo_obj.exact, true);
  ASSERT_EQ(geo_obj.arrival_points.size(), 3);
  EXPECT_EQ(geo_obj.arrival_points[0].name.value_or("(none)"), "1");

  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[0].point, 73.472461, 54.921267));
  EXPECT_EQ(geo_obj.arrival_points[1].name.value_or("(none)"), "2");
  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[1].point, 73.472399, 54.92147437));
  EXPECT_EQ(geo_obj.arrival_points[2].name.value_or("(none)"), "3");
  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[2].point, 73.472336, 54.92168137));
  EXPECT_EQ(geo_obj.entrance.value_or("(none)"), "3");
  EXPECT_EQ(
      geo_obj.uri.value_or("(none)"),
      "ymapsbm1://"
      "geo?ll=73.472%2C54.921&spn=0.001%2C0.001&text=%D0%A0%D0%BE%D1%81%D1%81%"
      "D0%B8%D1%8F%2C%20%D0%9E%D0%BC%D1%81%D0%BA%2C%20%D0%BC%D0%B8%D0%BA%D1%80%"
      "D0%BE%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%20%D0%9C%D0%BE%D1%81%D0%BA%D0%BE%D0%"
      "B2%D0%BA%D0%B0%2C%20%D0%91%D0%B0%D1%82%D1%83%D0%BC%D1%81%D0%BA%D0%B0%D1%"
      "8F%20%D1%83%D0%BB%D0%B8%D1%86%D0%B0%2C%2030%2C%20%D0%BF%D0%BE%D0%B4%D1%"
      "8A%D0%B5%D0%B7%D0%B4%203%20%7B1711089298%7D");
  EXPECT_EQ(geo_obj.object_type, "другое");
  EXPECT_EQ(geo_obj.type, clients::yamaps::Type::kAddr);
}

TEST(TestYamaps, TestGeoObjectProtoOrg) {
  std::string proto_org_str(reinterpret_cast<char*>(kOrgExample),
                            sizeof(kOrgExample));
  const auto geo_objs = clients::yamaps::ExtractGeoObjectsFromProto(
      proto_org_str, dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(geo_objs.size(), 1);
  const auto& geo_org_obj = geo_objs[0];
  EXPECT_EQ(geo_org_obj.description, "Зубовский бул., 11А");
  EXPECT_EQ(geo_org_obj.oid, "1151417069");
  EXPECT_EQ(geo_org_obj.kind, clients::yamaps::Kind::kHouse);
  EXPECT_EQ(geo_org_obj.precision, clients::yamaps::Precision::kExact);
  EXPECT_EQ(geo_org_obj.house, "11А");
  EXPECT_EQ(geo_org_obj.street, "Зубовский бульвар");
  EXPECT_EQ(geo_org_obj.city, "Москва");
  EXPECT_EQ(geo_org_obj.country, "Россия");
  EXPECT_TRUE(PosEqLonLat(geo_org_obj.point, 37.592758, 55.735493));
  EXPECT_EQ(geo_org_obj.full_text,
            "Россия, Москва, Зубовский бульвар, 11А, Хлеб Насущный");
  EXPECT_EQ(geo_org_obj.short_text, "Хлеб Насущный");
  EXPECT_EQ(geo_org_obj.exact, true);
  EXPECT_EQ(geo_org_obj.arrival_points.size(), 1);
  EXPECT_FALSE(geo_org_obj.entrance);
  EXPECT_EQ(geo_org_obj.uri.value_or("(none)"),
            "ymapsbm1://org?oid=1151417069");
  EXPECT_EQ(geo_org_obj.object_type, "организация");
  ASSERT_EQ(geo_org_obj.rubrics.size(), 2);
  EXPECT_EQ(geo_org_obj.rubrics[0].category_class, "cafe");
  EXPECT_EQ(geo_org_obj.rubrics[0].category_id, "184106390");
  EXPECT_EQ(geo_org_obj.rubrics[1].category_class, "confectionary");
  EXPECT_EQ(geo_org_obj.rubrics[1].category_id, "184106798");
  EXPECT_EQ(geo_org_obj.type, clients::yamaps::Type::kOrg);
  ASSERT_EQ(geo_org_obj.phones.size(), 1);
  EXPECT_EQ(geo_org_obj.phones[0].formatted, "+7 (495) 419-20-25");
  EXPECT_EQ(geo_org_obj.phones[0].type, clients::yamaps::Phone::kPhone);
  EXPECT_EQ(geo_org_obj.phones[0].details.country, "7");
  EXPECT_EQ(geo_org_obj.phones[0].details.prefix, "495");
  EXPECT_EQ(geo_org_obj.phones[0].details.number, "4192025");
  EXPECT_EQ(geo_org_obj.open_hours->text,
            "пн-пт 07:00–22:00; сб,вс 09:00–22:00");
  EXPECT_EQ(geo_org_obj.open_hours->state.text, "Открыто до 22:00");
  EXPECT_EQ(geo_org_obj.open_hours->state.short_text, "До 22:00");
  EXPECT_EQ(geo_org_obj.distance->text, "5,5 км");
  EXPECT_EQ(geo_org_obj.distance->value, 5500);
  ASSERT_EQ(geo_org_obj.photos.size(), 11);
  EXPECT_EQ(geo_org_obj.photos[0].url_template,
            "https://avatars.mds.yandex.net/get-altay/2761244/"
            "2a00000171d91419f8915efd2a3c4bf3dd04/%s");
  ASSERT_EQ(geo_org_obj.references.size(), 3);
  ASSERT_EQ(geo_org_obj.references[0].id, "1541938774");
  ASSERT_EQ(geo_org_obj.references[0].scope, "nyak");
  ASSERT_EQ(geo_org_obj.references[1].id, "894");
  ASSERT_EQ(geo_org_obj.references[1].scope, "yandex-eda");
  ASSERT_EQ(geo_org_obj.references[2].id, "5731decd9c183f0cfd8f7d09");
  ASSERT_EQ(geo_org_obj.references[2].scope, "afisha");
  ASSERT_TRUE(geo_org_obj.qr_payment);
  EXPECT_EQ(geo_org_obj.qr_payment->qr_id, "hleb_nasushny_005");
}

TEST(TestYamaps, TestFullResponse) {
  std::string proto_str(reinterpret_cast<char*>(kExampleAddress),
                        sizeof(kExampleAddress));
  const auto parsed = clients::yamaps::ExtractFullResponseFromProto(
      proto_str, dynamic_config::GetDefaultSnapshot());
  ASSERT_TRUE(parsed);
  EXPECT_EQ(parsed->geoobjects.size(), 1);
  EXPECT_EQ(parsed->reqid.value_or("(none)"),
            "1571441446295744-1298912709-man2-5852");
  ASSERT_TRUE(parsed->bounded_by);
  EXPECT_TRUE(AreCloseBoundingBoxes(*parsed->bounded_by,
                                    geometry::BoundingBox{
                                        {73.471312_lon, 54.921091_lat},
                                        {73.47336_lon, 54.92227_lat},
                                    }));
}

TEST(TestYamaps, TestStripComponentFromText) {
  using clients::yamaps::StripComponentFromText;
  ASSERT_EQ(StripComponentFromText("ab,cd,ef", "cd"), "ab,ef");
  ASSERT_EQ(StripComponentFromText("ab, cd, ef", "cd"), "ab, ef");
  ASSERT_EQ(StripComponentFromText("ab , cd , ef", "cd"), "ab  , ef");
  ASSERT_EQ(StripComponentFromText("ab,cd,ef", "ef"), "ab,cd");
  ASSERT_EQ(StripComponentFromText("ab,cd,ef,ef", "ef"), "ab,cd,ef");
  ASSERT_EQ(StripComponentFromText("ab,ef,cd, ef", "ef"), "ab,ef,cd");
  ASSERT_EQ(StripComponentFromText("ab,ef,cd,ef", "ab"), "ef,cd,ef");
  ASSERT_EQ(StripComponentFromText("ab , ef,cd,ef", "ab"), "ef,cd,ef");
  ASSERT_EQ(StripComponentFromText("ab,ef,cd,ab,ef", "ab"), "ab,ef,cd,ef");
  ASSERT_EQ(StripComponentFromText("a, b, c, d", "gh"), "a, b, c, d");
  ASSERT_EQ(StripComponentFromText("a, b, c, d", ""), "a, b, c, d");
  ASSERT_EQ(StripComponentFromText("", ""), "");
  ASSERT_EQ(StripComponentFromText("", "abcd"), "");
  ASSERT_EQ(StripComponentFromText("ab, cd, ef, ef gh", "ef"), "ab, cd, ef gh");
  ASSERT_EQ(StripComponentFromText("ab, cd, ef gh, ef", "ef"), "ab, cd, ef gh");
  ASSERT_EQ(StripComponentFromText("ef, ab, cd, ef gh", "ef"), "ab, cd, ef gh");
  ASSERT_EQ(StripComponentFromText("abc, ef, gh, abc", "ef, gh"), "abc, abc");
  ASSERT_EQ(StripComponentFromText("abc,ef, gh,abc", "ef, gh"), "abc,abc");
  ASSERT_EQ(StripComponentFromText("a, ef, gh a", "ef, gh"), "a, ef, gh a");
  ASSERT_EQ(StripComponentFromText("a ef, gh, a", "ef, gh"), "a ef, gh, a");
  ASSERT_EQ(StripComponentFromText("ef, gh, ef, gh,", "ef, gh"), "ef, gh,");
  ASSERT_EQ(StripComponentFromText("ef, gh, ef, gh,", "ef, gh"), "ef, gh,");
}

TEST(TestYamaps, TestGeoObjectProtoAddressFormatted) {
  std::string proto_str(reinterpret_cast<char*>(kExampleAddress),
                        sizeof(kExampleAddress));
  namespace ymtf = taxi_config::yandex_maps_text_formats;
  ymtf::CountryTextFormats formats;
  formats.short_text = {
      ymtf::TextTypeFormat{{"STREET", "HOUSE"}, "{HOUSE} {STREET}"}};
  const auto keyvalue = dynamic_config::KeyValue(
      taxi_config::YANDEX_MAPS_TEXT_FORMATS,
      ymtf::YandexMapsTextFormats{
          true, dynamic_config::ValueDict<ymtf::CountryTextFormats>(
                    {{"__default__", formats}})});
  const auto storage = dynamic_config::MakeDefaultStorage({keyvalue});
  auto geo_objs = clients::yamaps::ExtractGeoObjectsFromProto(
      proto_str, storage.GetSnapshot());
  ASSERT_EQ(geo_objs.size(), 1);
  auto& geo_obj = geo_objs[0];
  EXPECT_EQ(geo_obj.description, "mikrorayon Moskovka, Omsk, Russia");
  EXPECT_EQ(geo_obj.oid, "1711089298");
  EXPECT_EQ(geo_obj.kind, clients::yamaps::Kind::kEntrance);
  EXPECT_EQ(geo_obj.precision, clients::yamaps::Precision::kExact);
  EXPECT_EQ(geo_obj.house, "30");
  EXPECT_EQ(geo_obj.city, "Omsk");
  EXPECT_EQ(geo_obj.country, "Russia");

  EXPECT_TRUE(PosEqLonLat(geo_obj.point, 73.472336, 54.921681));
  EXPECT_TRUE(PosEqLonLat(geo_obj.geometry_point, 73.472336, 54.921681));
  EXPECT_EQ(geo_obj.street, "Batumskaya ulitsa");
  EXPECT_EQ(
      geo_obj.full_text,
      "Russia, Omsk, mikrorayon Moskovka, Batumskaya ulitsa, 30, entrance 3");
  EXPECT_EQ(geo_obj.short_text, "30 Batumskaya ulitsa");
  EXPECT_EQ(geo_obj.exact, true);
  ASSERT_EQ(geo_obj.arrival_points.size(), 3);
  EXPECT_EQ(geo_obj.arrival_points[0].name.value_or("(none)"), "1");

  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[0].point, 73.472461, 54.921267));
  EXPECT_EQ(geo_obj.arrival_points[1].name.value_or("(none)"), "2");
  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[1].point, 73.472399, 54.92147437));
  EXPECT_EQ(geo_obj.arrival_points[2].name.value_or("(none)"), "3");
  EXPECT_TRUE(
      PosEqLonLat(geo_obj.arrival_points[2].point, 73.472336, 54.92168137));
  EXPECT_EQ(geo_obj.entrance.value_or("(none)"), "3");
  EXPECT_EQ(
      geo_obj.uri.value_or("(none)"),
      "ymapsbm1://"
      "geo?ll=73.472%2C54.921&spn=0.001%2C0.001&text=%D0%A0%D0%BE%D1%81%D1%81%"
      "D0%B8%D1%8F%2C%20%D0%9E%D0%BC%D1%81%D0%BA%2C%20%D0%BC%D0%B8%D0%BA%D1%80%"
      "D0%BE%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%20%D0%9C%D0%BE%D1%81%D0%BA%D0%BE%D0%"
      "B2%D0%BA%D0%B0%2C%20%D0%91%D0%B0%D1%82%D1%83%D0%BC%D1%81%D0%BA%D0%B0%D1%"
      "8F%20%D1%83%D0%BB%D0%B8%D1%86%D0%B0%2C%2030%2C%20%D0%BF%D0%BE%D0%B4%D1%"
      "8A%D0%B5%D0%B7%D0%B4%203%20%7B1711089298%7D");
  EXPECT_EQ(geo_obj.object_type, "другое");
  EXPECT_EQ(geo_obj.type, clients::yamaps::Type::kAddr);
}
