#include "classification/models/classifier.hpp"

#include <chrono>
#include <string>
#include <unordered_set>

#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

const std::string kToyota = "Toyota";
const std::string kPrius = "Prius";

const std::string kHyundai = "Hyundai";
const std::string kI35 = "i35";

const std::string kAudi = "Audi";
const std::string kA6 = "A6";

const std::string kVaz = "Vaz";
const std::string kKalina = "Kalina";

const auto kDefaultFirstOrderDate = utils::datetime::Epoch();

using namespace std::chrono_literals;

inline std::string MakeBrandModel(const std::string& brand,
                                  const std::string& model) {
  return brand + " " + model;
}

UTEST(Classifier, Empty) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};
  classification::models::Classifier c;
  EXPECT_EQ(c.Classify(MakeBrandModel(kToyota, kPrius), 10, 200000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
}

UTEST(Classifier, HyundaiI35) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};

  classification::models::ClassificationRule rule;
  rule.is_allowing = false;
  rule.class_index = class_id;
  rule.price_to = 500'000;
  rule.year_to = 2010;

  classification::models::Classifier c;
  c.AddRule(rule);

  EXPECT_EQ(c.Classify(MakeBrandModel(kHyundai, kI35), 2009, 800'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kHyundai, kI35), 2011, 400'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);

  EXPECT_EQ(c.Classify(MakeBrandModel(kHyundai, kI35), 2010, 500'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kHyundai, kI35), 2008, 400'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
}

UTEST(Classifier, BrandModelFilter) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};

  classification::models::ClassificationRule rule;
  rule.is_allowing = true;
  rule.class_index = class_id;
  rule.brand = kAudi;
  rule.model = kA6;
  rule.year_from = 2015;

  classification::models::Classifier c;
  c.AddRule(rule);
  c.AddTariff("econom", false);

  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2014, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2016, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2020, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2008, 200'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kToyota, kPrius), 2010, 200'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
}

UTEST(Classifier, PriceCut) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};
  classification::models::Classifier c;

  classification::models::ClassificationRule rule1, rule2;
  rule1.is_allowing = true;
  rule1.class_index = class_id;
  rule1.brand = kAudi;
  rule1.model = kA6;
  rule1.year_from = 2016;

  rule2.is_allowing = false;
  rule2.class_index = class_id;
  rule2.price_to = 1'000'000;
  rule2.year_from = 2020;

  c.AddRule(rule1);
  c.AddRule(rule2);

  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2015, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2021, 900'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kToyota, kPrius), 2015, 200'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
}

UTEST(Classifier, AllowingTariff) {
  namespace cm = classification::models;

  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};
  classification::models::Classifier c;
  classification::models::ClassificationRule rule1, rule2, rule3, rule4;

  rule1.is_allowing = true;
  rule1.class_index = class_id;
  rule1.brand = kAudi;
  rule1.model = kA6;
  rule1.year_from = 2010;
  rule1.started_at = utils::datetime::Now() - 10min;

  rule2.is_allowing = false;
  rule2.class_index = class_id;
  rule2.price_from = 10'000'000;

  rule3.is_allowing = false;
  rule3.class_index = class_id;
  rule3.year_from = 1967;

  rule4.is_allowing = false;
  rule4.class_index = class_id;
  rule4.price_to = 5'000'000;

  c.AddRule(rule4);
  c.AddRule(rule1);
  c.AddRule(rule2);
  c.AddRule(rule3);

  c.AddTariff("econom", true);

  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2018, 6'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  const auto& reject_info =
      c.GetRejectInfo(MakeBrandModel(kAudi, kA6), 2018, 6'000'000,
                      kDefaultFirstOrderDate, required_classes);
  EXPECT_EQ(reject_info.size(), 1);
  cm::TariffsRejectInfo expected_reject_info;
  {
    cm::TariffRejectReasons reject;
    reject.tariff_id = class_id;
    reject.reasons = {};

    expected_reject_info = {reject};
  }

  EXPECT_EQ(reject_info, expected_reject_info);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2005, 7'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 1945, 20'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 1945, 3'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
}

