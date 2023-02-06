#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/user_auction/plugin.hpp>

#include <userver/utest/utest.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <iostream>

using namespace std;

namespace routestats::full::user_auction {

namespace {

core::Experiments MockExperiments(bool enabled) {
  core::ExpMappedData experiments;
  formats::json::ValueBuilder exp_value = formats::json::Type::kObject;
  exp_value["enabled"] = enabled;
  experiments[experiments3::UserAuction::kName] = {
      experiments3::UserAuction::kName,
      formats::json::ValueBuilder{exp_value}.ExtractValue(),
      {}};
  return {std::move(experiments)};
}

std::shared_ptr<const ::routestats::plugins::top_level::Context> CreateContext(
    bool enabled) {
  auto context = test::full::GetDefaultContext();
  const auto exps = MockExperiments(enabled);
  context.get_experiments_mapped_data =
      [exps = std::move(exps)](
          const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return exps.mapped_data;
  };
  return test::full::MakeTopLevelContext(context);
}

core::ServiceLevel CreateServiceLevel(const std::string& class_) {
  auto service_level = test::MockDefaultServiceLevel(class_);
  return service_level;
}

}  // namespace

class UserAuctionExpParametrize : public ::testing::TestWithParam<bool> {
 protected:
  UserAuctionPlugin plugin;
};

TEST_P(UserAuctionExpParametrize, Check) {
  const auto enabled = GetParam();
  auto context = CreateContext(enabled);
  auto level = CreateServiceLevel("uberx");
  auto service_levels = std::vector<core::ServiceLevel>{level};

  const auto extensions = plugin.ExtendServiceLevels(context, service_levels);
  if (!enabled) {
    ASSERT_EQ(extensions.size(), 0);
  } else {
    for (auto& [_, extension] : extensions) {
      extension->Apply("test", level);
    }
    ASSERT_TRUE(level.user_auction.has_value());
    ASSERT_FALSE(level.user_auction->prepared);
  }
}

INSTANTIATE_TEST_SUITE_P(UserAuctionPlugin, UserAuctionExpParametrize,
                         ::testing::Values(false, true));

}  // namespace routestats::full::user_auction
