#include <optional>
#include <string>
#include <userver/utest/utest.hpp>

#include <clients/billing-subventions-x/client_mock_base.hpp>

#include <bsx-rules-select-wrapper/bsx-rules-select-wrapper.hpp>

namespace {

namespace bsx = clients::billing_subventions_x;
namespace rsw = bsx_rules_select_wrapper;

class MockClient : public bsx::ClientMockBase {
 public:
  mutable size_t times_called = 0;
  mutable size_t rules_amount;

  MockClient(size_t rules_amount) : rules_amount(rules_amount) {}

  bsx::v2_rules_select::post::Response V2RulesSelect(
      const rsw::impl::BSXRulesSelectWrapperImpl::Key& request,
      const bsx::CommandControl& /*command_control*/ = {}) const override {
    times_called++;
    const bool need_one_more_request =
        (rules_amount >= static_cast<size_t>(request.body.limit));

    const size_t limit = request.body.limit;
    const size_t size = std::min(limit, rules_amount);
    rules_amount -= size;
    std::optional<std::string> cursor;
    if (need_one_more_request) {
      cursor = "cursor";
    }

    rsw::impl::BSXRulesSelectWrapperImpl::Result rules(size);
    return bsx::v2_rules_select::post::Response{
        bsx::SelectRulesResponse{std::move(rules), cursor}};
  }
};

rsw::impl::BSXRulesSelectWrapperImpl::Result SelectRules(
    rsw::impl::BSXRulesSelectWrapperImpl& rules_select_wrapper,
    bsx::SelectRulesRequest&& body) {
  rsw::impl::BSXRulesSelectWrapperImpl::Key request;
  request.body = std::move(body);
  return rules_select_wrapper.SelectRules(std::move(request));
}

}  // namespace

TEST(RulesSelectWrapper, RulesAmountNSelectLimitK) {
  std::vector<std::pair<size_t, int>> test_cases{{10, 4}, {10, 50}, {5, 5}};

  for (const auto& [rules_amount, limit] : test_cases) {
    MockClient client(rules_amount);
    rsw::impl::BSXRulesSelectWrapperImpl rules_select_wrapper(client);
    bsx::SelectRulesRequest body;
    body.limit = limit;
    const auto rules = SelectRules(rules_select_wrapper, std::move(body));
    ASSERT_EQ((rules_amount + limit) / limit, client.times_called);
    ASSERT_EQ(rules_amount, rules.size());
  }
}
