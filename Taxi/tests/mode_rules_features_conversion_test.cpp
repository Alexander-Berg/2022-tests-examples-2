#include <userver/utest/utest.hpp>

#include <models/features/feature.hpp>
#include <models/features/set.hpp>

namespace {

const auto all_features_count =
    defs::internal::features::kFeatureNameValues.size();

models::features::WorkModeFeatures GetAllFeatures() {
  models::features::WorkModeFeatures all_work_mode_features;
  for (const auto& feature : defs::internal::features::kFeatureNameValues) {
    switch (feature) {
      case models::FeatureType::kActiveTransport:
        all_work_mode_features.active_transport.emplace();
        break;
      case models::FeatureType::kDriverFix:
        all_work_mode_features.driver_fix.emplace();
        break;
      case models::FeatureType::kReposition:
        all_work_mode_features.reposition.emplace();
        break;
      case models::FeatureType::kTags:
        all_work_mode_features.tags.emplace();
        break;
      case models::FeatureType::kGeobooking:
        all_work_mode_features.geobooking.emplace();
        break;
      case models::FeatureType::kBooking:
        all_work_mode_features.booking.emplace();
        break;
      case models::FeatureType::kLogisticWorkshifts:
        all_work_mode_features.logistic_workshifts.emplace();
        break;
    }
  }
  return all_work_mode_features;
}

}  // namespace

// TODO: find way to do this tests at compile time, may be refactor
// models::features::WorkModeFeatures to more complex container

TEST(ModeRulesFeatureConversion, ToAndFromFeaturesVec) {
  const auto all_work_mode_features = GetAllFeatures();
  // Check ToFeaturesOptVec
  const auto all_features_vec = ToFeaturesOptVec(all_work_mode_features);

  ASSERT_EQ(all_features_vec.has_value(), true);
  ASSERT_EQ(all_features_vec->size(), all_features_count);
  // Check FromFeaturesVecOpt
  auto all_work_mode_features_converted =
      models::features::FromFeaturesVecOpt(all_features_vec);
  const auto all_features_vec_converted =
      ToFeaturesOptVec(all_work_mode_features_converted);

  ASSERT_EQ(all_features_vec_converted, all_features_vec);
}

TEST(ModeRulesFeatureConversion, GetNames) {
  models::features::NamesSet expected_feature_names;
  for (const auto& feature : defs::internal::features::kFeatureNameValues) {
    expected_feature_names.insert(models::FeatureName{ToString(feature)});
  }
  // Check GetNames
  const auto all_feature_names = GetNames(GetAllFeatures());

  ASSERT_EQ(all_feature_names, expected_feature_names);
}

TEST(ModeRulesFeatureConversion, GetModeFeatures) {
  auto expected_mode_features_vec = std::vector<models::FeatureType>(
      defs::internal::features::kFeatureNameValues.begin(),
      defs::internal::features::kFeatureNameValues.end());
  std::sort(expected_mode_features_vec.begin(),
            expected_mode_features_vec.end());
  // Check GetModeFeatures
  auto all_mode_features = GetModeFeatures(GetAllFeatures());

  std::sort(all_mode_features.begin(), all_mode_features.end());

  ASSERT_EQ(expected_mode_features_vec, all_mode_features);
}
