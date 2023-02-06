#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <string>
#include <vector>

#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/logging/level.hpp>
#include <userver/utest/parameter_names.hpp>

#include "experiments3.hpp"
#include "visibility_helper_impl.hpp"

namespace ua_parser {

bool operator==(const AppVars& lhs, const AppVars& rhs) {
  using AppVarsMap = std::unordered_map<std::string, std::string>;
  return AppVarsMap(lhs.begin(), lhs.end()) ==
         AppVarsMap(rhs.begin(), rhs.end());
}

}  // namespace ua_parser

namespace tariff_categories_visibility::tests {

namespace {

const Brand kYaBrand = Brand{"yataxi"};
const std::optional<AppVars> kEmptyAppVars = {};
const std::optional<UserSource> kEmptyUserSource = {};
const std::optional<PhoneId> kEmptyPhoneId = {};
const std::optional<PaymentOption> kEmptyPaymentOption = {};

const dynamic_config::Snapshot& GetConfig() {
  return dynamic_config::GetDefaultSnapshot();
}

class ExperimentsHelperMock : public ExperimentsHelper {
  using ExperimentsHelper::ExperimentsHelper;

 public:
  MOCK_METHOD(bool, ShouldDelayVisibilityExperimentsMatch, (),
              (const, override));
  MOCK_METHOD(std::unordered_set<std::string>, GetVisibilityExperiments,
              (const AppVars&, std::optional<PhoneId>,
               std::optional<PaymentOption>),
              (const, override));
};

using CheckType = VisibilityHelperImpl::CheckType;

class VisibilityHelperMock : public VisibilityHelperImpl {
  using VisibilityHelperImpl::VisibilityHelperImpl;

 public:
  MOCK_METHOD(const dynamic_config::Snapshot&, GetConfig, (),
              (const, override));
  MOCK_METHOD(const std::vector<VisibilityCheck>&, GetChecks, (CheckType),
              (const, override));
};

std::vector<VisibilityCheck> MockVisibilityChecks(
    const std::vector<bool>& results) {
  std::vector<VisibilityCheck> checks;

  for (auto result : results) {
    checks.push_back(
        [result](const Category&, const CheckContext&,
                 const dynamic_config::Snapshot&) { return result; });
  }

  return checks;
}

}  // namespace

namespace filter_categories {

struct TestParams {
  std::vector<bool> basic_checks;
  std::vector<bool> hideable_checks;

  bool should_be_filtered;

  std::string test_name;
};

class TestVisibilityHelperFilter : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kBasicTestParams = {
    {
        {true, true},
        {true, true},
        false,
        "AllChecksTrue",
    },
    {
        {true, false},
        {true, true},
        true,
        "BasicFalse",
    },
    {
        {true, true},
        {true, false},
        true,
        "HideableFalse",
    },
    {
        {false, false},
        {false, false},
        true,
        "AllChecksFalse",
    },
};

TEST_P(TestVisibilityHelperFilter, GetFilteredCategories) {
  const auto params = GetParam();

  // It is safe to pass nullptr as exp3_cache as long as we mock all methods
  // called during test run.
  auto exp3_helper = std::make_shared<ExperimentsHelperMock>(nullptr);

  EXPECT_CALL(*exp3_helper, ShouldDelayVisibilityExperimentsMatch())
      .Times(1)
      .WillRepeatedly(testing::Return(false));

  // It is safe to pass nullptr as config since config getter is mocked.
  VisibilityHelperMock visibility_helper{dynamic_config::GetDefaultSnapshot(),
                                         exp3_helper, nullptr,
                                         logging::Level::kInfo};

  const auto& context =
      visibility_helper.MakeContext(kYaBrand, kEmptyAppVars, kEmptyUserSource,
                                    kEmptyPhoneId, kEmptyPaymentOption);

  const std::vector<Category> categories = {
      Category{"econom"},
      Category{"comfort"},
      Category{"business"},
  };
  const auto num_categories = categories.size();

  const auto& config = GetConfig();
  EXPECT_CALL(visibility_helper, GetConfig())
      .Times(1)
      .WillRepeatedly(testing::ReturnRef(config));

  const auto basic_checks = MockVisibilityChecks(params.basic_checks);
  const auto hideable_checks = MockVisibilityChecks(params.hideable_checks);

  EXPECT_CALL(visibility_helper, GetChecks(CheckType::Basic))
      .Times(num_categories)
      .WillRepeatedly(testing::ReturnRef(basic_checks));

  EXPECT_CALL(visibility_helper, GetChecks(CheckType::Hideable))
      .Times(num_categories)
      .WillRepeatedly(testing::ReturnRef(hideable_checks));

  const auto zone_name = ZoneName{"moscow"};

  const auto filtered_categories =
      visibility_helper.GetFilteredCategories(context, categories, zone_name);

  const auto expected_categories =
      params.should_be_filtered ? std::vector<Category>{} : categories;

  EXPECT_EQ(filtered_categories, expected_categories);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestVisibilityHelperFilter,
                         testing::ValuesIn(kBasicTestParams),
                         ::utest::PrintTestName());

}  // namespace filter_categories

namespace visibility_attributes {

struct TestParams {
  std::vector<bool> basic_checks;
  std::vector<bool> hideable_checks;
  bool supports_hideable;

