#include <gtest/gtest.h>

#include "api-over-data/config/childseat_mapping.hpp"
#include "api-over-data/parser/models/car_requirements.hpp"
#include "api-over-data/parser/unpackers.hpp"

#include <models/tracker_requirements.hpp>

#include <mongo/bson/bsonmisc.h>
#include <mongo/mongo.hpp>

namespace {
::mongo::BSONObj MakeTestDocumentCars() {
  ::mongo::BSONObjBuilder builder;
  builder
      .append(
          "service",
          BSON("wifi" << false << "conditioner" << true << "wagon" << false
                      << "animals" << true << "smoking" << false << "delivery"
                      << false << "child_seat" << false << "vip_event" << false
                      << "woman_driver" << false << "pos" << false
                      << "print_bill" << false << "yandex_money" << false
                      << "bicycle" << false << "booster" << false << "ski"
                      << false << "extra_seats" << false << "lightbox" << false
                      << "sticker" << false << "charge" << false << "rug"
                      << false << "franchise" << false << "cargo_clean" << false
                      << "cargo_packing" << false << "rigging_equipment"
                      << false))
      .append("confirmed_boosters", 1)
      .append("booster_count", 1)
      .append("lightbox_confirmed", false)
      .append("sticker_confirmed", false)
      .append("rug_confirmed", false)
      .append("charge_confirmed", false)
      .append("cargo_loaders_amount", 0);
  return builder.obj();
}
::mongo::BSONObj MakeTestDocumentTaxi() {
  return ::mongo::BSONObjBuilder()
      .append("requirements",
              ::mongo::BSONObjBuilder()
                  .append("nosmoking", true)
                  .append("childchair_min", 6)
                  .append("childbooster_amount", 1)
                  .append("animaltransport", true)
                  .append("childchair_max", 12)
                  .append("childseats", BSON_ARRAY(BSON_ARRAY(7)))
                  .append("childseat_amount", 0)
                  .append("conditioner", true)
                  .append("infantseat_amount", 0)
                  .obj())
      .obj();
}

::mongo::BSONObj MakeTestDocumentConfig() {
  return ::mongo::BSONObjBuilder()
      .append(
          "v",
          ::mongo::BSONArrayBuilder()
              .append(BSON("categories" << BSON_ARRAY(1) << "groups"
                                        << BSON_ARRAY(1)))
              .append(BSON("categories" << BSON_ARRAY(3) << "groups"
                                        << BSON_ARRAY(2)))
              .append(BSON("categories" << BSON_ARRAY(7) << "groups"
                                        << BSON_ARRAY(3)))
              .append(BSON("categories" << BSON_ARRAY(1) << "groups"
                                        << BSON_ARRAY(0 << 1)))
              .append(BSON("categories" << BSON_ARRAY(1 << 3) << "groups"
                                        << BSON_ARRAY(0 << 1 << 2)))
              .append(BSON("categories" << BSON_ARRAY(1 << 3 << 7) << "groups"
                                        << BSON_ARRAY(0 << 1 << 2 << 3)))
              .append(BSON("categories" << BSON_ARRAY(1 << 3) << "groups"
                                        << BSON_ARRAY(1 << 2)))
              .append(BSON("categories" << BSON_ARRAY(1 << 3 << 7) << "groups"
                                        << BSON_ARRAY(1 << 2 << 3)))
              .append(BSON("categories" << BSON_ARRAY(3 << 7) << "groups"
                                        << BSON_ARRAY(2 << 3)))
              .append(BSON("categories" << BSON_ARRAY(3 << 7) << "groups"
                                        << BSON_ARRAY(0 << 2 << 3)))
              .append(BSON("categories" << BSON_ARRAY(3) << "groups"
                                        << BSON_ARRAY(0 << 2)))
              .append(BSON("categories" << BSON_ARRAY(7) << "groups"
                                        << BSON_ARRAY(0 << 3)))
              .append(BSON("categories" << ::mongo::BSONArrayBuilder().arr()
                                        << "groups" << BSON_ARRAY(0)))
              .append(BSON("categories" << ::mongo::BSONArrayBuilder().arr()
                                        << "groups" << BSON_ARRAY(1 << 3)))
              .append(BSON("categories" << ::mongo::BSONArrayBuilder().arr()
                                        << "groups" << BSON_ARRAY(0 << 1 << 3)))
              .arr())
      .obj();
}

::mongo::BSONObj MakeTestDocumentCars1() {
  ::mongo::BSONObjBuilder builder;
  builder
      .append("service", ::mongo::BSONObjBuilder()
                             .append("wifi", true)
                             .append("conditioner", true)
                             .append("wagon", false)
                             .append("animals", true)
                             .append("smoking", false)
                             .append("delivery", true)
                             .append("child_seat", false)
                             .append("vip_event", false)
                             .append("woman_driver", false)
                             .append("pos", true)
                             .append("print_bill", true)
                             .append("yandex_money", false)
                             .append("bicycle", false)
                             .append("booster", false)
                             .append("ski", true)
                             .append("extra_seats", false)
                             .append("lightbox", false)
                             .append("sticker", true)
                             .append("charge", false)
                             .append("rug", false)
                             .append("franchise", false)
                             .append("cargo_clean", true)
                             .append("cargo_packing", true)
                             .append("rigging_equipment", true)
                             .obj())
      .append("cert_verification", true)
      .append("booster_count", 1)
      .append("lightbox_confirmed", false)
      .append("sticker_confirmed", true)
      .append("rug_confirmed", false)
      .append("charge_confirmed", false)
      .append("cargo_loaders_amount", 0)
      .append("chairs", ::mongo::BSONArrayBuilder()
                            .append(BSON("brand"
                                         << "Яндекс"
                                         << "categories" << BSON_ARRAY(1 << 2)
                                         << "isofix" << true

                                         ))
                            .arr())
      .append("confirmed_boosters", 1)
      .append("confirmed_chairs",
              BSON_ARRAY(BSON("brand"
                              << "Яндекс"
                              << "categories" << BSON_ARRAY(1 << 2) << "isofix"
                              << true << "is_enabled" << true
                              << "confirmed_categories" << BSON_ARRAY(1 << 2)
                              << "inventory_number"
                              << "YT0426")));
  return builder.obj();
}

::mongo::BSONObj MakeTestDocumentTaxi1() {
  return ::mongo::BSONObjBuilder()
      .append("requirements",
              ::mongo::BSONObjBuilder()
                  .append("nosmoking", true)
                  .append("childchair_min", 0.9)
                  .append("stiker", true)
                  .append("childbooster_amount", 1)
                  .append("animaltransport", true)
                  .append("childchair_max", 12)
                  .append("childseats",
                          BSON_ARRAY(BSON_ARRAY(1 << 3) << BSON_ARRAY(7)))
                  .append("childseat_amount", 0)
                  .append("cargo_clean", true)
                  .append("cargo_packing", true)
                  .append("rigging_equipment", true)
                  .append("conditioner", true)
                  .append("ski", true)
                  .append("check", true)
                  .append("infantseat_amount", 1)
                  .obj())
      .obj();
}
}  // namespace

