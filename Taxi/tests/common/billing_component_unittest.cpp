#include <fstream>

#include <gtest/gtest.h>

#include <billing/billing_component.hpp>
#include <secdist/secdist.hpp>
#include <secdist/settings/protocol.hpp>
#include <utils/helpers/json.hpp>

namespace billing {
namespace internal {

secdist::BillingService LoadConfigForService(
    const secdist::SecdistConfig& secdist, const std::string& service_type,
    const LogExtra& log_extra);
}
}  // namespace billing

namespace {

const std::string kLocalTestDataDir =
    std::string(SOURCE_DIR) + "/tests/static/billing_component_unittest/";
const std::string kSecdistWithUber =
    kLocalTestDataDir + "secdist_with_uber.json";
const std::string kSecdistNoUber = kLocalTestDataDir + "secdist_no_uber.json";
const std::string kSecdistEmpty = kLocalTestDataDir + "secdist_empty.json";

const std::string kSecdistBasicPath = SECDIST_PATH;

struct Params {
  std::string provided_service_type;
  std::string secdist_src;
  bool expect_loaded;
  std::string expected_billing_name;
  std::string expected_billing_key;
};

class TestLoadSecdistConfig : public ::testing::TestWithParam<Params> {};

TEST_P(TestLoadSecdistConfig, test_load_secdist_config) {
  const Params& params = GetParam();
  const LogExtra log_extra;

  Json::Value basic_doc;
  {
    std::ifstream stream(kSecdistBasicPath);
    basic_doc = utils::helpers::ParseJson(stream);
  }

  {
    std::ifstream stream(params.secdist_src);
    Json::Value patch_doc;
    ASSERT_NO_THROW(patch_doc = utils::helpers::ParseJson(stream))
        << params.secdist_src;
    basic_doc["settings_override"]["BILLINGS"] = std::move(patch_doc);
  }

  const secdist::SecdistConfig secdist_inst(basic_doc);
  if (params.expect_loaded) {
    const auto& billing_inst = billing::internal::LoadConfigForService(
        secdist_inst, params.provided_service_type, log_extra);
    EXPECT_EQ(params.expected_billing_name, billing_inst.name);
    EXPECT_EQ(params.expected_billing_key, billing_inst.api_key);
  } else {
    EXPECT_THROW(billing::internal::LoadConfigForService(
                     secdist_inst, params.provided_service_type, log_extra),
                 billing::ServiceConfigNotFound);
  }
}

const std::string kServiceTypeUber = "uber";

INSTANTIATE_TEST_CASE_P(
    P1, TestLoadSecdistConfig,
    ::testing::Values(
        Params{billing::kServiceTypeCard, kSecdistNoUber, true, "card",
               "card_token"},
        Params{kServiceTypeUber, kSecdistNoUber, true, "card", "card_token"},
        Params{"unknown", kSecdistNoUber, true, "card", "card_token"},

        Params{billing::kServiceTypeCard, kSecdistWithUber, true, "card",
               "card_token"},
        Params{kServiceTypeUber, kSecdistWithUber, true, "uber", "uber_token"},

        Params{billing::kServiceTypeCard, kSecdistEmpty, false, "n/a", "n/a"},
        Params{kServiceTypeUber, kSecdistEmpty, false, "n/a", "n/a"},
        Params{"unknown", kSecdistEmpty, false, "n/a", "n/a"}), );

}  // namespace
