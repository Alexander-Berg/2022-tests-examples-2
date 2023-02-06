#include <gtest/gtest.h>

#include <models/filters/parse.hpp>
#include <models/values/error.hpp>

namespace {

using Result = models::filters::Filter::Result;

}  // namespace

TEST(TestFilter, ParseCreate) {
  const std::string kJsonFilters = R"(
    {
      "$and": [
        {
          "$not": {"tariff_zone": "123"}
        },
        {
          "$or": [
            {"is_frozen.freeze": {"$eq": true}},
            {"order_info.id": {"$ne": "order_id"}},
            {"order_info.chained_id": {"$ne": "chained_id"}}
          ]
        },
        {"payment_methods.actual": {"$all": ["cash"]}},
        {"payment_methods.dispatch": {"$any": ["cash"]}},
        {"payment_methods.taximeter": {"$any": ["cash"]}},
        {"car_classes.actual": {"$any": []}},
        {"car_classes.dispatch": ["econom", "comfort"]},
        {"car_classes.taximeter": {"$all": ["econom", "comfort"]}},
        {"car_classes.chain": {"$any": ["express"]}},
        {"ids.park_id": {"$ne": "park_id"}},
        {"ids.driver_profile_id": {"$ne": "profile_id"}},
        {"ids.udid": "udid"},
        {"ids.car_number": "car_number"},
        {"ids.driver_license_hash": "driver_license_hash"},
        {"reposition.enabled": false},
        {"reposition.mode": "home"},
        {"tags.tag_names": {"$any": ["tag_name"]}},
        {"statuses.driver": "online"},
        {"statuses.taximeter": "free"},
        {"statuses.order": "busy"},
        {"airports.queue_place": {"$ge": 3}},
        {"airports.queue_place": {"$le": 5}}
      ]
    }
  )";

  const auto& json = formats::json::FromString(kJsonFilters);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  const std::unordered_set<std::string> kAllFields{"payment_methods.actual",
                                                   "payment_methods.dispatch",
                                                   "payment_methods.taximeter",
                                                   "car_classes.actual",
                                                   "car_classes.dispatch",
                                                   "car_classes.taximeter",
                                                   "car_classes.chain",
                                                   "ids.park_id",
                                                   "ids.driver_profile_id",
                                                   "ids.udid",
                                                   "ids.car_number",
                                                   "ids.driver_license_hash",
                                                   "reposition.enabled",
                                                   "reposition.mode",
                                                   "tags.tag_names",
                                                   "statuses.driver",
                                                   "statuses.taximeter",
                                                   "statuses.order",
                                                   "airports.queue_place",
                                                   "is_frozen.freeze",
                                                   "tariff_zone",
                                                   "order_info.id",
                                                   "order_info.chained_id"};
  ASSERT_EQ(filter->GetRequiredFields(), kAllFields);
}

