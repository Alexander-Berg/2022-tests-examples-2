#include "catalog.hpp"

#include <fstream>
#include <userver/formats/json/string_builder.hpp>
#include <userver/utest/utest.hpp>

#include "delivery_zone.hpp"
#include "place.hpp"

namespace eats_catalog_storage::models {

extern const std::string kExpectedCatalogRecordJson;

TEST(Catalog, DumpFormat) {
  PlaceCacheItem place;
  place.id = 205753;
  place.created_at =
      utils::datetime::FromRfc3339StringSaturating("2020-04-30T15:46:00+03:00");
  place.updated_at =
      utils::datetime::FromRfc3339StringSaturating("2020-05-05T15:46:00+03:00");
  place.slug = "bazar_sadovaya_3_anilb";
  place.enabled = true;
  place.name = "Bazar";
  place.revision = 0;
  place.type = PlaceType::kNative;
  place.business = "restaurant";
  place.launched_at =
      utils::datetime::FromRfc3339StringSaturating("2020-04-27T15:46:00+03:00");

  place.payment_methods = {
      PlacePaymentMethod::kPayture, PlacePaymentMethod::kApplePay,
      PlacePaymentMethod::kTaxi, PlacePaymentMethod::kGooglePay,
      PlacePaymentMethod::kCardPostPayment};
  place.gallery = {
      PlaceGallery{
          "picture",
          "https://avatars.mds.yandex.net/get-eda/1387779/"
          "f3819fadbe9b062b26a7df079c534e61/214x140",
          {"/images/1387779/f3819fadbe9b062b26a7df079c534e61-{w}x{h}.jpg"},
          100},
      PlaceGallery{"video", "https://video.url", std::nullopt, 1}};
  place.brand = PlaceBrand{20064, "bazar_mvsij", "Bazar"};

  place.address = PlaceAddress{"Иваново", "Садовая улица, 3"};
  place.country =
      PlaceCountry{35, "Российская Федерация", "RU", {"RUB", "₽"}};
  place.categories = {
      PlaceCategory{235, "Завтраки"}, {593, "Выпечка"}, {37, "Узбекская"}};

  place.quick_filters = {PlaceQuickFilter{21, "slug21"},
                         PlaceQuickFilter{130, "black_mamba"}};
  place.wizard_quick_filters = {PlaceQuickFilter{21, "slug21"},
                                PlaceQuickFilter{45, "slug45"},
                                PlaceQuickFilter{130, "slug130"}};

  place.region = PlaceRegion{57, {5}, "Europe/Moscow", "region_name"};
  place.location = {40.984494, 57.001598};
  place.price_category = PlacePriceCategory{2, "₽₽", 0.5};
  place.assembly_cost = 10;

  place.rating =
      storages::postgres::PlainJson{ConvertPlaceRating(handlers::Rating{
          /*shown*/ {4.6034},
          /*users*/ 4.6034,
          /*admin*/ 5.0,
          /*count*/ 116,
      })};
  place.new_rating = storages::postgres::PlainJson{
      handlers::Serialize(handlers::NewRating{4.7, true},
                          ::formats::serialize::To<formats::json::Value>{})};
  place.extra_info =
      storages::postgres::PlainJson{ConvertPlaceExtraInfo(handlers::ExtraInfo{
          /*footer_description*/ {"footer_description"},
          /*legal_info_description*/
          {"Исполнитель (продавец): ООО \"Возрождение\", 153012, "
           "Ивановская обл., Иваново г, Садовая ул., д.3, ИНН 3702651753, "
           "рег.номер 1113702017164."}})};
  place.features =
      storages::postgres::PlainJson{ConvertPlaceFeatures(handlers::Feature{
          /*ignore_surge*/ false,
          /*supports_preordering*/ true,
          /*fast_food*/ false,
          /*eco_package*/ {false},
          /*visibility_mode*/ {"on"},
          /*availability_strategy*/ {"burger_king"},
          /*editorial_description*/ {"Отличное место для бизнес-ланча"},
          /*editorial_verdict*/ {"Обедайте только здесь!"},
          /*brand_ui_backgrounds*/
          {std::vector<handlers::BrandUIBackground>{
              {handlers::BrandUIBackgroundTheme::kLight, "#1f1f1F"},
              {handlers::BrandUIBackgroundTheme::kDark, "#1f1f1F"},
          }},
          /*brand_ui_logo*/
          {std::vector<handlers::BrandUILogo>{
              {handlers::BrandUILogoTheme::kLight,
               "http://avatars.mdst.yandex.net/get-eda/69745/"
               "67df013c7628ce8d549de20a164038a0/orig",
               handlers::BrandUILogoSize::kSmall},
              {handlers::BrandUILogoTheme::kLight,
               "http://avatars.mdst.yandex.net/get-eda/69745/"
               "67df013c7628ce8d549de20a164038a0/orig",
               handlers::BrandUILogoSize::kMedium}}},
          /*constraints*/
          {std::vector<handlers::PlaceConstraint>{
              {handlers::PlaceConstraintCode::kMaxOrderCost, 10000},
              {handlers::PlaceConstraintCode::kMaxOrderWeight, 15}}}})};
  place.timing = storages::postgres::PlainJson{
      ConvertPlaceTiming(handlers::Timing{/*preparation*/ 24 * 60,
                                          /*extra_preparation*/ 600,
                                          /*average_preparation*/ 20 * 60})};
  place.sorting = storages::postgres::PlainJson{
      ConvertPlaceSorting(handlers::Sorting{/*weight*/ 100,
                                            /*popular*/ 1000,
                                            /*wizard*/ {12}})};
  place.address_comment = {};
  place.contacts = {};
  place.archived = false;

  const DeliveryZone zone{
      /*id*/ 940904,
      /*source*/ Source::kEatsCore,
      /*external_id*/ "id-940904",
      /*place_id*/ 205753,
      /*place_ids*/ std::nullopt,
      /*couriers_zone_id*/ 8050,
      /*name*/ "isochrone_automobile_20",
      /*created_at*/
      utils::datetime::FromRfc3339StringSaturating("2020-05-01T15:46:00+03:00"),
      /*updated_at*/
      utils::datetime::FromRfc3339StringSaturating("2020-05-07T15:46:00+03:00"),
      /*revision*/ 0,
      /*enabled*/ true,
      /*couriers_type*/ CouriersType::kYandexTaxi,
      /*shipping_type*/ ShippingType::kDelivery,
      /*delivery_conditions*/
      {DeliveryCondition{200, 1000}, DeliveryCondition{150, 2500}},
      /*market_avg_time*/ {600.0},

      /*time_of_arrival*/ {1200.0},
      /*working_intervals*/
      {WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599116400)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599152400))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599202800)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599238800))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599289200)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599325200))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599375600)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599411600))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599462000)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599498000))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599548400)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599584400))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599634800)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599670800))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599721200)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599757200))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599807600)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599843600))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599894000)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599930000))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1599980400)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600016400))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600066800)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600102800))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600153200)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600189200))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600239600)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600275600))},
       WorkingInterval{std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600326000)),
                       std::chrono::system_clock::time_point(
                           std::chrono::seconds(1600362000))}},
      /*polygons*/
      {storages::postgres::io::detail::Polygon{
          {{40.836667, 57.003798}, {40.842155, 57.008107},
           {40.844298, 57.008653}, {40.855585, 57.013111},
           {40.858114, 57.014378}, {40.885306, 57.03007},
           {40.886631, 57.03767},  {40.886568, 57.038429},
           {40.88509, 57.04372},   {40.888252, 57.058752},
           {40.913819, 57.089751}, {40.919312, 57.088117},
           {40.924437, 57.085647}, {40.929876, 57.082793},
           {40.934951, 57.080137}, {40.962058, 57.075287},
           {41.00043, 57.089421},  {41.050259, 57.068588},
           {41.053336, 57.052021}, {41.045058, 57.047598},
           {41.040553, 57.028797}, {41.05392, 57.01915},
           {41.074518, 57.005178}, {41.108542, 56.988242},
           {41.107145, 56.975901}, {41.100893, 56.958549},
           {41.080752, 56.930802}, {41.068648, 56.934191},
           {41.066739, 56.934728}, {41.055591, 56.941674},
           {41.050147, 56.943442}, {40.99663, 56.940899},
           {40.992053, 56.937036}, {40.984008, 56.925414},
           {40.98055, 56.924777},  {40.957971, 56.91278},
           {40.944173, 56.906998}, {40.937332, 56.902095},
           {40.942021, 56.915821}, {40.942044, 56.916244},
           {40.952316, 56.92856},  {40.952347, 56.933741},
           {40.943252, 56.945001}, {40.915674, 56.968322},
           {40.862399, 56.972583}, {40.864672, 56.976176},
           {40.858572, 56.993439}, {40.836667, 57.003798}}}},

      /*archived*/
      false,
  };

  const std::unordered_set<ShippingType> expected_shipping_types = {
      ShippingType::kPickup, ShippingType::kDelivery};
  const handlers::GoCatalogDumpRecord r = CreateCatalogS3DumpRecord(
      place, zone, {{place.id, expected_shipping_types}});

  EXPECT_EQ(r.address.city, place.address.city);
  EXPECT_EQ(r.address.short_, place.address.short_);
  EXPECT_EQ(r.brand_id, place.brand.id);
  EXPECT_EQ(r.brand_name, place.brand.name);
  EXPECT_EQ(r.brand_slug, place.brand.slug);
  EXPECT_EQ(r.brand_business, place.business);
  EXPECT_EQ(r.place_country.code, place.country.code);
  EXPECT_EQ(r.place_currency.code, place.country.currency.code);
  EXPECT_EQ(r.place_currency.sign, place.country.currency.sign);
  EXPECT_EQ(r.place_country.id, place.country.id);
  EXPECT_EQ(r.place_country.name, place.country.name);
  EXPECT_EQ(r.place_footer_description,
            place.extra_info["footer_description"].As<std::string>());
  EXPECT_EQ(r.place_legal_info_description,
            place.extra_info["legal_info_description"].As<std::string>());
  EXPECT_EQ(r.use_eco_package, place.features["eco_package"].As<bool>());
  EXPECT_EQ(r.is_fast_food, place.features["fast_food"].As<bool>());
  EXPECT_EQ(r.brand_ignore_surge, place.features["ignore_surge"].As<bool>());
  EXPECT_EQ(r.brand_supports_orders_by_time,
            place.features["supports_preordering"].As<bool>());
  EXPECT_EQ(r.place_visibility_mode,
            place.features["visibility_mode"].As<std::string>());

  auto place_brand_ui_backgrounds = place.features["brand_ui_backgrounds"];
  EXPECT_TRUE(place_brand_ui_backgrounds.IsArray());
  size_t backgrounds_size = place_brand_ui_backgrounds.GetSize();
  EXPECT_EQ(r.brand_ui_backgrounds.size(), backgrounds_size);
  for (size_t i = 0; i < backgrounds_size; i++) {
    EXPECT_EQ(r.brand_ui_backgrounds[i],
              place_brand_ui_backgrounds[i].As<handlers::BrandUIBackground>());
  }

  auto place_brand_ui_logos = place.features["brand_ui_logos"];
  EXPECT_TRUE(place_brand_ui_logos.IsArray());
  size_t logo_size = place_brand_ui_logos.GetSize();
  EXPECT_EQ(r.brand_ui_logos.size(), logo_size);
  for (size_t i = 0; i < logo_size; i++) {
    EXPECT_EQ(r.brand_ui_logos[i],
              place_brand_ui_logos[i].As<handlers::BrandUILogo>());
  }

  auto place_constraints = place.features["constraints"];
  EXPECT_TRUE(place_constraints.IsArray());
  size_t constraints_size = place_constraints.GetSize();
  EXPECT_EQ(r.place_constraints.size(), constraints_size);
  for (size_t i = 0; i < backgrounds_size; i++) {
    EXPECT_EQ(r.place_constraints[i],
              place_constraints[i].As<handlers::PlaceConstraint>());
  }

  EXPECT_EQ(r.launched, place.launched_at);
  EXPECT_DOUBLE_EQ(r.place_point.lon, place.location.x);
  EXPECT_DOUBLE_EQ(r.place_point.lat, place.location.y);
  EXPECT_EQ(r.place_name, place.name);

  ASSERT_EQ(r.payment_methods.size(), place.payment_methods.size());
  for (size_t i = 0; i < r.payment_methods.size(); ++i) {
    EXPECT_EQ(r.payment_methods[i], static_cast<int>(place.payment_methods[i]));
  }

  EXPECT_EQ(r.place_price_category.id, place.price_category.id);
  EXPECT_EQ(r.place_price_category.name, place.price_category.name);
  EXPECT_EQ(r.place_price_category.value, place.price_category.value);
  EXPECT_EQ(r.common_quick_filters_ids, (std::vector<int64_t>{21, 130}));
  EXPECT_EQ(r.wizard_quick_filters_ids, (std::vector<int64_t>{21, 45, 130}));
  EXPECT_EQ(r.place_rating, place.rating["admin"].As<int>());
  EXPECT_EQ(r.rating_count, place.rating["count"].As<int>());

  EXPECT_TRUE(r.place_avg_rating.has_value());
  EXPECT_DOUBLE_EQ(*r.place_avg_rating, place.rating["shown"].As<double>());

  EXPECT_DOUBLE_EQ(r.real_avg_rating, place.rating["users"].As<double>());
  EXPECT_EQ(r.region_geobase_ids, place.region.geobase_ids);
  EXPECT_EQ(r.place_region_id, place.region.id);
  EXPECT_EQ(r.place_region_timezone, place.region.time_zone);
  EXPECT_EQ(r.place_slug, place.slug);
  EXPECT_EQ(r.sort_scores.popular, place.sorting["popular"].As<int>());
  EXPECT_EQ(r.place_sort, place.sorting["weight"].As<int>());

  if (r.wizard_sort_order) {
    EXPECT_EQ(*r.wizard_sort_order, place.sorting["wizard"].As<std::int64_t>());
  } else {
    EXPECT_FALSE(place.sorting.GetUnderlying().HasMember("wizard"));
  }

  EXPECT_EQ(r.extra_preparation_minutes,
            place.timing["extra_preparation"].As<int>() / 60);
  EXPECT_EQ(r.place_avg_prepare_time,
            place.timing["average_preparation"].As<int>() / 60);
  EXPECT_EQ(r.place_prepare_time, place.timing["preparation"].As<int>() / 60);

  EXPECT_EQ(static_cast<int>(r.place_type), static_cast<int>(place.type));
  EXPECT_EQ(static_cast<int>(r.couriers_type),
            static_cast<int>(zone.couriers_type));

  ASSERT_EQ(r.delivery_conditions.size(), zone.delivery_conditions.size());
  for (size_t i = 0; i < r.delivery_conditions.size(); ++i) {
    EXPECT_EQ(r.delivery_conditions[i].delivery_cost,
              zone.delivery_conditions[i].delivery_cost);
    EXPECT_EQ(r.delivery_conditions[i].order_cost,
              zone.delivery_conditions[i].order_cost);
  }

  EXPECT_EQ(r.delivery_zone_name, zone.name);

  ASSERT_TRUE(!zone.polygons.empty());
  EXPECT_EQ(r.place_coordinates.type, "polygon");
  ASSERT_EQ(r.place_coordinates.coordinates.size(), 1);
  auto& points = r.place_coordinates.coordinates.front();
  ASSERT_EQ(points.size(), zone.polygons.front().points.size());
  for (size_t i = 0; i < zone.polygons.front().points.size(); ++i) {
    ASSERT_EQ(points[i].size(), 2);
    EXPECT_DOUBLE_EQ(points[i][0], zone.polygons.front().points[i].x);
    EXPECT_DOUBLE_EQ(points[i][1], zone.polygons.front().points[i].y);
  }

  EXPECT_EQ(static_cast<int>(r.delivery_zone_shipping_type),
            static_cast<int>(zone.shipping_type));

  EXPECT_EQ(r.delivery_zone_source_info.source,
            models::ConvertSourceToHandlers(zone.source));
  EXPECT_EQ(r.delivery_zone_source_info.external_id, zone.external_id);

  ASSERT_EQ(r.place_working_intervals.size(), zone.working_intervals.size());
  for (size_t i = 0; i < zone.working_intervals.size(); ++i) {
    EXPECT_EQ(r.place_working_intervals[i].gte,
              std::chrono::duration_cast<std::chrono::seconds>(
                  zone.working_intervals[i].from.time_since_epoch())
                  .count());
    EXPECT_EQ(r.place_working_intervals[i].lte,
              std::chrono::duration_cast<std::chrono::seconds>(
                  zone.working_intervals[i].to.time_since_epoch())
                  .count());
  }

  EXPECT_EQ(r.api_categories, "Завтраки,Выпечка,Узбекская");
  EXPECT_FALSE(r.brand_is_store);

  EXPECT_EQ(r.delivery_cost, 150);
  EXPECT_EQ(r.min_order_price, 1000);
  EXPECT_EQ(r.indexed_at, utils::datetime::FromRfc3339StringSaturating(
                              "2020-05-07T15:46:00+03:00"));

  EXPECT_EQ(r.place_indexed_at, utils::datetime::FromRfc3339StringSaturating(
                                    "2020-05-05T15:46:00+03:00"));
  EXPECT_EQ(r.delivery_zone_indexed_at,
            utils::datetime::FromRfc3339StringSaturating(
                "2020-05-07T15:46:00+03:00"));

  ASSERT_EQ(r.place_categories.size(), place.categories.size());
  for (size_t i = 0; i < r.place_categories.size(); ++i) {
    EXPECT_EQ(r.place_categories[i].name, place.categories[i].text);
    EXPECT_EQ(r.place_categories[i].id, place.categories[i].id);
  }

  EXPECT_EQ(r.delivery_zone_id, zone.id);
  EXPECT_EQ(r.place_id, place.id);
  EXPECT_TRUE(r.place_enabled);
  if (zone.time_of_arrival) {
    EXPECT_DOUBLE_EQ(*r.delivery_zone_time_of_arrival,
                     *zone.time_of_arrival / 60.0);
  } else {
    EXPECT_FALSE(r.delivery_zone_time_of_arrival.has_value());
  }

  ASSERT_EQ(r.place_pictures.size(), 1);
  EXPECT_EQ(r.place_pictures[0].url,
            "https://avatars.mds.yandex.net/get-eda/1387779/"
            "f3819fadbe9b062b26a7df079c534e61/214x140");
  EXPECT_EQ(r.place_pictures[0].template_,
            "/images/1387779/f3819fadbe9b062b26a7df079c534e61-{w}x{h}.jpg");
  EXPECT_EQ(r.place_pictures[0].sort, 100);
  EXPECT_EQ(r.place_pictures[0].enabled, true);

  ASSERT_FALSE(place.gallery.empty());
  EXPECT_EQ(r.place_picture_url, place.gallery[0].url);
  ASSERT_TRUE(place.gallery[0].template_.has_value());
  EXPECT_EQ(r.place_picture_template, *place.gallery[0].template_);

  ASSERT_EQ(r.place_shipping_types.size(), expected_shipping_types.size());
  for (auto type : r.place_shipping_types) {
    EXPECT_EQ(
        expected_shipping_types.count(ShippingType(static_cast<int>(type))), 1);
  }

  EXPECT_EQ(r.couriers_zone_id, zone.couriers_zone_id);
  ASSERT_TRUE(zone.market_avg_time.has_value());
  EXPECT_DOUBLE_EQ(r.marketplace_avg_time, *zone.market_avg_time / 60.0);

  ASSERT_TRUE(r.editorial_description.has_value());
  EXPECT_EQ(*r.editorial_description, "Отличное место для бизнес-ланча");
  ASSERT_TRUE(r.editorial_verdict.has_value());
  EXPECT_EQ(*r.editorial_verdict, "Обедайте только здесь!");

  ASSERT_TRUE(r.place_availability_strategy.has_value());
  EXPECT_EQ(*r.place_availability_strategy, "burger_king");

  EXPECT_EQ(r.assembly_cost, place.assembly_cost);

  // Проверка ниже нужна, чтобы застраховаться от случая, когда выше мы
  // забыли провалидировать какое-то поле. Мы загружаем эталонный JSON и
  // сравниваем его целиком с тем объектом, который у нас получился.
  //
  // Если они оказались неравны, нужно понять, в каких полях есть
  // рахождение. Я это делал так. Раскомментировал строки ниже, в которых
  // выполняется сохранение обоих объектов в файлы r.json и e.json
  // соответственно, а затем в консоли выполнил команды:
  //
  // $ cd <path-to-uservices-repo>
  // $ make utest-eats-catalog-storage
  // $ cat build/services/eats-catalog-storage/r.json | python -m json.tool
  // > result.json $ cat build/services/eats-catalog-storage/e.json | python
  // -m json.tool > etalon.json $ diff -y --color=always result.json
  // etalon.json | less -SR
  //
  // diff'ом находим, какие поля отличаются, разбираемся, исправляем
  const handlers::GoCatalogDumpRecord expected =
      handlers::Parse(formats::json::FromString(kExpectedCatalogRecordJson),
                      formats::parse::To<handlers::GoCatalogDumpRecord>());
  //  {
  //    formats::json::StringBuilder json_builder;
  //    handlers::WriteToStream(r, json_builder);
  //    std::ofstream output("r.json");
  //    output << json_builder.GetString() << '\n';
  //  }
  //  {
  //    formats::json::StringBuilder json_builder;
  //    handlers::WriteToStream(expected, json_builder);
  //    std::ofstream output("e.json");
  //    output << json_builder.GetString() << '\n';
  //  }
  ASSERT_EQ(r, expected);
}