UTEST(Classifier, NotAllowingTariff) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};
  classification::models::Classifier c;
  classification::models::ClassificationRule rule1, rule2, rule3, rule4;

  rule1.is_allowing = true;
  rule1.class_index = class_id;
  rule1.brand = kAudi;
  rule1.model = kA6;
  rule1.year_from = 2010;
  rule1.started_at = utils::datetime::Now() - 10min;

  rule2.is_allowing = true;
  rule2.class_index = class_id;
  rule2.price_from = 10'000'000;

  rule3.is_allowing = false;
  rule3.class_index = class_id;
  rule3.year_from = 1967;

  rule4.is_allowing = true;
  rule4.class_index = class_id;
  rule4.price_to = 5'000'000;

  c.AddRule(rule1);
  c.AddRule(rule2);
  c.AddRule(rule3);
  c.AddRule(rule4);

  c.AddTariff("econom", false);

  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2018, 6'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2005, 7'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{});
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 1945, 20'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 1945, 5'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
}

UTEST(Classifier, InactiveRules) {
  const auto class_id = ::models::ClassesMapper::Parse("econom");
  const auto required_classes = ::models::Classes{class_id};
  classification::models::Classifier c;

  classification::models::ClassificationRule rule1, rule2;
  rule1.is_allowing = false;
  rule1.class_index = class_id;
  rule1.year_from = 0;
  rule1.started_at = utils::datetime::Now() + 10min;

  rule2.is_allowing = false;
  rule2.class_index = class_id;
  rule2.price_from = 0;
  rule2.ended_at = utils::datetime::Now() - 10min;

  c.AddRule(rule1);
  c.AddRule(rule2);

  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2015, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2010, 1'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2021, 800'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
  EXPECT_EQ(c.Classify(MakeBrandModel(kToyota, kPrius), 2020, 200'000,
                       kDefaultFirstOrderDate, required_classes),
            required_classes);
}

