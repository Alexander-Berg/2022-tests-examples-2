#include <gtest/gtest.h>

#include <string>

#include <ml/common/datetime.hpp>
#include <ml/surge_notify/v1/features.hpp>
#include <ml/surge_notify/v1/objects.hpp>

#include "common/utils.hpp"

ml::surge_notify::v1::Request GetFullRequest() {
  ml::surge_notify::v1::Request req;
  req.nz = "moscow";
  req.time = "2018-05-14T20:09:43.66744+0300";
  req.surge_id = "aaa";
  req.route_points = {{55.735082, 37.642662}};
  req.currency = "FORINT";

  ml::surge_notify::v1::Classesinfo econom_ci;
  econom_ci.surge_info.surge_value = 1.4;
  econom_ci.surge_info.surge_value_raw = 1.398;
  econom_ci.surge_info.surge_value_smooth = 1.38;
  econom_ci.surge_info.free = 10;
  econom_ci.surge_info.free_chain = 5;
  econom_ci.surge_info.pins = 100;
  econom_ci.surge_info.total = 200;
  econom_ci.surge_info.radius = 2500;
  econom_ci.max_line_distance = 1000;
  econom_ci.max_time = 500;
  econom_ci.max_distance = 900;
  econom_ci.limit = 20;
  econom_ci.cost = 600;
  econom_ci.cost_original = 900;
  econom_ci.tariff_class = "econom";
  econom_ci.estimated_waiting = 450;

  req.classes_info.push_back(econom_ci);

  ml::surge_notify::v1::Classesinfo vip_ci;
  vip_ci.surge_info.surge_value = 1.1;
  vip_ci.surge_info.surge_value_raw = 1.098;
  vip_ci.surge_info.surge_value_smooth = 1.08;
  vip_ci.surge_info.free = 2;
  vip_ci.surge_info.free_chain = 1;
  vip_ci.surge_info.pins = 20;
  vip_ci.surge_info.total = 50;
  vip_ci.surge_info.radius = 2500;
  vip_ci.max_line_distance = 1000;
  vip_ci.max_time = 500;
  vip_ci.max_distance = 900;
  vip_ci.limit = 20;
  vip_ci.cost = 1600;
  vip_ci.cost_original = 1900;
  vip_ci.tariff_class = "vip";
  vip_ci.estimated_waiting = 900;

  req.classes_info.push_back(vip_ci);
  return req;
}

ml::surge_notify::v1::Resources GetResourses() {
  ml::surge_notify::v1::Resources result;

  result.apply_up =
      [](const std::vector<std::vector<double>>& num_feats,
         const std::vector<std::vector<std::string>>& /*cat_feats*/) {
        std::vector<double> result(num_feats.size(), 0.6);
        return result;
      };
  result.apply_down =
      [](const std::vector<std::vector<double>>& num_feats,
         const std::vector<std::vector<std::string>>& /*cat_feats*/) {
        std::vector<double> result(num_feats.size(), 0.4);
        return result;
      };
  result.get_threshold_up = [](double desired_precision) {
    ml::surge_notify::v1::ModelMetadata result = {0.5, 0.5, 0.5, 0.5};

    if (desired_precision >= 0.6) {
    }
    return result;
  };
  result.get_threshold_down = [](double /*desired_precision*/) {
    ml::surge_notify::v1::ModelMetadata result = {0.5, 0.5, 0.5, 0.5};
    return result;
  };
  return result;
}

void assert_double_list_eq(const std::vector<double> lhs,
                           std::vector<double> rhs) {
  ASSERT_EQ(lhs.size(), rhs.size());
  for (size_t i = 0; i < lhs.size(); ++i) {
    ASSERT_FLOAT_EQ(lhs[i], rhs[i]);
  }
}