const std::string kExpectedCatalogRecordJson = R"(
{
  "delivery_conditions": [
    {
      "delivery_cost": 200,
      "order_cost": 1000
    },
    {
      "delivery_cost": 150,
      "order_cost": 2500
    }
  ],
  "common_quick_filters_ids": [
    21,
    130
  ],
  "place_point": {
    "lon": 40.984494,
    "lat": 57.001598
  },
  "place_pictures": [
    {
      "template": "/images/1387779/f3819fadbe9b062b26a7df079c534e61-{w}x{h}.jpg",
      "sort": 100,
      "url": "https://avatars.mds.yandex.net/get-eda/1387779/f3819fadbe9b062b26a7df079c534e61/214x140",
      "enabled": true
    }
  ],
  "assembly_cost": 10,
  "place_categories": [
    {
      "quick_filter_id": 0,
      "name": "Завтраки",
      "id": 235,
      "sort": 0
    },
    {
      "quick_filter_id": 0,
      "name": "Выпечка",
      "id": 593,
      "sort": 0
    },
    {
      "quick_filter_id": 0,
      "name": "Узбекская",
      "id": 37,
      "sort": 0
    }
  ],
  "editorial_verdict": "Обедайте только здесь!",
  "brand_slug": "bazar_mvsij",
  "sort_scores": {
    "popular": 1000
  },
  "launched": "2020-04-27T15:46:00+03:00",
  "place_rating": 5,
  "new_rating": {
    "rating": 4.7, "show": true
  },
  "couriers_zone_id": 8050,
  "payment_methods": [
    1,
    2,
    3,
    4,
    6
  ],
  "brand_ignore_surge": false,
  "delivery_cost": 150,
  "indexed_at": "2020-05-07T15:46:00+03:00",
  "place_indexed_at": "2020-05-05T15:46:00+03:00",
  "delivery_zone_indexed_at": "2020-05-07T15:46:00+03:00",
  "place_availability_strategy": "burger_king",
  "brand_is_store": false,
  "editorial_description": "Отличное место для бизнес-ланча",
  "place_id": 205753,
  "min_order_price": 1000,
  "place_country": {
    "code": "RU",
    "name": "Российская Федерация",
    "id": 35
  },
  "use_eco_package": false,
  "brand_name": "Bazar",
  "brand_id": 20064,
  "rating_count": 116,
  "delivery_zone_id": 940904,
  "is_fast_food": false,
  "place_coordinates": {
    "coordinates": [
      [
        [
          40.836667,
          57.003798
        ],
        [
          40.842155,
          57.008107
        ],
        [
          40.844298,
          57.008653
        ],
        [
          40.855585,
          57.013111
        ],
        [
          40.858114,
          57.014378
        ],
        [
          40.885306,
          57.03007
        ],
        [
          40.886631,
          57.03767
        ],
        [
          40.886568,
          57.038429
        ],
        [
          40.88509,
          57.04372
        ],
        [
          40.888252,
          57.058752
        ],
        [
          40.913819,
          57.089751
        ],
        [
          40.919312,
          57.088117
        ],
        [
          40.924437,
          57.085647
        ],
        [
          40.929876,
          57.082793
        ],
        [
          40.934951,
          57.080137
        ],
        [
          40.962058,
          57.075287
        ],
        [
          41.00043,
          57.089421
        ],
        [
          41.050259,
          57.068588
        ],
        [
          41.053336,
          57.052021
        ],
        [
          41.045058,
          57.047598
        ],
        [
          41.040553,
          57.028797
        ],
        [
          41.05392,
          57.01915
        ],
        [
          41.074518,
          57.005178
        ],
        [
          41.108542,
          56.988242
        ],
        [
          41.107145,
          56.975901
        ],
        [
          41.100893,
          56.958549
        ],
        [
          41.080752,
          56.930802
        ],
        [
          41.068648,
          56.934191
        ],
        [
          41.066739,
          56.934728
        ],
        [
          41.055591,
          56.941674
        ],
        [
          41.050147,
          56.943442
        ],
        [
          40.99663,
          56.940899
        ],
        [
          40.992053,
          56.937036
        ],
        [
          40.984008,
          56.925414
        ],
        [
          40.98055,
          56.924777
        ],
        [
          40.957971,
          56.91278
        ],
        [
          40.944173,
          56.906998
        ],
        [
          40.937332,
          56.902095
        ],
        [
          40.942021,
          56.915821
        ],
        [
          40.942044,
          56.916244
        ],
        [
          40.952316,
          56.92856
        ],
        [
          40.952347,
          56.933741
        ],
        [
          40.943252,
          56.945001
        ],
        [
          40.915674,
          56.968322
        ],
        [
          40.862399,
          56.972583
        ],
        [
          40.864672,
          56.976176
        ],
        [
          40.858572,
          56.993439
        ],
        [
          40.836667,
          57.003798
        ]
      ]
    ],
    "type": "polygon"
  },
  "place_avg_prepare_time": 20,
  "place_prepare_time": 24,
  "place_visibility_mode": "on",
  "api_categories": "Завтраки,Выпечка,Узбекская",
  "place_picture_template": "/images/1387779/f3819fadbe9b062b26a7df079c534e61-{w}x{h}.jpg",
  "real_avg_rating": 4.6034,
  "extra_preparation_minutes": 10,
  "place_slug": "bazar_sadovaya_3_anilb",
  "delivery_zone_time_of_arrival": 20,
  "place_legal_info_description": "Исполнитель (продавец): ООО \"Возрождение\", 153012, Ивановская обл., Иваново г, Садовая ул., д.3, ИНН 3702651753, рег.номер 1113702017164.",
  "enabled": true,
  "place_region_timezone": "Europe/Moscow",
  "place_shipping_types": [
    "delivery", "pickup"
  ],
  "place_type": "native",
  "place_price_category": {
    "name": "₽₽",
    "id": 2,
    "value": 0.5
  },
  "place_region_id": 57,
  "place_name": "Bazar",
  "address": {
    "city": "Иваново",
    "short": "Садовая улица, 3"
  },
  "place_avg_rating": 4.6034,
  "delivery_zone_name": "isochrone_automobile_20",
  "wizard_quick_filters_ids": [
    21,
    45,
    130
  ],
  "region_geobase_ids": [
    5
  ],
  "wizard_sort_order": 12,
  "place_currency": {
    "code": "RUB",
    "sign": "₽"
  },
  "place_sort": 100,
  "marketplace_avg_time": 10,
  "brand_supports_orders_by_time": true,
  "brand_business": "restaurant",
  "couriers_type": "yandex_taxi",
  "place_enabled": true,
  "delivery_zone_shipping_type": "delivery",
  "delivery_zone_source_info": {
    "source": "eats_core",
    "external_id": "id-940904"
  },
  "place_picture_url": "https://avatars.mds.yandex.net/get-eda/1387779/f3819fadbe9b062b26a7df079c534e61/214x140",
  "place_working_intervals": [
    {
      "gte": 1599116400,
      "lte": 1599152400
    },
    {
      "gte": 1599202800,
      "lte": 1599238800
    },
    {
      "gte": 1599289200,
      "lte": 1599325200
    },
    {
      "gte": 1599375600,
      "lte": 1599411600
    },
    {
      "gte": 1599462000,
      "lte": 1599498000
    },
    {
      "gte": 1599548400,
      "lte": 1599584400
    },
    {
      "gte": 1599634800,
      "lte": 1599670800
    },
    {
      "gte": 1599721200,
      "lte": 1599757200
    },
    {
      "gte": 1599807600,
      "lte": 1599843600
    },
    {
      "gte": 1599894000,
      "lte": 1599930000
    },
    {
      "gte": 1599980400,
      "lte": 1600016400
    },
    {
      "gte": 1600066800,
      "lte": 1600102800
    },
    {
      "gte": 1600153200,
      "lte": 1600189200
    },
    {
      "gte": 1600239600,
      "lte": 1600275600
    },
    {
      "gte": 1600326000,
      "lte": 1600362000
    }
  ],
  "place_footer_description": "footer_description",
  "brand_ui_backgrounds": [
    {
      "theme" : "light",
      "color" : "#1f1f1F"
    },
    {
      "theme" : "dark",
      "color" : "#1f1f1F"
    }
  ],
  "brand_ui_logos": [
    {
      "theme" : "light",
      "url" : "http://avatars.mdst.yandex.net/get-eda/69745/67df013c7628ce8d549de20a164038a0/orig",
      "size" : "small"
    },
    {
      "theme" : "light",
      "url" : "http://avatars.mdst.yandex.net/get-eda/69745/67df013c7628ce8d549de20a164038a0/orig",
      "size" : "medium"
    }
  ],
  "place_constraints": [
    {
      "code": "max_order_cost",
      "value": 10000
    },
    {
      "code": "max_order_weight",
      "value": 15
    }
  ]
})";

}  // namespace eats_catalog_storage::models