TEST(TestFilter, CheckAnd) {
  const std::string kJsonAndFilter = R"(
    {
      "$and": [
        {"tariff_zone": "moscow"},
        {"is_frozen.freeze": {"$eq": true}}
      ]
    }
  )";

  const auto& json = formats::json::FromString(kJsonAndFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.tariff_zone = "moscow";
  driver_info.is_frozen = models::IsFrozen{true};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.tariff_zone = "sbp";
  driver_info.is_frozen = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.tariff_zone = "moscow";
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckOr) {
  const std::string kJsonOrFilter = R"(
    {
      "$or": [
        {"tariff_zone": "moscow"},
        {"is_frozen.freeze": {"$eq": true}}
      ]
    }
  )";

  const auto& json = formats::json::FromString(kJsonOrFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.tariff_zone = "moscow";
  driver_info.is_frozen = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.tariff_zone = "spb";
  driver_info.is_frozen = models::IsFrozen{false};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.is_frozen = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckNot) {
  const std::string kJsonNotFilter = R"(
    {
      "$not": {"tariff_zone": "moscow"}
    }
  )";

  const auto& json = formats::json::FromString(kJsonNotFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.tariff_zone = "spb";
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.tariff_zone = "moscow";
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.tariff_zone = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckAll) {
  const std::string kJsonAllFilter = R"(
    {"car_classes.actual": {"$all": ["econom", "comfort"]}}
  )";

  const auto& json = formats::json::FromString(kJsonAllFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.car_classes =
      models::CarClasses{{"comfort", "econom"}, {}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.car_classes = models::CarClasses{{"comfort"}, {}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.car_classes = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckAny) {
  const std::string kJsonAnyFilter = R"(
    {"car_classes.actual": {"$any": ["econom", "comfort"]}}
  )";

  const auto& json = formats::json::FromString(kJsonAnyFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.car_classes =
      models::CarClasses{{"express", "econom"}, {}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.car_classes = models::CarClasses{{"express"}, {}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.car_classes = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckEq) {
  const std::string kJsonEqFilter = R"(
    {"statuses.driver": {"$eq": "free"}}
  )";

  const auto& json = formats::json::FromString(kJsonEqFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.statuses = models::Statuses{"free", "off", "none"};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.statuses = models::Statuses{"busy", "off", "none"};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.statuses = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckNe) {
  const std::string kJsonNeFilter = R"(
    {"car_classes.dispatch": ["econom", "comfort"]}
  )";

  const auto& json = formats::json::FromString(kJsonNeFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.car_classes =
      models::CarClasses{{}, {"comfort", "econom"}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.car_classes =
      models::CarClasses{{}, {"comfort", "express"}, {}, {}};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.car_classes = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckLe) {
  const std::string kJsonLeFilter = R"(
    {"airports.queue_place": {"$le": 3}}
  )";

  const auto& json = formats::json::FromString(kJsonLeFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.airports = models::Airports{3};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.airports = models::Airports{4};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.airports = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckGe) {
  const std::string kJsonGeFilter = R"(
    {"airports.queue_place": {"$ge": 3}}
  )";

  const auto& json = formats::json::FromString(kJsonGeFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.airports = models::Airports{4};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.airports = models::Airports{2};
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);

  driver_info.airports = std::nullopt;
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kUnknown);
}

TEST(TestFilter, CheckIn) {
  const std::string kJsonInFilter = R"(
    {"statuses.driver": {"$in": ["busy", "verybusy", "superbusy"]}}
  )";

  const auto& json = formats::json::FromString(kJsonInFilter);

  auto filter = models::filters::Parse(json);
  ASSERT_TRUE(filter);

  models::DriverInfo driver_info;

  driver_info.statuses = models::Statuses{};
  driver_info.statuses->driver = "busy";
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kAllowed);

  driver_info.statuses->driver = "superpuperbusy";
  ASSERT_EQ(filter->Satisfy(driver_info), Result::kDisallowed);
}

TEST(TestFilter, CreateAndFailed) {
  const std::string kJsonAndFailedFilter = R"(
    {
      "$and": {"tariff_zone": "moscow"}
    }
  )";

  const auto& json = formats::json::FromString(kJsonAndFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateOrFailed) {
  const std::string kJsonOrFailedFilter = R"(
    {
      "$or": [
        {"tariff_zone": "moscow"}
      ]
    }
  )";

  const auto& json = formats::json::FromString(kJsonOrFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateNotFailed) {
  const std::string kJsonNotFailedFilter = R"(
    {
      "$not": "moscow"
    }
  )";

  const auto& json = formats::json::FromString(kJsonNotFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateAllFailed) {
  const std::string kJsonAllFailedFilter = R"(
    {"car_classes.actual": {"$all": "econom"}}
  )";

  const auto& json = formats::json::FromString(kJsonAllFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateAnyFailed) {
  const std::string kJsonAnyFailedFilter = R"(
    {"car_classes.actual": {"$any": {"key": "value"}}}
  )";

  const auto& json = formats::json::FromString(kJsonAnyFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateEqFailed) {
  const std::string kJsonEqFailedFilter = R"(
    {"ids.car_number": {"$eq": 123456}}
  )";

  const auto& json = formats::json::FromString(kJsonEqFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateNeFailed) {
  const std::string kJsonNeFailedFilter = R"(
    {"ids.car_number": {"$ne": true}}
  )";

  const auto& json = formats::json::FromString(kJsonNeFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateLeFailed) {
  const std::string kJsonLeFailedFilter = R"(
    {"airports.queue_place": {"$le": false}}
  )";

  const auto& json = formats::json::FromString(kJsonLeFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateGeFailed) {
  const std::string kJsonGeFailedFilter = R"(
    {"airports.queue_place": {"$ge": "3"}}
  )";

  const auto& json = formats::json::FromString(kJsonGeFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, FieldFailed) {
  const std::string kJsonFieldFailedFilter = R"(
    {"invalid_field": {"$ge": "3"}}
  )";

  const auto& json = formats::json::FromString(kJsonFieldFailedFilter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}

TEST(TestFilter, CreateInFailed) {
  std::string json_in_filter = R"(
    {"statuses.driver": {"$in": "busy"}}
  )";

  auto json = formats::json::FromString(json_in_filter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);

  json_in_filter = R"(
    {"payment_methods.actual": {"$in": ["busy"]}}
  )";

  json = formats::json::FromString(json_in_filter);
  EXPECT_THROW(models::filters::Parse(json), models::errors::FilterException);
}
