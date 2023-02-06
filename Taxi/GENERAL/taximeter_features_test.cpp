#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <taximeter-version-settings/taximeter_features.hpp>

namespace {

const auto kConfig = R"(
{
  "__default__": {
    "current": "9.24",
    "disabled": [
    ],
    "feature_support": {
      "activity_reuse_order_details": "8.92",
      "cargo_ref_id": "9.28",
      "chair_categories": "8.55",
      "chair_requirements_fix": "9.07",
      "corp_order": "8.47",
      "driver_support_zendesk": "9.25",
      "fix_driver_waiting_costs": "8.78",
      "gzip_push": "9.99",
      "hold_subventions": "8.43",
      "json_geoareas": "8.30",
      "login_driver_fix": "9.27",
      "loyalty": "8.91",
      "loyalty_cards": "8.93",
      "loyalty_cards_buttons": "9.26",
      "loyalty_history": "9.30",
      "nmfg_ctor": "9.06",
      "pool": "8.43",
      "qc_default": "8.30",
      "qc_identity": "9.12",
      "qc_push": "8.52",
      "reposition_v2_in_polling_order": "9.28",
      "request_confirm_disable_translate_status": "8.00",
      "selfemployed_referral": "8.91",
      "selfreg_onfoot_flow": "9.32",
      "selfreg_self_employment": "9.99",
      "service_push_types": "8.40",
      "subvention": "8.33",
      "taximeter_waiting_in_transporting": "8.75",
      "taximeter_xs": "9.00",
      "warning_icon": "9.06"
    },
    "min": "9.24"
  },
  "taximeter-az": {
    "current": "9.11",
    "min": "9.11"
  },
  "taximeter-ios": {
    "current": "1.00",
    "disabled": [
    ],
    "feature_support": {
      "activity_reuse_order_details": "1.00",
      "cargo_ref_id": "1.00",
      "chair_categories": "1.00",
      "chair_requirements_fix": "1.00",
      "complete_request_polling": "1.00",
      "corp_order": "1.00",
      "correct_dashboard_dates_from_front": "1.00",
      "driver_support_zendesk": "1.00",
      "gzip_push": "1.00",
      "hold_subventions": "1.00",
      "json_geoareas": "1.00",
      "login_driver_fix": "1.00",
      "login_polling_state": "1.00",
      "loyalty": "1.00",
      "loyalty_cards": "1.00",
      "loyalty_cards_buttons": "1.00",
      "loyalty_history": "1.00",
      "nmfg_ctor": "1.00",
      "pool": "1.00",
      "push_order_change_payment": "1.00",
      "qc_default": "1.00",
      "qc_identity": "1.00",
      "qc_sts": "1.00",
      "reposition_v2_in_polling_order": "1.00",
      "request_confirm_disable_translate_status": "1.00",
      "selfemployed_referral": "1.00",
      "selfreg_self_employment": "9.99",
      "selfreg_undefined_color": "9.99",
      "service_push_types": "1.00",
      "subvention": "1.00",
      "taximeter_waiting_in_transporting": "1.00",
      "taximeter_xs": "1.00",
      "topics": "1.00",
      "warning_icon": "1.00"
    },
    "min": "1.00"
  },
  "taximeter-sdc": {
    "current": "9.00",
    "min": "9.00"
  },
  "taximeter-uber": {
    "current": "9.17",
    "min": "9.17"
  },
  "taximeter-x": {
    "current": "9.25",
    "min": "9.25"
  },
  "taximeter-yango": {
    "current": "9.11",
    "min": "9.11"
  }
}
)";

}  // namespace

TEST(TaximeterVersionSettings, FeatureSupport) {
  const auto features_config =
      formats::json::FromString(kConfig).As<config::TaximeterFeatures>();
  EXPECT_EQ(
      features_config.GetFeaturesIds(
          {"activity_reuse_order_details", "cargo_ref_id", "chair_categories",
           "qc_push", "fix_driver_waiting_costs", "selfreg_onfoot_flow"}),
      config::TaximeterFeatures::FeaturesIds({0, 1, 2, 19, 6, 23}));

  EXPECT_EQ(features_config.GetFeaturesIds(
                ua_parser::TaximeterApp::FromUserAgent("taximeter 2.02 ios")),
            features_config.GetFeaturesIds(
                {"activity_reuse_order_details",
                 "cargo_ref_id",
                 "chair_categories",
                 "chair_requirements_fix",
                 "complete_request_polling",
                 "corp_order",
                 "correct_dashboard_dates_from_front",
                 "driver_support_zendesk",
                 "gzip_push",
                 "hold_subventions",
                 "json_geoareas",
                 "login_driver_fix",
                 "login_polling_state",
                 "loyalty",
                 "loyalty_cards",
                 "loyalty_cards_buttons",
                 "loyalty_history",
                 "nmfg_ctor",
                 "pool",
                 "push_order_change_payment",
                 "qc_default",
                 "qc_identity",
                 "qc_sts",
                 "reposition_v2_in_polling_order",
                 "request_confirm_disable_translate_status",
                 "selfemployed_referral",
                 "service_push_types",
                 "subvention",
                 "taximeter_waiting_in_transporting",
                 "taximeter_xs",
                 "topics",
                 "warning_icon"}));
}