  bool should_be_skipped;
  bool is_visible;

  std::string test_name;
};

class TestVisibilityHelperAttributes
    : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kBasicTestParams = {
    {
        {true, true},
        {true, true},
        false,
        false,
        true,
        "AllChecksTrue",
    },
    {
        {true, false},
        {true, true},
        false,
        true,
        false,
        "BasicFalse",
    },
    {
        {true, true},
        {true, false},
        false,
        true,
        false,
        "HideableFalse",
    },
    {
        {false, false},
        {false, false},
        false,
        true,
        false,
        "AllChecksFalse",
    },
    {
        {true, true},
        {true, true},
        true,
        false,
        true,
        "SupportsHideableAllChecksTrue",
    },
    {
        {true, false},
        {true, true},
        true,
        true,
        false,
        "SupportsHideableBasicFalse",
    },
    {
        {true, true},
        {true, false},
        true,
        false,
        false,
        "SupportsHideableHideableFalse",
    },
    {
        {false, false},
        {false, false},
        true,
        true,
        false,
        "SupportsHideableAllChecksFalse",
    },
};

TEST_P(TestVisibilityHelperAttributes, VisibilityAttributes) {
  const auto params = GetParam();

  // It is safe to pass nullptr as exp3_cache as long as we mock all methods
  // called during test run.
  auto exp3_helper = std::make_shared<ExperimentsHelperMock>(nullptr);

  EXPECT_CALL(*exp3_helper, ShouldDelayVisibilityExperimentsMatch())
      .Times(1)
      .WillRepeatedly(testing::Return(false));

  // It is safe to pass nullptr as config since config getter is mocked.
  VisibilityHelperMock visibility_helper{dynamic_config::GetDefaultSnapshot(),
                                         exp3_helper, nullptr,
                                         logging::Level::kInfo};

  const auto& context =
      visibility_helper.MakeContext(kYaBrand, kEmptyAppVars, kEmptyUserSource,
                                    kEmptyPhoneId, kEmptyPaymentOption);

  const std::vector<Category> categories = {
      Category{"econom"},
      Category{"comfort"},
      Category{"business"},
  };
  const auto num_categories = categories.size();

  const auto& config = GetConfig();
  EXPECT_CALL(visibility_helper, GetConfig())
      .Times(1)
      .WillRepeatedly(testing::ReturnRef(config));

  const auto basic_checks = MockVisibilityChecks(params.basic_checks);
  const auto hideable_checks = MockVisibilityChecks(params.hideable_checks);

  EXPECT_CALL(visibility_helper, GetChecks(CheckType::Basic))
      .Times(num_categories)
      .WillRepeatedly(testing::ReturnRef(basic_checks));

  EXPECT_CALL(visibility_helper, GetChecks(CheckType::Hideable))
      .Times(num_categories)
      .WillRepeatedly(testing::ReturnRef(hideable_checks));

  const auto zone_name = ZoneName{"moscow"};

  const auto attributes_map = visibility_helper.GetVisibilityAttributes(
      context, categories, params.supports_hideable, zone_name);

  for (const auto& category : categories) {
    const auto& attributes = attributes_map.at(category);
    EXPECT_EQ(attributes.should_be_skipped, params.should_be_skipped);
    EXPECT_EQ(attributes.is_visible, params.is_visible);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestVisibilityHelperAttributes,
                         testing::ValuesIn(kBasicTestParams),
                         ::utest::PrintTestName());

}  // namespace visibility_attributes

namespace create_context {

struct TestParams {
  Brand brand;
  std::optional<AppVars> app_vars;
  std::optional<UserSource> user_source;
  std::optional<PhoneId> phone_id;
  std::optional<PaymentOption> payment_option;
  bool should_delay_exp_match;

