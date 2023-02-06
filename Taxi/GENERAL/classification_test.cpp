#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "classification/classification.hpp"

#include <classification/models/classifier.hpp>
#include <classification/models/classifier_exceptions.hpp>
#include <classification/models/vehicle.hpp>
#include <classification/models/vehicles_first_order_date.hpp>
#include <models/classes.hpp>

class ClassifyTest : public ::testing::Test {
 public:
  ClassifyTest() {
    moscow_zone_id_ = "moscow";
    mozhaysk_zone_id_ = "mozhaysk";

    classifier_allowing_econom_.SetAllowingPolicy(false);
    classifier_allowing_econom_.AddTariff("econom", true);

    vehicle_.manufacture_year = 0;
    vehicle_.brand_model = "";
    vehicle_.price = 1000000;
    vehicle_.raw_number =
        reinterpret_cast<const char*>(u8"АА99");  // cyrillic L'A'
    vehicle_.number_normalized = "AA99";          // latin 'A'

    classifier_exceptions_[{vehicle_.number_normalized, "*"}] =
        models::Classes{"business"};
    classifier_exceptions_[{vehicle_.number_normalized, mozhaysk_zone_id_}] =
        models::Classes{"comfortplus", "vip"};
  }

  classification::models::Classifier classifier_allowing_econom_;
  classification::models::ClassifierExceptionsMap classifier_exceptions_;
  std::string every_zone_id_;
  std::string moscow_zone_id_;
  std::string mozhaysk_zone_id_;

  classification::models::Vehicle empty_vehicle_;
  classification::models::VehiclesFirstOrderDateMap
      empty_vehicles_first_order_date_;
  classification::models::ClassifierExceptionsMap empty_classifier_exceptions_;
  classification::models::Vehicle vehicle_;
};

UTEST_F(ClassifyTest, NoClassifier) {
  models::Classes required_classes{"vip", "business", "comfortplus"};
  const models::Classes expected{"vip", "business", "comfortplus"};
  const auto actual = classification::Classify(
      required_classes, empty_vehicle_, every_zone_id_,
      empty_vehicles_first_order_date_, empty_classifier_exceptions_, nullptr);

  EXPECT_EQ(expected, actual);
}

UTEST_F(ClassifyTest, Clamping) {
  models::Classes required_classes{"econom"};
  const models::Classes expected{"econom"};
  const auto actual = classification::Classify(
      required_classes, vehicle_, mozhaysk_zone_id_,
      empty_vehicles_first_order_date_, classifier_exceptions_,
      &classifier_allowing_econom_);

  EXPECT_EQ(expected, actual);
}

UTEST_F(ClassifyTest, MoscowZone) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes expected{"econom", "business"};
  const auto actual = classification::Classify(
      required_classes, vehicle_, moscow_zone_id_,
      empty_vehicles_first_order_date_, classifier_exceptions_,
      &classifier_allowing_econom_);

  EXPECT_EQ(expected, actual);
}

UTEST_F(ClassifyTest, MozhayskZone) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes expected{"econom", "business", "comfortplus", "vip"};

  const auto actual = classification::Classify(
      required_classes, vehicle_, mozhaysk_zone_id_,
      empty_vehicles_first_order_date_, classifier_exceptions_,
      &classifier_allowing_econom_);

  EXPECT_EQ(expected, actual);
}

UTEST_F(ClassifyTest, ClassifyWithoutWhiteList) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes expected{"econom"};

  const auto actual = classification::Classify(
      required_classes, vehicle_, mozhaysk_zone_id_,
      empty_vehicles_first_order_date_, empty_classifier_exceptions_,
      &classifier_allowing_econom_);

  EXPECT_EQ(expected, actual);
}

UTEST_F(ClassifyTest, kWrongVehicleNumber) {
  models::Classes required_classes{"econom", "vip", "business", "comfortplus"};
  const models::Classes expected{"econom"};

  auto vehicle_with_wrong_number = vehicle_;
  // set raw_number instead of normalized
  vehicle_with_wrong_number.number_normalized =
      vehicle_with_wrong_number.raw_number;

  const auto actual = classification::Classify(
      required_classes, vehicle_with_wrong_number, mozhaysk_zone_id_,
      empty_vehicles_first_order_date_, classifier_exceptions_,
      &classifier_allowing_econom_);

  EXPECT_EQ(expected, actual);
}
