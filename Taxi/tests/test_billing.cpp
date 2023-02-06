#include <gtest/gtest.h>

#include <chrono>
#include <set>

#include <userver/utils/datetime.hpp>

#include "models/billing.hpp"

namespace parks_activation {

TEST(TestBillingModels, TestPaymentMethods) {
  models::Contract contract1;
  contract1.services = {135};
  EXPECT_FALSE(contract1.IsOfCard());
  EXPECT_FALSE(contract1.IsOfCash());

  contract1.services = {111, 125};
  EXPECT_TRUE(contract1.IsOfCard());
  EXPECT_TRUE(contract1.IsOfCash());

  contract1.services = {124};
  EXPECT_TRUE(contract1.IsOfCard());
  EXPECT_FALSE(contract1.IsOfCash());

  contract1.services = {605};
  EXPECT_TRUE(contract1.IsOfCard());
  EXPECT_FALSE(contract1.IsOfCash());
}

TEST(TestBillingModels, TestActiveContract) {
  {
    models::Contract contract1;
    contract1.type = models::ContractType::Spendable;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::Spendable;
    contract1.is_active = 1;
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 1;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 1;
    contract1.services = {124};
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 1;
    contract1.services = {124};
    contract1.payment_type = 1;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 1;
    contract1.services = {124};
    contract1.payment_type = 2;
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 1;
    contract1.services = {111};
    contract1.payment_type = 3;
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_faxed = 1;
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.is_cancelled = 1;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.is_deactivated = 1;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.is_suspended = 1;
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    const auto now = ::utils::datetime::Now();

    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.active_from = now - std::chrono::hours(1);
    contract1.active_till = now + std::chrono::hours(1);
    EXPECT_TRUE(contract1.IsActive());
  }

  {
    const auto now = ::utils::datetime::Now();

    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.active_from = now + std::chrono::hours(1);
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    const auto now = ::utils::datetime::Now();

    models::Contract contract1;
    contract1.type = models::ContractType::General;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.active_till = now - std::chrono::hours(1);
    EXPECT_FALSE(contract1.IsActive());
  }

  {
    const auto now = ::utils::datetime::Now();

    models::Contract contract1;
    contract1.type = models::ContractType::Spendable;
    contract1.is_active = 0;
    contract1.services = {111};
    contract1.payment_type = 3;
    contract1.is_signed = 1;
    contract1.active_till = now - std::chrono::hours(23);
    EXPECT_TRUE(contract1.IsActive());
  }
}

TEST(TestBillingModels, TestCachedClients) {
  using TimePoint = std::chrono::system_clock::time_point;
  static const std::string kTimeFormat = "%Y-%m-%dT%H:%M:%S";
  static const TimePoint kSampleTimePoint1 =
      ::utils::datetime::Stringtime("2015-3-22T9:00:00", "UTC", kTimeFormat);

  models::CachedClients clients;
  clients.insert({"park1", {"client1", "park1", kSampleTimePoint1}});
  clients.insert({"park2", {"client2", "park2", kSampleTimePoint1}});
  clients.insert({"park3", {"client2", "park3", kSampleTimePoint1}});
  clients.insert({"park3", {"client3", "park3", kSampleTimePoint1}});

  EXPECT_EQ(std::unordered_set<std::string>{"client1"},
            clients.GetClientsForPark("park1"));

  auto expected = std::unordered_set<std::string>{"client2", "client3"};
  EXPECT_EQ(expected, clients.GetClientsForPark("park3"));

  EXPECT_EQ(std::unordered_set<std::string>{"client2"},
            clients.GetClientsForPark("park2"));

  EXPECT_TRUE(clients.IsParkRegistered("park1"));
  EXPECT_TRUE(clients.IsParkRegistered("park2"));
  EXPECT_TRUE(clients.IsParkRegistered("park3"));
  EXPECT_FALSE(clients.IsParkRegistered("park4"));

  EXPECT_EQ(3, clients.size());
}

TEST(TestBillingModels, TestUpdate) {
  models::CachedBilling cached_billing;

  models::Contract contract1{1,
                             "client1",
                             models::ContractType::General,
                             models::ContractStatus::Active,
                             std::string("rur"),
                             1,
                             {},
                             {},
                             {},
                             2,
                             1,
                             1,
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {}};
  models::Contract contract2{2,
                             "client1",
                             models::ContractType::General,
                             models::ContractStatus::Active,
                             std::string("rur"),
                             1,
                             {},
                             {},
                             {},
                             2,
                             1,
                             2,
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {}};
  models::Contract contract3{3,
                             "client2",
                             models::ContractType::General,
                             models::ContractStatus::Active,
                             std::string("rur"),
                             1,
                             {},
                             {},
                             {},
                             2,
                             1,
                             3,
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {}};
  models::Contract contract4{4,
                             "client1",
                             models::ContractType::General,
                             models::ContractStatus::Active,
                             std::string("rur"),
                             1,
                             {},
                             {},
                             {},
                             2,
                             1,
                             4,
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {}};
  models::Contract contract5{5,
                             "client3",
                             models::ContractType::General,
                             models::ContractStatus::Active,
                             std::string("rur"),
                             1,
                             {},
                             {},
                             {},
                             2,
                             1,
                             5,
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {},
                             {}};

  models::Balance balance1{1, {}, {}, {}, {}, 4, std::nullopt};
  models::Balance balance2{2, {}, {}, {}, {}, 5, std::nullopt};
  models::Balance balance3{3, {}, {}, {}, {}, 6, std::nullopt};
  models::Balance balance4{4, {}, {}, {}, {}, 7, std::nullopt};

  models::ContractList new_contracts = {contract1, contract2, contract3};
  models::BalanceList new_balances = {balance1, balance2, balance3};

  cached_billing.Update(false, new_contracts, new_balances, {});

  models::CachedContracts expected_contracts{
      {1, contract1}, {2, contract2}, {3, contract3}};
  models::CachedBalances expected_balances{
      {1, balance1}, {2, balance2}, {3, balance3}};

  EXPECT_EQ(expected_contracts, cached_billing.Contracts());
  EXPECT_EQ(expected_balances, cached_billing.Balances());

  auto expected_contract_ids_1 = std::set<int>{1, 2};
  auto expected_contract_ids_2 = std::set<int>{3};

  EXPECT_EQ(expected_contract_ids_1,
            cached_billing.GetContractIdsForClient("client1"));
  EXPECT_EQ(expected_contract_ids_2,
            cached_billing.GetContractIdsForClient("client2"));

  EXPECT_EQ(3, cached_billing.ContractsRevision());
  EXPECT_EQ(6, cached_billing.BalancesRevision());

  contract1.revision = 6;
  contract1.contract_status = models::ContractStatus::Inactive;
  new_contracts = {contract1, contract4, contract5};
  new_balances = {balance4};

  cached_billing.Update(true, new_contracts, new_balances, {});

  expected_contracts = {
      {2, contract2}, {3, contract3}, {4, contract4}, {5, contract5}};
  expected_balances = {{2, balance2}, {3, balance3}, {4, balance4}};
  expected_contract_ids_1 = std::set<int>{2, 4};
  expected_contract_ids_2 = std::set<int>{3};
  auto expected_contract_ids_3 = std::set<int>{5};

  EXPECT_EQ(expected_contracts, cached_billing.Contracts());
  EXPECT_EQ(expected_balances, cached_billing.Balances());

  EXPECT_EQ(expected_contract_ids_1,
            cached_billing.GetContractIdsForClient("client1"));
  EXPECT_EQ(expected_contract_ids_2,
            cached_billing.GetContractIdsForClient("client2"));
  EXPECT_EQ(expected_contract_ids_3,
            cached_billing.GetContractIdsForClient("client3"));

  EXPECT_EQ(6, cached_billing.ContractsRevision());
  EXPECT_EQ(7, cached_billing.BalancesRevision());

  contract1.revision = 9223372036854775800;
  contract1.contract_status = models::ContractStatus::Active;
  new_contracts = {contract1};
  balance1.revision = 9223372036854775801;
  new_balances = {balance1};

  cached_billing.Update(true, new_contracts, new_balances, {});
  EXPECT_EQ(9223372036854775800, cached_billing.ContractsRevision());
  EXPECT_EQ(9223372036854775801, cached_billing.BalancesRevision());
}

}  // namespace parks_activation