TEST(Datetime, Datetime) {
  ASSERT_EQ(
      ml::common::datetime::StrToTimestamp("2018-05-14T20:09:43.66744+0300"),
      ml::common::datetime::StrToTimestamp("2018-05-14T20:09:43.66744+0000") -
          60 * 60 * 3);

  ASSERT_EQ(
      0,  // sunday
      ml::common::datetime::GetUTCWeekday(ml::common::datetime::StrToTimestamp(
          "2019-12-01T12:09:43.66744+0300")));

  ASSERT_EQ(
      0,  // sunday
      ml::common::datetime::GetUTCWeekday(ml::common::datetime::StrToTimestamp(
          "2019-12-01T00:09:43.66744+0000")));
}

TEST(SurgeNotifyFe, DatetimeFeats) {
  int timestamp = 10;
  std::vector<double> res = {1.6534392e-05, 0.33334985, 0.666683,
                             0.00011574074, 0.333449,   0.66678238};

  assert_double_list_eq(
      ml::surge_notify::v1::ExtractDatetimeFeatures(timestamp), res);
}

TEST(SurgeNotifyFe, full) {
  auto req = GetFullRequest();
  std::vector<std::string> tariff_classes = {"econom", "vip"};
  ml::surge_notify::v1::FeaturesStorage fe(req, tariff_classes);
  auto num_feats = fe.GetNumFeatures();
  for (const auto& fs : num_feats) {
    ASSERT_EQ(fs.size(),
              ml::surge_notify::v1::FeaturesStorage::kNumFeaturesCount);
  }
  for (const auto& fs : fe.GetCatFeatures()) {
    ASSERT_EQ(fs.size(),
              ml::surge_notify::v1::FeaturesStorage::kCatFeaturesCount);
  }
}

TEST(SurgeNotifyFe, empty_optional) {
  ml::surge_notify::v1::Request req;
  req.nz = "moscow";
  req.time = "2018-05-14T20:09:43.66744+0300";
  req.surge_id = "aaa";
  req.route_points = {{55.735082, 37.642662}};
  req.currency = "FORINT";

  ml::surge_notify::v1::Classesinfo econom_ci;
  econom_ci.tariff_class = "econom";

  req.classes_info.push_back(econom_ci);

  ml::surge_notify::v1::Classesinfo vip_ci;
  vip_ci.tariff_class = "vip";

  req.classes_info.push_back(vip_ci);

  std::vector<std::string> tariff_classes = {"econom", "vip"};
  ml::surge_notify::v1::FeaturesStorage fe(req, tariff_classes);
  auto num_feats = fe.GetNumFeatures();
  ml::surge_notify::v1::Resources resources;
  ml::surge_notify::v1::Predictor predictor(resources);
}

TEST(SurgeNotifyPredictor, simple_run) {
  auto req = GetFullRequest();
  auto resources = GetResourses();
  ml::surge_notify::v1::Predictor predictor(resources);
  ml::surge_notify::v1::FullApplyParams applyParams;
  applyParams.class_params_.insert({"econom", {0.7, 0.7}});

  applyParams.class_params_.insert({"vip", {0.7, 0.7}});
  auto verdicts = predictor.Apply(req, applyParams);
  ASSERT_EQ(verdicts.size(), 2ul);
  ASSERT_EQ(verdicts.front().expected_trend,
            ml::surge_notify::v1::Predictor::Verdict::SAME);
}

TEST(SurgeNotifyFE, datetime) {
  auto req = GetFullRequest();
  auto resources = GetResourses();
  ml::surge_notify::v1::Predictor predictor(resources);
  ml::surge_notify::v1::FullApplyParams applyParams;
  applyParams.class_params_.insert({"econom", {0.7, 0.7}});

  applyParams.class_params_.insert({"vip", {0.7, 0.7}});
  auto verdicts = predictor.Apply(req, applyParams);
  ASSERT_EQ(verdicts.size(), 2ul);
  ASSERT_EQ(verdicts.front().expected_trend,
            ml::surge_notify::v1::Predictor::Verdict::SAME);
}
