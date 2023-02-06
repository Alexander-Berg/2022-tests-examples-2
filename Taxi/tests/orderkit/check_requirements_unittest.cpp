#include <common/test_config.hpp>
#include <config/config.hpp>
#include <orderkit/check_requirements.hpp>
#include <orderkit/exceptions.hpp>

#include <gtest/gtest.h>

struct CheckRequirementsParams {
  std::string tariff_class;
  std::string payment_type;
  std::vector<std::string> requirements;
  bool card_enabled;
  bool corp_enabled;
  bool card_tester;
  int hours;
  std::string exception;
};

using CheckRequirements = ::testing::TestWithParam<CheckRequirementsParams>;

TEST_P(CheckRequirements, Basic) {
  const auto& params = GetParam();
  orderkit::Order order;
  order.id = "1111111111111111111111111";
  order.nearest_zone = "moscow";
  order.request.classes.Add(params.tariff_class);
  for (const auto& requirement : params.requirements) {
    order.request.requirements[requirement] = true;
  }
  order.payment_tech.type = models::payment_types::Parse(params.payment_type);
  order.request.payment.type =
      models::payment_types::Parse(params.payment_type);
  if (params.hours != -1) {
    order.request.due =
        utils::datetime::Stringtime("2017-06-26", "Europe/Moscow", "%Y-%m-%d");
    order.request.due += std::chrono::hours(params.hours);
  }
  requirements::Descriptions requirements_descriptions;
  models::requirements::Description nosmoking_requirement;
  nosmoking_requirement.name = "nosmoking";
  nosmoking_requirement.type = models::requirements::types::Type::Boolean;
  requirements_descriptions.push_back(nosmoking_requirement);

  models::ZoneGeoindex zone_geoindex;

  models::TariffSettings tariff_settings;
  tariff_settings.zone_name = order.nearest_zone;
  tariff_settings.timezone = "Europe/Moscow";
  tariff_settings.payment_options[models::PaymentOption::Corp] =
      params.corp_enabled;
  tariff_settings.payment_options[models::PaymentOption::Card] =
      params.card_enabled;
  models::TariffSettings::Category ts_econom_category;
  ts_econom_category.class_type = models::Classes::Econom;
  ts_econom_category.client_requirements.insert("nosmoking");
  ts_econom_category.only_for_soon_orders = true;
  ts_econom_category.restrict_by_payment_type =
      std::set<std::string>{"cash", "card", "googlepay"};
  tariff_settings.categories.push_back(ts_econom_category);
  models::TariffSettings::Category ts_business_category;
  ts_business_category.class_type = models::Classes::Business;
  ts_business_category.restrict_by_payment_type =
      std::set<std::string>{"cash", "corp", "googlepay"};
  tariff_settings.categories.push_back(ts_business_category);
  models::Country country;
  tariff::Tariff tariff;
  tariff.home_zone = order.nearest_zone;
  tariff::Category econom_category;
  econom_category.name = "econom";
  econom_category.category_type = tariff::CategoryType::Application;
  econom_category.day_type = tariff::DayType::Everyday;
  econom_category.time_from = std::make_pair(0, 0);
  econom_category.time_to = std::make_pair(23, 59);
  tariff.categories.push_back(econom_category);
  tariff::Category business_category;
  business_category.name = "business";
  business_category.category_type = tariff::CategoryType::Application;
  business_category.day_type = tariff::DayType::Everyday;
  business_category.time_from = std::make_pair(5, 0);
  business_category.time_to = std::make_pair(7, 0);
  tariff.categories.push_back(business_category);
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override("BILLING_CORP_ENABLED", true);
  docs_map.Override("BILLING_CREDITCARD_ENABLED", true);
  config::Config config(docs_map);
  std::set<std::string> user_experiments;
  if (params.card_tester) user_experiments.insert("card_tester");
  LogExtra log_extra;
  handlers::ProtocolContext context({}, config, {}, log_extra);

  auto call = [&]() {
    orderkit::CheckRequirements(order, requirements_descriptions,
                                tariff_settings, country, tariff, zone_geoindex,
                                user_experiments, {}, context);
  };

  if (params.exception.empty()) {
    call();
  } else if (params.exception == "UnsupportedRequirements") {
    ASSERT_THROW(call(), orderkit::UnsupportedRequirements);
  } else if (params.exception == "UnsupportedPaymentTypeCard") {
    ASSERT_THROW(call(), orderkit::UnsupportedPaymentTypeCard);
  } else if (params.exception == "UnsupportedPaymentTypeCorp") {
    ASSERT_THROW(call(), orderkit::UnsupportedPaymentTypeCorp);
  } else if (params.exception == "TariffIsUnavailableError") {
    ASSERT_THROW(call(), orderkit::TariffIsUnavailableError);
  } else if (params.exception == "TariffIsRestrictedError") {
    ASSERT_THROW(call(), orderkit::TariffIsRestrictedError);
  } else if (params.exception == "TariffUnacceptableDueError") {
    ASSERT_THROW(call(), orderkit::TariffUnacceptableDueError);
  } else if (params.exception == "TariffUnacceptablePaymentTypeError") {
    ASSERT_THROW(call(), orderkit::TariffUnacceptablePaymentTypeError);
  } else {
    ASSERT_TRUE(false);
  }
}

