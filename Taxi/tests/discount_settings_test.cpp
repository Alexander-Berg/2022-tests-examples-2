#include <userver/formats/bson.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/shared_readable_ptr.hpp>

#include <models/discount_settings.hpp>
#include <mongo/discounts.hpp>
#include <testing/taxi_config.hpp>
#include <views/utils.hpp>

using namespace discmod;

const auto kBrGeoNodesResponse =
    formats::json::FromString(R"=(
{
    "items": [
        {
            "name": "br_kazakhstan",
            "name_en": "Kazakhstan",
            "name_ru": "Казахстан",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_almaty",
            "name_en": "Almaty",
            "name_ru": "Алматы",
            "node_type": "agglomeration",
            "parent_name": "br_kazakhstan",
            "tariff_zones": ["almaty"]
        },
        {
            "name": "br_moscow",
            "name_en": "Moscow",
            "name_ru": "Москва",
            "node_type": "agglomeration",
            "parent_name": "br_moskovskaja_obl"
        },
        {
            "name": "br_moscow_adm",
            "name_en": "Moscow (adm)",
            "name_ru": "Москва (адм)",
            "node_type": "node",
            "parent_name": "br_moscow",
            "tariff_zones": [
                "boryasvo",
                "moscow",
                "vko"
            ]
        },
        {
            "name": "br_moscow_middle_region",
            "name_en": "Moscow (Middle Region)",
            "name_ru": "Москва (среднее)",
            "node_type": "node",
            "parent_name": "br_moscow"
        },
        {
            "name": "br_moskovskaja_obl",
            "name_en": "Moscow Region",
            "name_ru": "Московская область",
            "node_type": "node",
            "parent_name": "br_tsentralnyj_fo"
        },
        {
            "name": "br_root",
            "name_en": "Basic Hierarchy",
            "name_ru": "Базовая иерархия",
            "node_type": "root"
        },
        {
            "name": "br_russia",
            "name_en": "Russia",
            "name_ru": "Россия",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_tsentralnyj_fo",
            "name_en": "Central Federal District",
            "name_ru": "Центральный ФО",
            "node_type": "node",
            "parent_name": "br_russia"
        }
    ]
}
)=")
        .As<clients::taxi_agglomerations::ListGeoNodes>();

const auto kTree = ::utils::SharedReadablePtr<caches::agglomerations::Tree>(
    std::make_shared<caches::agglomerations::Tree>(kBrGeoNodesResponse));

TEST(DiscountSettings, ParseAgglomerationZoneType) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "moscow";
  doc_builder[discounts::mongo::DiscountSettings::kZoneType] = "agglomeration";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();
  DiscountSettingsData discount_settings(doc_builder.ExtractValue());
  ASSERT_EQ(discount_settings.zone, "moscow");
  ASSERT_EQ(discount_settings.zone_type, handlers::ZoneType::kAgglomeration);
}

TEST(DiscountSettings, ParseMissingZoneType) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "moscow";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();
  DiscountSettingsData discount_settings(doc_builder.ExtractValue());
  ASSERT_EQ(discount_settings.zone, "moscow");
  ASSERT_EQ(discount_settings.zone_type, handlers::ZoneType::kTariffZone);
}

TEST(DiscountSettings, ParseTariffZoneType) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "moscow";
  doc_builder[discounts::mongo::DiscountSettings::kZoneType] = "tariff_zone";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();
  DiscountSettingsData discount_settings(doc_builder.ExtractValue());
  ASSERT_EQ(discount_settings.zone, "moscow");
  ASSERT_EQ(discount_settings.zone_type, handlers::ZoneType::kTariffZone);
}

namespace {
DiscountSettingsItem CreateDiscountSettingsItem(const std::string id) {
  handlers::Discount result;
  result.discount_series_id = id;
  return DiscountSettingsItem(std::move(result));
}

DiscountItems CreateDiscountItems(const std::vector<std::string>& ids) {
  DiscountSettingsItemCPtrList result;
  result.reserve(ids.size());
  for (const auto& id : ids) {
    result.push_back(std::make_shared<const DiscountSettingsItem>(
        CreateDiscountSettingsItem(id)));
  }
  return std::make_shared<const DiscountSettingsItemCPtrList>(
      std::move(result));
}

}  // namespace

