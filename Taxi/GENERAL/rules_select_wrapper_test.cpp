#include <userver/utest/utest.hpp>

#include <clients/billing_subventions/client_mock_base.hpp>

#include <rules-select-wrapper/impl/rules_select_wrapper_impl.hpp>

namespace {

namespace cbs = clients::billing_subventions;
namespace crsw = clients::rules_select_wrapper;

class MockClient : public cbs::ClientMockBase {
 public:
  mutable size_t times_called = 0;
  mutable size_t rules_amount;

  MockClient(size_t rules_amount) : rules_amount(rules_amount) {}

  cbs::v1_rules_select::post::Response V1RulesSelect(
      const cbs::v1_rules_select::post::Request& request,
      const cbs::CommandControl& /*command_control*/ = {}) const override {
    times_called++;

    const size_t limit = request.body.limit;
    const size_t size = std::min(limit, rules_amount);
    rules_amount -= size;

    std::vector<cbs::Rule> rules(size);
    return cbs::v1_rules_select::post::Response{
        cbs::SelectRulesPostResponse{std::move(rules)}};
  }
};

std::vector<cbs::Rule> SelectRules(
    crsw::impl::RulesSelectWrapperImpl& rules_select_wrapper,
    cbs::SelectRulesPostRequest&& body, size_t chunk_size) {
  cbs::v1_rules_select::post::Request request;
  request.body = std::move(body);
  return rules_select_wrapper.SelectRules(std::move(request), chunk_size);
}

}  // namespace

TEST(RulesSelectWrapper, Limit1SelectOne) {
  MockClient client(1);
  crsw::impl::RulesSelectWrapperImpl rules_select_wrapper(client);
  cbs::SelectRulesPostRequest body;
  body.rule_ids = {"1"};
  body.limit = 1;
  const auto rules = SelectRules(rules_select_wrapper, std::move(body), 0);
  ASSERT_EQ(1, client.times_called);
  ASSERT_EQ(1, rules.size());
}

TEST(RulesSelectWrapper, Limit1SelectAll) {
  MockClient client(30);
  crsw::impl::RulesSelectWrapperImpl rules_select_wrapper(client);
  cbs::SelectRulesPostRequest body;
  body.rule_ids = {"1"};
  body.limit = std::numeric_limits<int>::max();
  const auto rules = SelectRules(rules_select_wrapper, std::move(body), 1);
  ASSERT_EQ(31, client.times_called);
  ASSERT_EQ(30, rules.size());
}

TEST(RulesSelectWrapper, Limit16SelectAll) {
  MockClient client(30);
  crsw::impl::RulesSelectWrapperImpl rules_select_wrapper(client);
  cbs::SelectRulesPostRequest body;
  body.rule_ids = {"1"};
  body.limit = std::numeric_limits<int>::max();
  const auto rules = SelectRules(rules_select_wrapper, std::move(body), 16);
  ASSERT_EQ(2, client.times_called);
  ASSERT_EQ(30, rules.size());
}

TEST(RulesSelectWrapper, InvalidRequest) {
  MockClient client(1);
  crsw::impl::RulesSelectWrapperImpl rules_select_wrapper(client);
  {
    cbs::SelectRulesPostRequest body;
    body.rule_ids = {"1"};

    ASSERT_NO_THROW(SelectRules(rules_select_wrapper, std::move(body), 0));
  }
  {
    cbs::SelectRulesPostRequest body;
    body.rule_ids = {"1"};
    body.is_personal = true;

    ASSERT_NO_THROW(SelectRules(rules_select_wrapper, std::move(body), 0));
  }

  {
    cbs::SelectRulesPostRequest body;
    body.rule_ids = {"1"};
    body.time_range.emplace();

    ASSERT_NO_THROW(SelectRules(rules_select_wrapper, std::move(body), 0));
  }

  {
    cbs::SelectRulesPostRequest body;
    body.rule_ids = {"1"};
    body.time_range.emplace();
    body.is_personal = true;

    ASSERT_THROW(SelectRules(rules_select_wrapper, std::move(body), 0),
                 crsw::impl::InvalidRequestException);
  }
}
