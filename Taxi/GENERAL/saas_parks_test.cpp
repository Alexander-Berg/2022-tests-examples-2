#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark.hpp>
#include <filters/partners/saas_parks/saas_parks.hpp>
#include <testing/taxi_config.hpp>

#include "saas_parks.hpp"

namespace cf = candidates::filters;

namespace {

struct TestCase {
  bool is_saas_park;
  bool is_getting_orders_from_app;
  formats::json::Value white_label_requirements;
  cf::Result expected_result;
  bool is_filter_created;
};

class SaasParksTestCase : public ::testing::TestWithParam<TestCase> {};

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

TEST_P(SaasParksTestCase, Filter) {
  const auto& test_case = GetParam();

  cf::partners::SaasParksFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter =
                      factory.Create(test_case.white_label_requirements, env));
  if (test_case.is_filter_created) {
    ASSERT_TRUE(filter);
  } else {
    ASSERT_FALSE(filter);
  }

  if (test_case.is_filter_created) {
    cf::Context context;
    auto park = std::make_shared<models::DbPark>(
        models::DbPark{"dbid0",
                       "clid0",
                       "Berlin",
                       {},
                       test_case.is_saas_park,
                       test_case.is_getting_orders_from_app});
    cf::infrastructure::FetchDbPark::Set(context, park);

    EXPECT_EQ(filter->Process({{}, "dbid0_uuid0"}, context),
              test_case.expected_result);
  }
}

const formats::json::Value kWhiteLabelRequirements =
    formats::json::FromString(R"=(
  {
    "order": {
      "request": {
        "white_label_requirements": {}
      }
    }
  }
  )=");

const formats::json::Value kNoWhiteLabelRequirements =
    formats::json::FromString(R"=(
  {
    "order": {
      "request": {}
    }
  }
  )=");

const formats::json::Value kNoRequest = formats::json::FromString(R"=(
  {
    "order": {}
  }
  )=");

const formats::json::Value kNoOrder = formats::json::FromString(R"=(
  {}
  )=");

INSTANTIATE_TEST_SUITE_P(
    SaasParksTests, SaasParksTestCase,
    ::testing::Values(
        // not saas orders and saas parks
        TestCase{true, true, kNoWhiteLabelRequirements, cf::Result::kAllow,
                 true},
        TestCase{true, true, kNoRequest, cf::Result::kAllow, true},
        TestCase{true, true, kNoOrder, cf::Result::kAllow, true},
        TestCase{true, false, kNoWhiteLabelRequirements, cf::Result::kDisallow,
                 true},
        TestCase{true, false, kNoRequest, cf::Result::kDisallow, true},
        TestCase{true, false, kNoOrder, cf::Result::kDisallow, true},
        // saas orders and saas parks
        TestCase{true, true, kWhiteLabelRequirements, {}, false},
        TestCase{true, false, kWhiteLabelRequirements, {}, false},
        // saas orders and not saas parks
        TestCase{false, true, kWhiteLabelRequirements, {}, false},
        TestCase{false, false, kWhiteLabelRequirements, {}, false},
        // not saas orders and not saas parks
        TestCase{false, true, kNoWhiteLabelRequirements, cf::Result::kIgnore,
                 true},
        TestCase{false, true, kNoRequest, cf::Result::kIgnore, true},
        TestCase{false, false, kNoOrder, cf::Result::kIgnore, true}));
