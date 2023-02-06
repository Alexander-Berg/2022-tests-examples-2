#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <models/event.hpp>

TEST(Payload, Serialize) {
  auto payload = billing_time_events::models::Payload{
      "free",
      std::vector<std::string>{"msk", "spb"},
      std::vector<std::string>{"econom", "business"},
      std::vector<std::string>{"tag1", "tag2"},
      "none",
      67.};
  auto json = formats::json::ValueBuilder(payload).ExtractValue();
  EXPECT_EQ(json["activity_points"].As<double>(), payload.activity_points);
  EXPECT_EQ(json["profile_payment_type_restrictions"].As<std::string>(),
            payload.payment_type_restrictions);
  EXPECT_EQ(json["status"].As<std::string>(), payload.status);
  auto geoareas = json["geoareas"].As<std::vector<std::string>>();
  EXPECT_TRUE(std::equal(payload.geoareas.cbegin(), payload.geoareas.cend(),
                         geoareas.cbegin()));
  auto tariffs =
      json["available_tariff_classes"].As<std::vector<std::string>>();
  EXPECT_TRUE(std::equal(payload.tariff_classes.cbegin(),
                         payload.tariff_classes.cend(), tariffs.cbegin()));
  auto tags = json["tags"].As<std::vector<std::string>>();
  EXPECT_TRUE(
      std::equal(payload.tags.cbegin(), payload.tags.cend(), tags.cbegin()));
}

TEST(Payload, Deserialize) {
  auto builder = formats::json::ValueBuilder(formats::json::Type::kObject);
  builder["status"] = "free";
  builder["geoareas"] = std::vector<std::string>{"msk", "spb"};
  builder["available_tariff_classes"] =
      std::vector<std::string>{"econom", "business"};
  builder["tags"] = std::vector<std::string>{"tag1", "tag2"};
  builder["profile_payment_type_restrictions"] = "cash";
  builder["activity_points"] = 100;
  builder["unique_driver_id"] = "unique_driver_id";
  builder["clid"] = "clid";
  auto payload_json = builder.ExtractValue();
  auto payload = payload_json.As<billing_time_events::models::Payload>();
  EXPECT_EQ(payload.status, "free");
  EXPECT_EQ(payload.geoareas[0], "msk");
  EXPECT_EQ(payload.geoareas[1], "spb");
  EXPECT_EQ(payload.tariff_classes[0], "econom");
  EXPECT_EQ(payload.tariff_classes[1], "business");
  EXPECT_EQ(payload.tags[0], "tag1");
  EXPECT_EQ(payload.tags[1], "tag2");
  EXPECT_EQ(payload.payment_type_restrictions, "cash");
  EXPECT_EQ(payload.activity_points, 100);
  EXPECT_EQ(payload.unique_driver_id, "unique_driver_id");
  EXPECT_EQ(payload.clid, "clid");
}
