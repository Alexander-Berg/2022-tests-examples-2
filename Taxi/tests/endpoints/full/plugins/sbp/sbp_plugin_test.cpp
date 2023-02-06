#include <functional>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/common.hpp>
#include <endpoints/full/plugins/sbp_tariff_unavailable/plugin.hpp>

#include <taxi_config/variables/SBP_TARIFF_UNAVAILABLE_BLACKLIST.hpp>

namespace routestats::full {

namespace {
const std::string kOtherCode = "other_code";
const std::string kOtherMessage = "Other message";
const std::string kSbpCode = "sbp_not_available_without_point_b";
const std::string kSbpMessage =
    "routestats.tariff_unavailable.need_point_b_for_sbp##ru";
const std::string kEconome = "econome";
const std::string kBusiness = "business";
const std::string kShuttle = "shuttle";

core::TaxiConfigsPtr FillConfigs() {
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::SBP_TARIFF_UNAVAILABLE_BLACKLIST,
       {std::unordered_set<std::string>{kBusiness}}},
  });

  return std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));
}

routestats::full::ContextData MakeContext(bool is_sbp, bool exists_point_b,
                                          bool empty_blacklist) {
  auto context = routestats::test::full::GetDefaultContext();

  auto payment_method = is_sbp ? "sbp" : "card";
  context.input.original_request.payment =
      handlers::RequestPayment{payment_method};
  context.user.auth_context.locale = "ru";

  auto& request = context.input.original_request;

  request.route.emplace();
  request.route->push_back(
      ::geometry::Position{36.0 * ::geometry::lat, 55.0 * ::geometry::lon});
  if (exists_point_b) {
    request.route->push_back(
        ::geometry::Position{36.2 * ::geometry::lat, 55.2 * ::geometry::lon});
  }
  const auto& input = context.input;
  context.input = routestats::full::BuildRoutestatsInput(
      request, input.tariff_requirements, input.supported_options);

  if (!empty_blacklist) {
    context.taxi_configs = FillConfigs();
  }

  return context;
}

core::ServiceLevel MakeServiceLevel(const std::string class_,
                                    bool is_unavailable) {
  core::ServiceLevel service_level;
  service_level.class_ = class_;
  if (is_unavailable) {
    service_level.tariff_unavailable.emplace();
    service_level.tariff_unavailable->code = kOtherCode;
    service_level.tariff_unavailable->message = kOtherMessage;
  }
  return service_level;
}

std::vector<core::ServiceLevel> MakeServiceLevels() {
  return {MakeServiceLevel("econom", false),
          MakeServiceLevel("business", false),
          MakeServiceLevel("shuttle", true)};
}

void CheckResult(bool is_sbp, bool exists_point_b, bool empty_blacklist,
                 const std::vector<ServiceLevel>& service_levels) {
  bool need_block_order = is_sbp && !exists_point_b;

  for (const auto& level : service_levels) {
    if (level.class_ == kShuttle) {
      ASSERT_EQ(level.tariff_unavailable->code, kOtherCode);
      ASSERT_EQ(level.tariff_unavailable->message, kOtherMessage);
      continue;
    }
    // if business is not empty then business is in blacklist
    if (!need_block_order || (!empty_blacklist && level.class_ == kBusiness)) {
      ASSERT_EQ(level.tariff_unavailable, std::nullopt);
      continue;
    }
    ASSERT_EQ(level.tariff_unavailable->code, kSbpCode);
    ASSERT_EQ(level.tariff_unavailable->message, kSbpMessage);
  }
}

void MakeTest(bool is_sbp, bool exists_point_b, bool empty_blacklist) {
  const auto& context = MakeContext(is_sbp, exists_point_b, empty_blacklist);
  SbpTariffUnavailablePlugin plugin;
  auto service_levels = MakeServiceLevels();

  const auto& extentions = plugin.ExtendServiceLevels(
      test::full::MakeTopLevelContext(context), service_levels);
  test::ApplyExtensions(extentions, service_levels);

  CheckResult(is_sbp, exists_point_b, empty_blacklist, service_levels);
}

}  // namespace

TEST(SbpPluginExtendTest, NoSbp) {
  bool is_sbp = false;
  bool exists_point_b = false;
  bool empty_blacklist = true;
  MakeTest(is_sbp, exists_point_b, empty_blacklist);
}

TEST(SbpPluginExtendTest, PointBExists) {
  bool is_sbp = true;
  bool exists_point_b = true;
  bool empty_blacklist = true;
  MakeTest(is_sbp, exists_point_b, empty_blacklist);
}

TEST(SbpPluginExtendTest, EmptyBlacklist) {
  bool is_sbp = true;
  bool exists_point_b = false;
  bool empty_blacklist = true;
  MakeTest(is_sbp, exists_point_b, empty_blacklist);
}

TEST(SbpPluginExtendTest, FilledBlacklist) {
  bool is_sbp = true;
  bool exists_point_b = false;
  bool empty_blacklist = false;
  MakeTest(is_sbp, exists_point_b, empty_blacklist);
}
}  // namespace routestats::full