  std::string test_name;
};

class TestMakeContext : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kBasicTestParams = {
    {
        kYaBrand,
        {},
        {},
        {},
        {},
        false,

        "ExpMatchNotDelayedEmptyOptionalUserData",
    },
    {
        kYaBrand,
        AppVars{},
        UserSource{},
        PhoneId{},
        PaymentOption{},
        false,

        "ExpMatchNotDelayedFilledUserData",
    },
    {
        kYaBrand,
        {},
        {},
        {},
        {},
        true,

        "ExpMatchDelayedEmptyOptionalUserData",
    },
    {
        kYaBrand,
        AppVars{},
        UserSource{},
        PhoneId{},
        PaymentOption{},
        true,

        "ExpMatchDelayedFilledUserData",
    },
};

TEST_P(TestMakeContext, VisibilityAttributes) {
  const auto params = GetParam();

  static const UserExperiments user_exps{"exp1", "exp2"};

  // It is safe to pass nullptr as exp3_cache as long as we mock all methods
  // called during test run.
  auto exp3_helper = std::make_shared<ExperimentsHelperMock>(nullptr);

  EXPECT_CALL(*exp3_helper, ShouldDelayVisibilityExperimentsMatch())
      .Times(1)
      .WillRepeatedly(testing::Return(params.should_delay_exp_match));

  const bool exp_match_should_be_called =
      !params.should_delay_exp_match && params.app_vars.has_value();

  if (exp_match_should_be_called) {
    EXPECT_CALL(*exp3_helper,
                GetVisibilityExperiments(testing::_, testing::_, testing::_))
        .Times(1)
        .WillRepeatedly(testing::Return(user_exps));
  } else {
    EXPECT_CALL(*exp3_helper,
                GetVisibilityExperiments(testing::_, testing::_, testing::_))
        .Times(0);
  }

  // It is safe to pass nullptr as config since config getter is mocked.
  VisibilityHelperMock visibility_helper{dynamic_config::GetDefaultSnapshot(),
                                         exp3_helper, nullptr,
                                         logging::Level::kInfo};

  const auto context = visibility_helper.MakeContext(
      params.brand, params.app_vars, params.user_source, params.phone_id,
      params.payment_option);

  EXPECT_EQ(context.brand, params.brand);
  EXPECT_EQ(context.app_vars, params.app_vars);
  EXPECT_EQ(context.user_source, params.user_source);
  EXPECT_EQ(context.phone_id, params.phone_id);
  EXPECT_EQ(context.payment_option, params.payment_option);

  OptUserExperiments expected_experiments;
  if (!params.should_delay_exp_match) {
    expected_experiments =
        params.app_vars.has_value() ? user_exps : UserExperiments{};
  }
  EXPECT_EQ(context.experiments, expected_experiments);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestMakeContext,
                         testing::ValuesIn(kBasicTestParams),
                         ::utest::PrintTestName());

}  // namespace create_context

}  // namespace tariff_categories_visibility::tests
