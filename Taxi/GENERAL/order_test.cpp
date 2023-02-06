#include <gtest/gtest.h>
#include <pugixml/pugixml.hpp>

#include <models/providers.hpp>
#include <utils/helpers/json.hpp>

#include "request_confirm.hpp"
#include "setcar.hpp"
#include "statuses.hpp"

TEST(ModelsOrderSetCar, ToDriverDto) {
  using models::order::Statuses;
  using models::order::request_confirm::DbS2S;
  using models::order::request_confirm::S2DbS;
  using models::order::request_confirm::Status;
  using models::order::set_car::ToDriverDto;
  using utils::helpers::CreateJsonArray;
  using utils::helpers::CreateJsonObject;

  // prepare
  const Json::Value& addres_obj =
      CreateJsonObject({{"ArrivalDistance", 0.0},
                        {"Street", "улица Суворова"},
                        {"House", "145А"},
                        {"Region", ""},
                        {"Lat", 53.201671},
                        {"Lon", 44.997592}});
  const std::string& expected_street =
      addres_obj["Street"].asString() + ", " + addres_obj["House"].asString();

  const auto composite_price = CreateJsonObject({{"boarding", 1},
                                                 {"distance", 2},
                                                 {"time", 3},
                                                 {"waiting", 4},
                                                 {"requirements", 5},
                                                 {"transit_waiting", 6},
                                                 {"destination_waiting", 7}});

  Json::Value orig_json;
  orig_json["address_from"] = addres_obj;
  orig_json["address_to"] = addres_obj;
  orig_json["route_points"] = CreateJsonArray({addres_obj, addres_obj});
  orig_json["show_address"] = true;
  orig_json["fixed_price"] = CreateJsonObject({{"show", false}});
  orig_json["base_price"] = CreateJsonObject(
      {{"user", composite_price}, {"driver", composite_price}});
  orig_json["driver_fixed_price"] = CreateJsonObject({{"show", false}});
  orig_json["provider"] = models::providers::Yandex;
  orig_json["subvention"] =
      CreateJsonObject({{"disabled_rules", CreateJsonArray({})}});
  orig_json["pool"] = CreateJsonObject(
      {{"orders",
        CreateJsonObject({
            {"order2_0",
             CreateJsonObject(
                 {{"fixed_price",
                   CreateJsonObject({{"show", true}, {"price", 100}})}})},
            {"order2_1",
             CreateJsonObject(
                 {{"fixed_price",
                   CreateJsonObject({{"show", false}, {"price", 100}})}})},
            {"order2_2", CreateJsonObject({})},
        })}});

  orig_json["type_name"] = "Яндекс.Корпоративный";
  orig_json["client_geo_sharing"] = CreateJsonObject({{"track_id", "uuid"}});

  Statuses statuses;
  statuses.status = Status::Transporting;
  statuses.embedded_statuses = {{"order2_0", Status::Driving},
                                {"order2_1", Status::Waiting},
                                {"order2_2", Status::Transporting}};

  std::set<std::string> feature_support{"json_geoareas", "gzip_push",
                                        "subvention", "pool"};

  l10n::MainTranslations translations{{}};

  // process
  const Json::Value& res_json =
      ToDriverDto(std::move(orig_json), statuses, true, translations, "en",
                  std::nullopt, {});

  // checks
  ASSERT_TRUE(res_json.isObject());

  EXPECT_TRUE(res_json["address_from"]["House"].isNull());
  EXPECT_STREQ(expected_street.c_str(),
               res_json["address_from"]["Street"].asCString());

  EXPECT_TRUE(res_json["address_to"]["House"].isNull());
  EXPECT_STREQ(expected_street.c_str(),
               res_json["address_to"]["Street"].asCString());

  for (const auto& addr : res_json["route_points"]) {
    EXPECT_TRUE(addr["House"].isNull());
    EXPECT_STREQ(expected_street.c_str(), addr["Street"].asCString());
  }

  EXPECT_FALSE(res_json.isMember("fixed_price"));
  EXPECT_FALSE(res_json.isMember("driver_fixed_price"));
  EXPECT_FALSE(res_json.isMember("base_price"));

  EXPECT_TRUE(res_json["subvention"]["disabled_rules"].isArray());

  const Json::Value& pool_orders = res_json["pool"]["orders"];
  EXPECT_TRUE(pool_orders["order2_0"].isMember("fixed_price"));
  EXPECT_EQ(pool_orders["order2_0"]["fixed_price"]["price"], 100);
  EXPECT_FALSE(pool_orders["order2_1"].isMember("fixed_price"));
  for (const auto& pair : statuses.embedded_statuses) {
    EXPECT_EQ(static_cast<int>(pair.second),
              pool_orders[pair.first]["status"].asInt());
  }

  EXPECT_STREQ("Яндекс.Безналичный", res_json["type_name"].asCString());

  EXPECT_FALSE(res_json.isMember("client_geo_sharing"));
}

TEST(ModelsOrderSetCarDriverReservEtag, Parse) {
  using models::order::set_car::driver::reserv::Etag;
  Etag etag;

  etag.Parse("beeefdddf5654b5687568160b93e6027_3155378975999999999");
  EXPECT_STREQ("beeefdddf5654b5687568160b93e6027", etag.value.c_str())
      << etag.ToPrettyString();
  EXPECT_EQ(Etag::kDefaultDelay, etag.delay) << etag.ToPrettyString();
  EXPECT_STREQ("beeefdddf5654b5687568160b93e6027_3155378975999999999",
               etag.ToString().c_str())
      << etag.ToPrettyString();

  etag.Parse("26b48f44e62c429e8a6a9858c5ab2ec6_636394707000000000");
  EXPECT_STREQ("26b48f44e62c429e8a6a9858c5ab2ec6", etag.value.c_str())
      << etag.ToPrettyString();
  EXPECT_NE(Etag::kDefaultDelay, etag.delay) << etag.ToPrettyString();
  EXPECT_NE(Etag::kEmptyDelay, etag.delay) << etag.ToPrettyString();
  EXPECT_STREQ("26b48f44e62c429e8a6a9858c5ab2ec6_636394707000000000",
               etag.ToString().c_str())
      << etag.ToPrettyString();
}
