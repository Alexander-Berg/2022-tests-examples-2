#include "classify.hpp"

#include <iostream>

#include <gtest/gtest.h>

#include <models/classes.hpp>
#include <models/dispatch/classifier.hpp>
#include <models/driver/car.hpp>
#include <models/driver/profile.hpp>

// models::dispatch::Classifier is not tested here.
// It is empty, thus allowing everything.
// These test cases is mostly for whitelists.

namespace models {
void PrintTo(const Classes& classes, ::std::ostream* os) {
  for (ClassType i = 0; i < Classes::kCount; ++i) {
    *os << (classes.Provides(i) ? '1' : '0') << ' ';
  }
}
}  // namespace models

class ClassifyTest : public ::testing::Test {
 public:
 protected:
  void SetUp() {
    static const std::array<models::ClassType, 6> deny_classes = {{
        models::Classes::Unknown,
        models::Classes::Express,
        models::Classes::Business,
        models::Classes::ComfortPlus,
        models::Classes::Vip,
        models::Classes::Minivan,
    }};
    for (auto ct : deny_classes) {
      classifier_allowing_econom_.AddRule(models::dispatch::ClassificationRule{
          ct, false, std::string(), boost::optional<uint32_t>(10000000), 0});
    }
    profile_with_whitelist_.years = 0;
    profile_with_whitelist_.model = "";
    profile_with_whitelist_.price = 1000000;

    car_with_whitelist_.manually_assigned_classes["*"] =
        models::Classes{"business"};
    car_with_whitelist_.manually_assigned_classes["mozhaysk"] =
        models::Classes{"comfortplus", "vip"};

    moscow_zone_id_ = "moscow";
    mozhaysk_zone_id_ = "mozhaysk";
  }

  boost::optional<const models::dispatch::Classifier&> empty_classifier_;
  models::dispatch::Classifier classifier_allowing_econom_;
  boost::optional<std::string> empty_zone_id_;
  boost::optional<std::string> moscow_zone_id_;
  boost::optional<std::string> mozhaysk_zone_id_;

  models::driver::ProfileCar empty_profile_car_;
  models::driver::Car empty_car_;

  models::driver::ProfileCar profile_with_whitelist_;
  models::driver::Car car_with_whitelist_;
};

TEST_F(ClassifyTest, NoClassifier) {
  // For missing models::dispatch::Classifier classification result is required
  // classes with classes by grade mask.
  models::Classes required_classes{"vip", "business", "comfortplus"};
  models::Classes classes_by_grade{"econom", "business"};
  const models::Classes expected{"business"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, empty_classifier_, empty_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, NoZone) {
  // models::dispatch::Classifier is set, car is whitelisted, but zone is not
  // set.
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes& classes_by_grade = required_classes;
  const models::Classes expected{"econom", "business"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, profile_with_whitelist_,
      car_with_whitelist_, nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      empty_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, Clamping) {
  // Though car supports more classes, only subset of requested
  // should be returned.
  models::Classes required_classes{"econom"};
  const models::Classes& classes_by_grade = required_classes;
  const models::Classes expected{"econom"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, profile_with_whitelist_,
      car_with_whitelist_, nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, EveryZone) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes& classes_by_grade = required_classes;
  const models::Classes expected{"econom", "business"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, profile_with_whitelist_,
      car_with_whitelist_, nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      moscow_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, MatchingZone) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes& classes_by_grade = required_classes;
  const models::Classes expected{"econom", "business", "comfortplus", "vip"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, profile_with_whitelist_,
      car_with_whitelist_, nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, ClassesByGradeAreMoreImportant) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes classes_by_grade{"business"};
  const models::Classes expected{"business"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, profile_with_whitelist_,
      car_with_whitelist_, nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, ClassifyCarWithoutWhiteList) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes& classes_by_grade = required_classes;
  const models::Classes expected{"econom"};
  const auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr,
      boost::optional<const models::dispatch::Classifier&>(
          classifier_allowing_econom_),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, ClassifyWithoutEconom) {
  models::dispatch::Classifier classifier;
  classifier.AddRule(models::dispatch::ClassificationRule{
      models::Classes::Econom, false, std::string(),
      boost::optional<uint32_t>(10000000), 0});

  models::Classes required_classes{"econom"};
  const models::Classes& classes_by_grade = required_classes;
  auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  const models::Classes expected{};
  EXPECT_EQ(expected, actual);

  required_classes = {"pool"};
  actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, ClassifyRejectPool) {
  models::dispatch::Classifier classifier;
  classifier.AddRule(models::dispatch::ClassificationRule{
      models::Classes::Econom, false, "0", boost::optional<uint32_t>(10000000),
      0});

  models::Classes required_classes{"pool"};
  const models::Classes& classes_by_grade = required_classes;
  auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  const models::Classes expected{};
  EXPECT_EQ(expected, actual);

  required_classes = {"pool", "econom"};
  actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(expected, actual);
}

TEST_F(ClassifyTest, ClassifyAllowPool) {
  models::dispatch::Classifier classifier;
  classifier.AddRule(models::dispatch::ClassificationRule{
      models::Classes::Econom, true, "0", boost::optional<uint32_t>(1000000),
      5});

  models::Classes required_classes{"econom"};
  const models::Classes& classes_by_grade = required_classes;
  auto actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  const models::Classes expected{};
  EXPECT_EQ(required_classes, actual);

  required_classes = {"pool"};
  actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(required_classes, actual);

  required_classes = {"pool", "econom"};
  actual = dispatch::kit::Classify(
      required_classes, classes_by_grade, empty_profile_car_, empty_car_,
      nullptr, boost::optional<const models::dispatch::Classifier&>(classifier),
      mozhaysk_zone_id_, boost::none);

  EXPECT_EQ(required_classes, actual);
}