UTEST(Classifier, SeveralTariffs) {
  namespace cm = classification::models;

  const auto vip_idx = ::models::ClassesMapper::Parse("vip"),
             econom_idx = ::models::ClassesMapper::Parse("econom"),
             business_idx = ::models::ClassesMapper::Parse("business"),
             child_idx = ::models::ClassesMapper::Parse("child");
  const auto required_classes =
      ::models::Classes{vip_idx, econom_idx, business_idx, child_idx};

  cm::Classifier c;

  cm::ClassificationRule econom_rule, business_rule, child_rule_1, child_rule_2;
  econom_rule.is_allowing = false;
  econom_rule.class_index = econom_idx;
  econom_rule.year_from = 2010;
  c.AddTariff("econom", true);

  business_rule.is_allowing = false;
  business_rule.class_index = business_idx;
  business_rule.price_from = 1'000'000;
  c.AddTariff("business", true);

  child_rule_1.is_allowing = true;
  child_rule_1.class_index = child_idx;
  child_rule_1.brand = kVaz;
  child_rule_1.model = kKalina;

  child_rule_2.is_allowing = false;
  child_rule_2.class_index = child_idx;
  child_rule_2.brand = kHyundai;
  child_rule_2.model = kI35;
  child_rule_2.price_from = 1000;
  child_rule_2.year_to = 2020;

  c.AddTariff("child", false);
  c.AddTariff("vip", false);

  c.AddRule(econom_rule);
  c.AddRule(business_rule);
  c.AddRule(child_rule_1);
  c.AddRule(child_rule_2);

  // Case 1
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{business_idx});
  const auto& reject_info_1 =
      c.GetRejectInfo(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                      kDefaultFirstOrderDate, ::models::Classes{vip_idx});
  cm::TariffsRejectInfo expected_reject_info_1;
  {
    cm::TariffRejectReasons vip_reject;
    vip_reject.tariff_id = vip_idx;
    vip_reject.reasons = {cm::RejectReason::kTariffNotAllowing};

    expected_reject_info_1.push_back(vip_reject);
  }
  EXPECT_EQ(reject_info_1, expected_reject_info_1);

  // Case 2
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2008, 2'000'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes{econom_idx});
  const auto& reject_info_2 = c.GetRejectInfo(
      MakeBrandModel(kAudi, kA6), 2008, 2'000'000, kDefaultFirstOrderDate,
      ::models::Classes{child_idx, business_idx});
  EXPECT_EQ(reject_info_2.size(), 2);
  cm::TariffsRejectInfo expected_reject_info_2;
  {
    cm::TariffRejectReasons child_reject;
    child_reject.tariff_id = child_idx;
    child_reject.reasons = {cm::RejectReason::kTariffNotAllowing};

    cm::TariffRejectReasons business_reject;
    business_reject.tariff_id = business_idx;
    business_reject.reasons = {cm::RejectReason::kPrice};

    expected_reject_info_2 = {business_reject, child_reject};
  }
  EXPECT_EQ(reject_info_2, expected_reject_info_2);

  // Case 3
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2008, 1'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes({econom_idx, business_idx}));
  const auto& reject_info_3 = c.GetRejectInfo(
      MakeBrandModel(kAudi, kA6), 2008, 1'000, kDefaultFirstOrderDate,
      ::models::Classes{child_idx, vip_idx});
  EXPECT_EQ(reject_info_3.size(), 2);
  cm::TariffsRejectInfo expected_reject_info_3;
  {
    cm::TariffRejectReasons child_reject;
    child_reject.tariff_id = child_idx;
    child_reject.reasons = {cm::RejectReason::kTariffNotAllowing};

    cm::TariffRejectReasons vip_reject;
    vip_reject.tariff_id = vip_idx;
    vip_reject.reasons = {cm::RejectReason::kTariffNotAllowing};

    expected_reject_info_3 = {vip_reject, child_reject};
  }
  EXPECT_EQ(reject_info_3, expected_reject_info_3);

  // Case 4
  EXPECT_EQ(c.Classify(MakeBrandModel(kVaz, kKalina), 2008, 1'000,
                       kDefaultFirstOrderDate, required_classes),
            ::models::Classes({econom_idx, business_idx, child_idx}));
  const auto& reject_info_4 =
      c.GetRejectInfo(MakeBrandModel(kVaz, kKalina), 2008, 1'000,
                      kDefaultFirstOrderDate, ::models::Classes{child_idx});
  EXPECT_EQ(reject_info_4.size(), 1);
  cm::TariffsRejectInfo expected_reject_info_4;
  {
    cm::TariffRejectReasons child_reject;
    child_reject.tariff_id = child_idx;
    child_reject.reasons = {};

    expected_reject_info_4 = {child_reject};
  }
  EXPECT_EQ(reject_info_4, expected_reject_info_4);

  // Case 5
  EXPECT_EQ(c.Classify(MakeBrandModel(kHyundai, kI35), 2015, 2'000,
                       kDefaultFirstOrderDate, ::models::Classes{child_idx}),
            ::models::Classes{});
  const auto& reject_info_5 =
      c.GetRejectInfo(MakeBrandModel(kHyundai, kI35), 2015, 2'000,
                      kDefaultFirstOrderDate, ::models::Classes{child_idx});
  EXPECT_EQ(reject_info_5.size(), 1);
  cm::TariffsRejectInfo expected_reject_info_5;
  {
    cm::TariffRejectReasons child_reject;
    child_reject.tariff_id = child_idx;
    child_reject.reasons = {cm::RejectReason::kPrice,
                            cm::RejectReason::kManufactureYear,
                            cm::RejectReason::kBrandModel};

    expected_reject_info_5 = {child_reject};
  }
  EXPECT_EQ(reject_info_5, expected_reject_info_5);
}

