#include <userver/utest/utest.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/common.hpp>
#include <endpoints/full/plugins/tariff_unavailable_by_point/plugin.hpp>
#include <experiments3/tariff_unavailable_by_point.hpp>

namespace routestats::full {

namespace {
const std::string kMessageTk = "routestats.tariff_unavailable.by_point";
const std::string kBrandingId = "test_branding_id";

formats::json::Value MakeExp(bool exp_enabled) {
  using formats::json::ValueBuilder;

  ValueBuilder Exp{};
  Exp["enabled"] = exp_enabled;
  Exp["message_tk"] = kMessageTk;
  Exp["branding_id"] = kBrandingId;

  return Exp.ExtractValue();
}

routestats::full::ContextData MakeContext(bool exp_enabled,
                                          bool exists_point_b) {
  auto context = test::full::GetDefaultContext();

  context.user.auth_context.locale = "ru";

  auto& request = context.input.original_request;
  request.route.emplace();
  request.route->push_back({36.0 * ::geometry::lat, 55.0 * ::geometry::lon});
  if (exists_point_b) {
    request.route->push_back({36.2 * ::geometry::lat, 55.2 * ::geometry::lon});
  }

  const auto& input = context.input;
  context.input = routestats::full::BuildRoutestatsInput(
      request, input.tariff_requirements, input.supported_options);

  using TitleExp = experiments3::TariffUnavailableByPoint;

  core::ExpMappedData exp_mapped_data{};
  exp_mapped_data[TitleExp::kName] = {
      TitleExp::kName, MakeExp(exp_enabled), {}};
  core::Experiments exps = {std::move(exp_mapped_data)};

  context.get_experiments_mapped_data =
      [exps = std::move(exps)](
          const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return exps.mapped_data;
  };

  return context;
}

void CheckResult(bool exp_enabled,
                 const std::vector<ServiceLevel>& service_levels) {
  for (const auto& level : service_levels) {
    if (exp_enabled) {
      ASSERT_EQ(level.tariff_unavailable->code, "not_available_by_points");
      ASSERT_EQ(level.tariff_unavailable->message, kMessageTk + "##ru");
    } else {
      ASSERT_EQ(level.tariff_unavailable, std::nullopt);
    }
  }
}

void MakeTest(bool exp_enabled, bool exists_point_b) {
  const auto& context = MakeContext(exp_enabled, exists_point_b);
  TariffUnavailableByPointPlugin plugin;

  auto service_levels = std::vector<core::ServiceLevel>{
      test::MockDefaultServiceLevel("econom"),
      test::MockDefaultServiceLevel("business")};

  const auto& extensions = plugin.ExtendServiceLevels(
      test::full::MakeTopLevelContext(context), service_levels);
  test::ApplyExtensions(extensions, service_levels);

  CheckResult(exp_enabled, service_levels);
}

}  // namespace

TEST(TariffUnavailableByPointTest, Disabled) {
  bool exp_enabled = false;
  bool exists_point_b = false;
  MakeTest(exp_enabled, exists_point_b);
}

TEST(TariffUnavailableByPointTest, Enabled) {
  bool exp_enabled = true;
  bool exists_point_b = false;
  MakeTest(exp_enabled, exists_point_b);
}

TEST(TariffUnavailableByPointTest, EnabledWithB) {
  bool exp_enabled = true;
  bool exists_point_b = true;
  MakeTest(exp_enabled, exists_point_b);
}

}  // namespace routestats::full