TEST(DiscountSettings, FindDiscount) {
  DiscountSettings discount_settings(kTree);
  struct Data {
    std::string zone_name;
    handlers::ZoneType zone_type;
    const std::vector<std::string> ids;
  };
  using ZoneType = handlers::ZoneType;
  std::vector<Data> discount_data = {
      {"moscow", ZoneType::kTariffZone, {"mos1", "mos2", "mos3"}},
      {"br_moscow_adm",
       ZoneType::kAgglomeration,
       {"br_moscow_adm_1", "br_moscow_adm_2"}},
      {"br_moscow", ZoneType::kAgglomeration, {"br_moscow"}},
      {"br_moskovskaja_obl", ZoneType::kAgglomeration, {"br_moskovskaja_obl"}},
      {"br_russia", ZoneType::kAgglomeration, {"br_russia"}},
      {"br_root", ZoneType::kAgglomeration, {"br_root"}},
  };
  for (auto&& item : discount_data) {
    discount_settings.AddData(DiscountSettingsData(
        std::move(item.zone_name), std::move(item.zone_type),
        CreateDiscountItems(item.ids)));
  }
  auto config{
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>()};
  config.discount_search_agglomerations_after_zones.enabled = true;
  config.discount_search_agglomerations_after_zones.level = std::nullopt;
  {
    auto res = discount_settings.GetDiscountsListByTariffZone("moscow", config);
    ASSERT_EQ(res.size(), 6);
    ASSERT_EQ(res[0]->size(), 3);
    ASSERT_EQ((*res[0])[0]->discount_series_id, "mos1");
    ASSERT_EQ((*res[0])[1]->discount_series_id, "mos2");
    ASSERT_EQ((*res[0])[2]->discount_series_id, "mos3");

    ASSERT_EQ(res[1]->size(), 2);
    ASSERT_EQ((*res[1])[0]->discount_series_id, "br_moscow_adm_1");
    ASSERT_EQ((*res[1])[1]->discount_series_id, "br_moscow_adm_2");

    ASSERT_EQ(res[2]->size(), 1);
    ASSERT_EQ((*res[2])[0]->discount_series_id, "br_moscow");

    ASSERT_EQ(res[3]->size(), 1);
    ASSERT_EQ((*res[3])[0]->discount_series_id, "br_moskovskaja_obl");

    ASSERT_EQ(res[4]->size(), 1);
    ASSERT_EQ((*res[4])[0]->discount_series_id, "br_russia");

    ASSERT_EQ(res[5]->size(), 1);
    ASSERT_EQ((*res[5])[0]->discount_series_id, "br_root");
  }
  {
    config.discount_search_agglomerations_after_zones.level = 1;
    auto res = discount_settings.GetDiscountsListByTariffZone("moscow", config);
    ASSERT_EQ(res.size(), 2);
    ASSERT_EQ(res[1]->size(), 2);
    ASSERT_EQ((*res[1])[0]->discount_series_id, "br_moscow_adm_1");
    ASSERT_EQ((*res[1])[1]->discount_series_id, "br_moscow_adm_2");
  }
  {
    config.discount_search_agglomerations_after_zones.level = std::nullopt;
    auto res =
        discount_settings.GetDiscountsListByTariffZone("invalid", config);
    ASSERT_EQ(res.size(), 0);
  }
}

TEST(DiscountSettings, ParseZoneNameOldFormat) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "moscow";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();

  discmod::DiscountSettingsData discount_settings(doc_builder.ExtractValue());
  ASSERT_EQ(discount_settings.zone, "moscow");
}

TEST(DiscountSettings, ParseZoneNameEmptyName) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "ID";
  doc_builder[discounts::mongo::DiscountSettings::kZoneName] = "";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();

  EXPECT_THROW(discmod::DiscountSettingsData(doc_builder.ExtractValue()),
               std::runtime_error);
}

TEST(DiscountSettings, ParseZoneNameNullName) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "ID";
  doc_builder[discounts::mongo::DiscountSettings::kZoneName] =
      formats::bson::Value();
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();

  EXPECT_THROW(discmod::DiscountSettingsData(doc_builder.ExtractValue()),
               std::runtime_error);
}

TEST(DiscountSettings, ParseZoneNameNewFormat) {
  formats::bson::ValueBuilder doc_builder;
  doc_builder[discounts::mongo::DiscountSettings::kId] = "ID";
  doc_builder[discounts::mongo::DiscountSettings::kZoneName] = "moscow";
  doc_builder[discounts::mongo::DiscountSettings::kDiscounts] =
      formats::bson::MakeArray();

  discmod::DiscountSettingsData discount_settings(doc_builder.ExtractValue());
  ASSERT_EQ(discount_settings.zone, "moscow");
}

TEST(SortDiscounts, CheckSorting) {
  std::vector<std::string> discount_classes = {"first", "second", "third"};

  auto discount1 = DiscountSettingsItem(handlers::Discount{});
  discount1.reference_entity_id = 1;
  discount1.discount_class = discount_classes[0];

  auto discount2 = DiscountSettingsItem(handlers::Discount{});
  discount2.reference_entity_id = 2;
  discount2.discount_class = discount_classes[0];

  auto discount3 = DiscountSettingsItem(handlers::Discount{});
  discount3.reference_entity_id = 3;
  discount3.discount_class = discount_classes[1];

  auto discount4 = DiscountSettingsItem(handlers::Discount{});
  discount4.reference_entity_id = 4;
  discount4.discount_class = discount_classes[2];

  auto invalid_discount1 = DiscountSettingsItem(handlers::Discount{});
  invalid_discount1.reference_entity_id = 100;
  invalid_discount1.discount_class = "invalid";

  auto invalid_discount2 = DiscountSettingsItem(handlers::Discount{});
  invalid_discount2.reference_entity_id = 101;
  invalid_discount2.discount_class = "invalid";

  std::vector<DiscountSettingsItemCPtr> discounts = {
      std::make_shared<DiscountSettingsItem>(invalid_discount1),
      std::make_shared<DiscountSettingsItem>(discount3),
      std::make_shared<DiscountSettingsItem>(invalid_discount2),
      std::make_shared<DiscountSettingsItem>(discount1),
      std::make_shared<DiscountSettingsItem>(discount2),
      std::make_shared<DiscountSettingsItem>(discount4)};
  std::vector<int> expected_ids = {1, 2, 3, 4, 100, 101};

  auto getter = [](const DiscountSettingsItemCPtr& item) {
    return item->discount_class;
  };

  SortDiscounts(discounts, discount_classes, getter);

  for (size_t i = 0; i < discounts.size(); i++) {
    ASSERT_EQ(discounts[i]->reference_entity_id, expected_ids[i]);
  }
}