UTEST(Classifier, VehicleBeforeFilter) {
  namespace cm = classification::models;

  const auto vip_idx = ::models::ClassesMapper::Parse("vip"),
             econom_idx = ::models::ClassesMapper::Parse("econom"),
             child_idx = ::models::ClassesMapper::Parse("child");
  // const auto required_classes =
  //     ::models::Classes{vip_idx, econom_idx, child_idx};
  cm::Classifier c;

  cm::ClassificationRule econom_rule, vip_rule, child_rule;

  econom_rule.is_allowing = false;
  econom_rule.class_index = econom_idx;
  econom_rule.vehicle_before = utils::datetime::Now() + 48h;
  c.AddRule(econom_rule);
  c.AddTariff("econom", true);

  vip_rule.is_allowing = false;
  vip_rule.class_index = vip_idx;
  vip_rule.vehicle_before = utils::datetime::Now() - 48h;
  c.AddRule(vip_rule);
  c.AddTariff("vip", true);

  child_rule.is_allowing = true;
  child_rule.class_index = child_idx;
  child_rule.vehicle_before = utils::datetime::Now() - 23h;
  c.AddRule(child_rule);
  c.AddTariff("child", false);

  // Case econom
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                       utils::datetime::Now(), ::models::Classes{econom_idx}),
            ::models::Classes{});
  const auto& reject_info_1 =
      c.GetRejectInfo(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                      utils::datetime::Now(), ::models::Classes{econom_idx});
  cm::TariffsRejectInfo expected_reject_info_1;
  {
    cm::TariffRejectReasons econom_reject;
    econom_reject.tariff_id = econom_idx;
    econom_reject.reasons = {cm::RejectReason::kVehicleBefore};

    expected_reject_info_1.push_back(econom_reject);
  }
  EXPECT_EQ(reject_info_1, expected_reject_info_1);

  // Case vip
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                       utils::datetime::Now(), ::models::Classes{vip_idx}),
            ::models::Classes{vip_idx});
  const auto& reject_info_2 =
      c.GetRejectInfo(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                      utils::datetime::Now(), ::models::Classes{vip_idx});
  cm::TariffsRejectInfo expected_reject_info_2;
  {
    cm::TariffRejectReasons vip_reject;
    vip_reject.tariff_id = vip_idx;
    vip_reject.reasons = {};

    expected_reject_info_2.push_back(vip_reject);
  }
  EXPECT_EQ(reject_info_2, expected_reject_info_2);

  // Case child
  EXPECT_EQ(c.Classify(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                       utils::datetime::Now(), ::models::Classes{child_idx}),
            ::models::Classes{child_idx});
  const auto& reject_info_3 =
      c.GetRejectInfo(MakeBrandModel(kAudi, kA6), 2017, 800'000,
                      utils::datetime::Now(), ::models::Classes{child_idx});
  cm::TariffsRejectInfo expected_reject_info_3;
  {
    cm::TariffRejectReasons child_reject;
    child_reject.tariff_id = child_idx;
    child_reject.reasons = {};

    expected_reject_info_3.push_back(child_reject);
  }
  EXPECT_EQ(reject_info_3, expected_reject_info_3);
}

UTEST(Classifier, ClassifierAllowingPolicy) {
  namespace cm = classification::models;

  const auto vip_idx = ::models::ClassesMapper::Parse("vip"),
             econom_idx = ::models::ClassesMapper::Parse("econom"),
             child_idx = ::models::ClassesMapper::Parse("child");

  const auto required_classes =
      ::models::Classes{vip_idx, econom_idx, child_idx};

  // allowing classifier check
  classification::models::Classifier allowing_classifier;
  allowing_classifier.SetAllowingPolicy(true);

  EXPECT_EQ(allowing_classifier.Classify(MakeBrandModel(kAudi, kA6), 2018,
                                         6'000'000, {}, required_classes),
            required_classes);

  allowing_classifier.AddTariff("vip", false);
  allowing_classifier.AddTariff("econom", false);

  EXPECT_EQ(allowing_classifier.Classify(MakeBrandModel(kAudi, kA6), 2018,
                                         6'000'000, {}, required_classes),
            ::models::Classes({child_idx}));

  // not allowing classifier check
  classification::models::Classifier not_allowing_classifier;
  not_allowing_classifier.SetAllowingPolicy(false);
  EXPECT_EQ(not_allowing_classifier.Classify(MakeBrandModel(kAudi, kA6), 2018,
                                             6'000'000, {}, required_classes),
            ::models::Classes{});

  not_allowing_classifier.AddTariff("vip", true);
  not_allowing_classifier.AddTariff("econom", true);

  EXPECT_EQ(not_allowing_classifier.Classify(MakeBrandModel(kAudi, kA6), 2018,
                                             6'000'000, {}, required_classes),
            ::models::Classes({vip_idx, econom_idx}));
}
