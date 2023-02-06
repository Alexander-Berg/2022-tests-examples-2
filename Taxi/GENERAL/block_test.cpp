#include "block.hpp"

#include <string>

#include <gtest/gtest.h>

namespace eats_catalog::models {

namespace {

namespace impl {

auto SetRatingValue(double rating) {
  return [rating](models::PlaceInfo& info) { info.rating.value = rating; };
}

template <typename... Args>
models::PlaceInfo CreatePlaceInfo(Args... args) {
  models::PlaceInfo info{};
  info.id = PlaceId{1};
  info.business = eats_shared::Business::kRestaurant;
  info.delivery_type = eats_places::models::DeliveryType::kNative;

  (args(info), ...);

  return info;
}

}  // namespace impl

using PredicateSource = handlers::libraries::eats_catalog_predicate::Predicate;
using ValueTypeSource = handlers::libraries::eats_catalog_predicate::ValueType;
using handlers::libraries::eats_catalog_predicate::Argument;
using handlers::libraries::eats_catalog_predicate::PredicateInit;
using handlers::libraries::eats_catalog_predicate::PredicateType;

struct ArgsTestCase {
  std::string name;
  PlaceInfo place_info;
  PredicateSource predicate;
  bool expected;
};

class ArgsTest : public ::testing::TestWithParam<ArgsTestCase> {};

std::vector<ArgsTestCase> CreateArgsTestCases() {
  return {
      {
          "rating > 4 == false",                           // name
          impl::CreatePlaceInfo(impl::SetRatingValue(3)),  // place
          PredicateSource{
              PredicateType::kGt,  // type
              PredicateInit{
                  Argument::kRating,         // arg_name
                  ValueTypeSource::kDouble,  // arg_type
                  4.0,                       // value
              },                             // init
          },                                 // predicate
          false,                             //
      },
      {
          "rating > 4 == true",                              // name
          impl::CreatePlaceInfo(impl::SetRatingValue(4.1)),  // place
          PredicateSource{
              PredicateType::kGt,  // type
              PredicateInit{
                  Argument::kRating,         // arg_name
                  ValueTypeSource::kDouble,  // arg_type
                  4.0,                       // value
              },                             // init
          },                                 // predicate
          true,                              //
      },
  };
}

}  // namespace

TEST_P(ArgsTest, Test) {
  const auto param = GetParam();

  const auto info = param.place_info;
  const Place place(info);
  const auto actual = expression::Eval(param.predicate, Args(place, {}));
  ASSERT_EQ(param.expected, actual) << param.name;
}

INSTANTIATE_TEST_SUITE_P(ArgsTest, ArgsTest,
                         ::testing::ValuesIn(CreateArgsTestCases()));

}  // namespace eats_catalog::models
