#include <userver/utest/utest.hpp>

#include <optional>

#include "utils/builders.hpp"
#include "utils/octonode.hpp"

namespace ivr_dispatcher::unit_tests {
// Test switch

/* static cast from Response (child) to Action (parent) class */

TEST(Switch, Default) {
  ASSERT_EQ(static_cast<handlers::Action>(utils::octonode::Switch()),
            (handlers::Action{handlers::ActionType::kSwitch}));
}

TEST(Switch, UseDeflectSwitch) {
  std::string call_to("123");
  ivr_dispatcher::utils::ActionParamsBuilder result_params;
  result_params.SetUseDeflectSwitch(true);
  result_params.SetCallTo(call_to);
  ASSERT_EQ(
      static_cast<handlers::Action>(utils::octonode::Switch(call_to, true)),
      (handlers::Action{handlers::ActionType::kSwitch,
                        result_params.ExtractValue()}));
}

TEST(Switch, UseSwitchTo) {
  std::string call_to("123");
  ivr_dispatcher::utils::ActionParamsBuilder result_params;
  result_params.SetCallTo(call_to);

  utils::octonode::OriginateParams originate_params{};
  ASSERT_EQ(static_cast<handlers::Action>(
                utils::octonode::Switch(call_to, false, originate_params)),
            (handlers::Action{handlers::ActionType::kSwitch,
                              result_params.ExtractValue()}));
}

}  // namespace ivr_dispatcher::unit_tests
