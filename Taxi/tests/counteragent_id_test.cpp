#include <userver/utest/utest.hpp>

#include <helpers/counteragent_id.hpp>

TEST(CounterAgentId, DonationCase) {
  const std::vector<helpers::counteragent_id::OrderItem> items{
      helpers::counteragent_id::OrderItem{
          "item_id", "stub", "balance_client_id", "10.00", std::nullopt,
          stq_tasks::eats_payments_billing_proxy_callback::OrderItemItemtype::
              kDonation}};

  const auto counter_agent_id = helpers::counteragent_id::GetPlaceId(items);
  ASSERT_EQ(counter_agent_id, "999999999");
}

TEST(CounterAgentId, TrivialCase) {
  const std::vector<helpers::counteragent_id::OrderItem> items{
      helpers::counteragent_id::OrderItem{
          "item_id", "123", "balance_client_id", "10.00", std::nullopt,
          stq_tasks::eats_payments_billing_proxy_callback::OrderItemItemtype::
              kProduct}};

  const auto counter_agent_id = helpers::counteragent_id::GetPlaceId(items);
  ASSERT_EQ(counter_agent_id, "123");
}