namespace models {
bool operator==(const ChildChairRequirement& left,
                const ChildChairRequirement& right) {
  return left.chairs == right.chairs;
}
}  // namespace models

TEST(DriverRequirements, ParseTest) {
  using namespace api_over_data;
  config::DocsMap docs_map;
  docs_map.Insert("CHILDSEAT_MAPPING", MakeTestDocumentConfig());
  config::ChildSeatMapping config(docs_map);
  {
    const auto car_requirements =
        OnUnpack<api_over_data::models::CarRequirements,
                 RowName::kCarRequirements>(MakeTestDocumentCars());
    const auto driver_requirements = ::models::ParseDriverRequirements(
        MakeTestDocumentTaxi()["requirements"].Obj());
    const auto new_driver_requirements =
        car_requirements.ToDriverRequirements("", config);
    EXPECT_EQ(new_driver_requirements.GetBoolRequirements(),
              driver_requirements.GetBoolRequirements());
    EXPECT_EQ(new_driver_requirements.GetIntRequirements(),
              driver_requirements.GetIntRequirements());
    EXPECT_EQ(new_driver_requirements.GetChildChairRequirement(),
              driver_requirements.GetChildChairRequirement());
  }
  {
    const auto car_requirements =
        OnUnpack<api_over_data::models::CarRequirements,
                 RowName::kCarRequirements>(MakeTestDocumentCars1());
    const auto driver_requirements = ::models::ParseDriverRequirements(
        MakeTestDocumentTaxi1()["requirements"].Obj());
    const auto new_driver_requirements =
        car_requirements.ToDriverRequirements("", config);
    EXPECT_EQ(new_driver_requirements.GetBoolRequirements(),
              driver_requirements.GetBoolRequirements());
    EXPECT_EQ(new_driver_requirements.GetIntRequirements(),
              driver_requirements.GetIntRequirements());
    EXPECT_EQ(new_driver_requirements.GetChildChairRequirement(),
              driver_requirements.GetChildChairRequirement());
  }
}