INSTANTIATE_TEST_CASE_P(
    OrderkitCheckReqirements, CheckRequirements,
    ::testing::Values(
        CheckRequirementsParams{"econom",
                                "card",
                                {"creditcard"},
                                0,
                                1,
                                0,
                                -1,
                                "UnsupportedPaymentTypeCard"},
        CheckRequirementsParams{
            "econom", "card", {"creditcard"}, 1, 1, 0, -1, ""},
        CheckRequirementsParams{
            "econom", "card", {"creditcard"}, 0, 1, 1, -1, ""},
        CheckRequirementsParams{"econom",
                                "cash",
                                {"childchair"},
                                0,
                                1,
                                0,
                                -1,
                                "UnsupportedRequirements"},
        CheckRequirementsParams{
            "econom", "cash", {"nosmoking"}, 0, 1, 0, -1, ""},
        CheckRequirementsParams{"econom", "cash", {"coupon"}, 0, 1, 0, -1, ""},
        CheckRequirementsParams{"econom", "cash", {}, 0, 1, 0, -1, ""},
        CheckRequirementsParams{
            "vip", "cash", {}, 0, 1, 0, -1, "TariffIsUnavailableError"},
        CheckRequirementsParams{
            "business", "cash", {}, 0, 1, 0, 4, "TariffIsUnavailableError"},
        CheckRequirementsParams{"business", "cash", {}, 0, 1, 0, 6, ""},
        CheckRequirementsParams{
            "business", "cash", {}, 0, 1, 0, 8, "TariffIsUnavailableError"},
        CheckRequirementsParams{
            "econom", "cash", {}, 0, 1, 0, 5, "TariffUnacceptableDueError"},
        CheckRequirementsParams{"business",
                                "card",
                                {"creditcard"},
                                1,
                                1,
                                0,
                                6,
                                "TariffUnacceptablePaymentTypeError"},
        CheckRequirementsParams{"business",
                                "applepay",
                                {"creditcard"},
                                1,
                                1,
                                0,
                                6,
                                "TariffUnacceptablePaymentTypeError"},
        CheckRequirementsParams{"econom",
                                "corp",
                                {"corp"},
                                1,
                                1,
                                0,
                                -1,
                                "TariffUnacceptablePaymentTypeError"},
        CheckRequirementsParams{"business", "corp", {"corp"}, 1, 1, 0, 6, ""},
        CheckRequirementsParams{"business",
                                "corp",
                                {"corp"},
                                1,
                                0,
                                0,
                                6,
                                "UnsupportedPaymentTypeCorp"},
        CheckRequirementsParams{"econom",
                                "corp",
                                {"corp"},
                                0,
                                1,
                                0,
                                5,
                                "TariffIsRestrictedError"}), );
