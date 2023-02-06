#include <gtest/gtest.h>
#include <chrono>
#include <iostream>
#include <list>
#include <memory>
#include <set>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include "components/park_activator.hpp"
#include "docs_map.hpp"
#include "names/parks_activation.hpp"
#include "utils/contracts.hpp"
#include "utils/field_value_change.hpp"
#include "utils/parks.hpp"
#include "utils/payment_methods.hpp"

namespace parks_activation {
std::vector<std::string> GetParkIds(
    const parks_activation::models::ParkList& accounts) {
  std::vector<std::string> ids;
  ids.reserve(accounts.size());
  std::transform(accounts.begin(), accounts.end(), std::back_inserter(ids),
                 [](const auto& park) { return park.park_id; });
  return ids;
}

using Deps = components::ParkActivator::Deps;
using ContractsForParks = utils::ContractsForParks;
using TimePoint = std::chrono::system_clock::time_point;

static const std::string kTimeFormat = "%Y-%m-%dT%H:%M:%S";

const TimePoint kSampleTimePoint1 =
    ::utils::datetime::Stringtime("2015-3-22T9:00:00", "UTC", kTimeFormat);
const TimePoint kSampleTimePoint2 =
    ::utils::datetime::Stringtime("2015-3-22T12:00:00", "UTC", kTimeFormat);

models::ParkList MockParkList() {
  models::ParkList parks;

  parks.push_back(models::Park{
      "park1", false, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {}, 0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  });

  parks.push_back(models::Park{
      "park2", false, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {}, 0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  });

  parks.push_back(models::Park{
      "park_nocontracts",
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      0,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
  });

  parks.push_back(models::Park{
      "park_logistic",
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      0,
      true,
      {},
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
  });

  return parks;
}

models::AccountList MockAccounts() {
  models::AccountList accounts;
  accounts.push_back(models::Account{
      "park1",
      "city1",
      std::nullopt,
      0.0,
      std::nullopt,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  });
  accounts.push_back(models::Account{
      "park2",
      "city2",
      std::nullopt,
      -10.0,
      std::nullopt,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  });
  accounts.push_back(models::Account{
      "park_nocontracts",
      "city3",
      std::nullopt,
      0.0,
      std::nullopt,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  });
  accounts.push_back(models::Account{
      "park_logistic",
      "city4",
      std::nullopt,
      0.0,
      std::nullopt,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  });
  return accounts;
}

models::CachedBilling MockBilling() {
  models::CachedBilling billing;
  models::ContractList contracts;
  contracts.push_back(models::Contract{1,
                                       "client1",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("RUR"),
                                       1,
                                       std::string(""),
                                       {},
                                       {111},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{2,
                                       "client1",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("RUR"),
                                       1,
                                       std::string(""),
                                       {},
                                       {111, 124},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{3,
                                       "client2",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("USD"),
                                       1,
                                       std::string(""),
                                       {},
                                       {111, 125},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{4,
                                       "client2",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("USD"),
                                       0,
                                       std::string(""),
                                       {},
                                       {605},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{5,
                                       "client3",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("USD"),
                                       0,
                                       std::string(""),
                                       {},
                                       {111},
                                       2,
                                       0,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{6,
                                       "client3",
                                       models::ContractType::Spendable,
                                       models::ContractStatus::Active,
                                       std::string("USD"),
                                       0,
                                       std::string(""),
                                       {},
                                       {111},
                                       2,
                                       1,
                                       0,
                                       81,
                                       1,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {}});
  contracts.push_back(models::Contract{7,
                                       "client3",
                                       models::ContractType::Spendable,
                                       models::ContractStatus::Active,
                                       std::string("USD"),
                                       0,
                                       std::string(""),
                                       {},
                                       {111},
                                       2,
                                       0,
                                       1,
                                       81,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{8,
                                       "client4",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("RUR"),
                                       1,
                                       std::string(""),
                                       {},
                                       {1161},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});
  contracts.push_back(models::Contract{9,
                                       "client4",
                                       models::ContractType::General,
                                       models::ContractStatus::Active,
                                       std::string("RUR"),
                                       1,
                                       std::string(""),
                                       {},
                                       {111},
                                       2,
                                       1,
                                       0,
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       {},
                                       ::utils::datetime::Now()});

  models::BalanceList balances;

  balances.push_back(
      models::Balance{1, {}, 10.0, 0.0, kSampleTimePoint1, 0, "ЛСТ-пример"});
  balances.push_back(
      models::Balance{2, {}, -10.0, 0.0, kSampleTimePoint2, 0, "ЛСЛ-пример"});
  // balance for contract 3 is absent
  balances.push_back(
      models::Balance{4, {}, -1.0, 0.0, std::nullopt, 0, std::nullopt});
  balances.push_back(
      models::Balance{5, {}, -1.0, 0.0, std::nullopt, 0, std::nullopt});
  balances.push_back(
      models::Balance{6, {}, -1.0, 0.0, std::nullopt, 0, std::nullopt});
  balances.push_back(
      models::Balance{7, {}, -1.0, 0.0, std::nullopt, 1, std::nullopt});
  balances.push_back(
      models::Balance{9, {}, -110.0, 0.0, std::nullopt, 0, std::nullopt});

  models::BalanceList balances_v2;

  balances_v2.push_back(models::Balance{8, 1161, -90.0, 0.0, kSampleTimePoint2,
                                        0, "ЛСЛ-пример-логистика"});

  billing.Update(false, contracts, balances, balances_v2);

  return billing;
}

models::CachedClients MockClients() {
  models::CachedClients result;
  result.insert({"park1", {"client1", "park1", kSampleTimePoint1}});
  result.insert({"park2", {"client2", "park2", kSampleTimePoint1}});
  result.insert(
      {"park_nocontracts", {"client3", "park_nocontracts", kSampleTimePoint1}});
  result.insert(
      {"park_logistic", {"client4", "park_logistic", kSampleTimePoint1}});
  return result;
}

models::Cities MockCities() {
  models::Cities result;
  result.emplace("city1", models::City{"city1", "country1", true});
  result.emplace("city2", models::City{"city2", "country2", true});
  result.emplace("city3", models::City{"city3", "country3", false});
  result.emplace("city4", models::City{"city4", "country4", true});
  return result;
}

models::Countries MockCountries() {
  models::Countries result;
  result.emplace("country1", models::Country{true});
  result.emplace("country2", models::Country{false});
  result.emplace("country3", models::Country{true});
  result.emplace("country4", models::Country{true});
  return result;
}

struct DepsWrapper {
  std::vector<std::string> park_ids;
  std::vector<models::Park> parks;
  std::unordered_map<std::string, models::Account> accounts;

  utils::ContractsForParks contracts_for_parks;
  models::CachedBilling billing;
  models::CachedClients billing_clients;
  models::Cities cities;
  models::Countries countries;
  configs::ParksActivationConfig config;

  // intermediate results - by value
  std::unordered_map<std::string,
                     std::unordered_map<std::string, models::ParkFieldChange>>
      field_changes;

  std::unordered_map<std::string, models::Park> old_values;
  Deps deps{park_ids, parks,           accounts,  contracts_for_parks,
            billing,  billing_clients, cities,    countries,
            config,   field_changes,   old_values};
};

DepsWrapper MockDeps(bool use_extra_thresholds = false) {
  models::ParkList parks = MockParkList();
  std::vector<std::string> parks_ids;
  parks_ids.reserve(parks.size());
  std::transform(parks.begin(), parks.end(), std::back_inserter(parks_ids),
                 [](const auto& park) { return park.park_id; });
  auto accounts_list = MockAccounts();
  models::CachedBilling billing = MockBilling();
  std::unordered_map<std::string, models::Account> accounts_map;
  for (auto&& account : accounts_list) {
    accounts_map.emplace(account.park_id, account);
  }
  auto billing_clients = MockClients();
  ContractsForParks contracts_for_parks = utils::GetActiveGeneralContracts(
      GetParkIds(parks), billing, billing_clients);
  models::Cities cities = MockCities();
  models::Countries countries = MockCountries();
  configs::ParksActivationConfig config(DocsMapForTest(use_extra_thresholds));
  std::unordered_map<std::string, models::Park> old_values;
  old_values.reserve(parks.size());
  std::transform(parks.begin(), parks.end(),
                 std::inserter(old_values, old_values.end()),
                 [](const models::Park& park) {
                   return std::make_pair(park.park_id, park);
                 });
  return DepsWrapper{std::move(parks_ids),    std::move(parks),
                     std::move(accounts_map), std::move(contracts_for_parks),
                     std::move(billing),      std::move(billing_clients),
                     std::move(cities),       std::move(countries),
                     std::move(config),       {},
                     std::move(old_values)};
}

using ParkContracts = utils::ParkContracts;
using JoinedContract = utils::JoinedContract;
void TestJoinedContractConsistency(const ParkContracts& park_contracts,
                                   int contract_id, bool has_balance) {
  EXPECT_TRUE(bool(park_contracts.count(contract_id)));
  auto contract = park_contracts.at(contract_id);
  EXPECT_EQ(contract_id, contract.contract.contract_id);
  if (has_balance) {
    ASSERT_TRUE(bool(contract.balance));
    EXPECT_EQ(contract_id, contract.balance->contract_id);
  } else {
    EXPECT_FALSE(bool(contract.balance));
  }
}

TEST(ParkActivator, TestGetActiveGeneralContracts) {
  auto parks = MockParkList();
  models::CachedBilling billing = MockBilling();
  auto billing_clients = MockClients();
  auto contracts_for_parks = utils::GetActiveGeneralContracts(
      GetParkIds(parks), billing, billing_clients);
  utils::ParkContracts park1_contracts(contracts_for_parks.at("park1"));
  EXPECT_EQ(2, park1_contracts.size());

  TestJoinedContractConsistency(park1_contracts, 1, true);
  EXPECT_TRUE(bool(park1_contracts.at(1).contract.netting));
  EXPECT_EQ(park1_contracts.at(1).contract, billing.Contracts().at(1));
  TestJoinedContractConsistency(park1_contracts, 2, true);

  utils::ParkContracts park2_contracts(contracts_for_parks.at("park2"));

  TestJoinedContractConsistency(park2_contracts, 3, false);
  TestJoinedContractConsistency(park2_contracts, 4, true);

  utils::ParkContracts park3_contracts(
      contracts_for_parks.at("park_nocontracts"));
  EXPECT_TRUE(park3_contracts.empty());
}

TEST(ParkActivator, TestJoinContracts) {
  auto parks = MockParkList();
  models::CachedBilling billing = MockBilling();
  auto billing_clients = MockClients();

  {
    auto contracts_for_parks =
        utils::JoinContracts(GetParkIds(parks), billing, billing_clients, true);
    auto park1_contracts = contracts_for_parks.at("park1");
    EXPECT_EQ(2, park1_contracts.size());

    auto park2_contracts = contracts_for_parks.at("park2");
    EXPECT_EQ(2, park2_contracts.size());

    auto park3_contracts = contracts_for_parks.at("park_nocontracts");
    EXPECT_EQ(1, park3_contracts.size());
  }
  {
    auto contracts_for_parks =
        utils::JoinContracts(GetParkIds(parks), billing, billing_clients, {},
                             models::ContractType::Spendable);
    auto park1_contracts = contracts_for_parks.at("park1");
    EXPECT_EQ(0, park1_contracts.size());

    auto park2_contracts = contracts_for_parks.at("park2");
    EXPECT_EQ(0, park2_contracts.size());

    auto park3_contracts = contracts_for_parks.at("park_nocontracts");
    EXPECT_EQ(2, park3_contracts.size());
    for (const auto& [contract_id, joined_contract] : park3_contracts) {
      EXPECT_EQ(models::ContractType::Spendable, joined_contract.contract.type);
    }
  }
  {
    auto contracts_for_parks =
        utils::JoinContracts(GetParkIds(parks), billing, billing_clients, {},
                             models::ContractType::Spendable, 81);
    auto park1_contracts = contracts_for_parks.at("park1");
    EXPECT_EQ(0, park1_contracts.size());

    auto park2_contracts = contracts_for_parks.at("park2");
    EXPECT_EQ(0, park2_contracts.size());

    auto park3_contracts = contracts_for_parks.at("park_nocontracts");
    EXPECT_EQ(2, park3_contracts.size());
  }
  {
    auto contracts_for_parks = utils::JoinContracts(
        GetParkIds(parks), billing, billing_clients, {}, {}, {}, 111);
    auto park1_contracts = contracts_for_parks.at("park1");
    EXPECT_EQ(2, park1_contracts.size());

    auto park2_contracts = contracts_for_parks.at("park2");
    EXPECT_EQ(1, park2_contracts.size());

    auto park3_contracts = contracts_for_parks.at("park_nocontracts");
    EXPECT_EQ(3, park3_contracts.size());
  }
}

TEST(ParkActivator, TestProcessCorpDontCheckContracts) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           false,        {},           {},  std::nullopt,
  };

  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  auto contract7 = models::Contract{7,
                                    "client1",
                                    models::ContractType::Spendable,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    1,
                                    81,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts{{1, {contract1, {}, {}}}};
  ParkContracts corp_contracts{{2, {contract7, {}, {}}}};

  auto corp = utils::ProcessCorpForPark(account, service_contracts,
                                        corp_contracts, true);
  EXPECT_EQ(false, corp.value);

  corp = utils::ProcessCorpForPark(account, service_contracts, corp_contracts,
                                   false);
  EXPECT_EQ(true, corp.value);
}

TEST(ParkActivator, TestProcessCorp) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  auto contract7 = models::Contract{7,
                                    "client1",
                                    models::ContractType::Spendable,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    1,
                                    81,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts{{1, {contract1, {}, {}}}};
  ParkContracts corp_contracts{{2, {contract7, {}, {}}}};

  auto corp = utils::ProcessCorpForPark(account, service_contracts,
                                        corp_contracts, true);
  EXPECT_EQ(true, corp.value);
}

TEST(ParkActivator, TestProcessCorpOffer) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };
  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };
  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    0,
                                    9,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  auto contract7 = models::Contract{7,
                                    "client1",
                                    models::ContractType::Spendable,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    1,
                                    81,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts{{1, {contract1, {}, {}}}};
  ParkContracts corp_contracts{{2, {contract7, {}, {}}}};

  auto corp = utils::ProcessCorpForPark(account, service_contracts,
                                        corp_contracts, true);
  EXPECT_EQ(false, corp.value);

  service_contracts[1].contract.offer_accepted = 1;
  corp = utils::ProcessCorpForPark(account, service_contracts, corp_contracts,
                                   true);
  EXPECT_EQ(true, corp.value);
}

TEST(ParkActivator, TestProcessCashAndCard) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account1 = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111, 128},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts{{1, {contract1, {}, {}}}};
  ParkContracts card_contracts{{1, {contract1, {}, {}}}};

  auto [cash, card] = utils::ProcessCashAndCardForPark(park1, service_contracts,
                                                       card_contracts, true);
  EXPECT_EQ(true, cash.value);
  EXPECT_EQ(true, card.value);
}

TEST(ParkActivator, TestProcessCashAndCardDontCheckContracts) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account1 = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111, 128},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts;
  ParkContracts card_contracts;

  auto [cash, card] = utils::ProcessCashAndCardForPark(park1, service_contracts,
                                                       card_contracts, true);
  EXPECT_EQ(false, cash.value);
  EXPECT_EQ(false, card.value);

  auto [no_contract_cash, no_cobtract_card] = utils::ProcessCashAndCardForPark(
      park1, service_contracts, card_contracts, false);
  EXPECT_EQ(true, no_contract_cash.value);
  EXPECT_EQ(true, no_cobtract_card.value);
}

TEST(ParkActivator, TestProcessCashAndCard2) {
  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account1 = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto contract1 = models::Contract{1,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("USD"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  auto contract2 = models::Contract{2,
                                    "client1",
                                    models::ContractType::General,
                                    models::ContractStatus::Active,
                                    std::string("RUR"),
                                    1,
                                    std::string(""),
                                    {},
                                    {111, 128},
                                    2,
                                    1,
                                    0,
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {},
                                    {}};

  ParkContracts service_contracts{{1, {contract1, {}, {}}}};
  ParkContracts card_contracts{{1, {contract1, {}, {}}},
                               {2, {contract2, {}, {}}}};

  auto [cash, card] = utils::ProcessCashAndCardForPark(park1, service_contracts,
                                                       card_contracts, true);
  EXPECT_EQ(true, cash.value);
  EXPECT_EQ(false, card.value);
}

TEST(ParkActivator, TestProcessSubsidy) {
  auto deps_wrapper = MockDeps();
  auto& deps = deps_wrapper.deps;

  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto service_contract = models::Contract{1,
                                           "client1",
                                           models::ContractType::General,
                                           models::ContractStatus::Active,
                                           std::string("USD"),
                                           1,
                                           std::string(""),
                                           {},
                                           {111},
                                           2,
                                           1,
                                           0,
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {}};

  auto subsidy_contract = models::Contract{7,
                                           "client1",
                                           models::ContractType::Spendable,
                                           models::ContractStatus::Active,
                                           std::string("USD"),
                                           1,
                                           std::string(""),
                                           1,
                                           {137},
                                           2,
                                           1,
                                           1,
                                           {},
                                           {},
                                           1,
                                           {},
                                           {},
                                           {},
                                           {},
                                           {}};

  ParkContracts service_contracts{{1, {service_contract, {}, {}}}};
  ParkContracts subsidy_contracts{{2, {subsidy_contract, {}, {}}}};

  auto subsidy = utils::ProcessSubsidyForPark(
      account, service_contracts, subsidy_contracts, deps.cities,
      deps.config.netting_subsidy_countries, true);
  EXPECT_EQ(true, subsidy.value);
}

TEST(ParkActivator, TestProcessSubsidyNoActiveSubsidyContract) {
  auto deps_wrapper = MockDeps();
  auto& deps = deps_wrapper.deps;

  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto service_contract = models::Contract{1,
                                           "client1",
                                           models::ContractType::General,
                                           models::ContractStatus::Active,
                                           std::string("USD"),
                                           1,
                                           std::string(""),
                                           {},
                                           {111},
                                           2,
                                           1,
                                           0,
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {}};

  auto subsidy_contract = models::Contract{7,
                                           "client1",
                                           models::ContractType::Spendable,
                                           models::ContractStatus::Active,
                                           std::string("USD"),
                                           1,
                                           std::string(""),
                                           0,
                                           {137},
                                           2,
                                           1,
                                           1,
                                           {},
                                           {},
                                           1,
                                           {},
                                           {},
                                           {},
                                           {},
                                           {}};

  ParkContracts service_contracts{{1, {service_contract, {}, {}}}};
  ParkContracts subsidy_contracts{{2, {subsidy_contract, {}, {}}}};

  auto subsidy = utils::ProcessSubsidyForPark(
      account, service_contracts, subsidy_contracts, deps.cities,
      deps.config.netting_subsidy_countries, true);
  EXPECT_EQ(false, subsidy.value);
}

TEST(ParkActivator, TestProcessSubsidyNettingSubsidyCountry) {
  auto now = ::utils::datetime::Stringtime("2020-01-01", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);

  auto deps_wrapper = MockDeps();
  auto& deps = deps_wrapper.deps;

  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto service_contract = models::Contract{1,
                                           "client1",
                                           models::ContractType::General,
                                           models::ContractStatus::Active,
                                           std::string("USD"),
                                           1,
                                           std::string(""),
                                           {},
                                           {111},
                                           2,
                                           1,
                                           0,
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {},
                                           {}};

  ParkContracts service_contracts{{1, {service_contract, {}, {}}}};

  std::unordered_map<std::string, ::utils::datetime::Date>
      netting_subsidy_countries_config;
  netting_subsidy_countries_config["country1"] =
      ::utils::datetime::Date(2019, 1, 1);

  auto subsidy =
      utils::ProcessSubsidyForPark(account, service_contracts, {}, deps.cities,
                                   netting_subsidy_countries_config, true);
  EXPECT_EQ(true, subsidy.value);

  netting_subsidy_countries_config["country1"] =
      ::utils::datetime::Date(2021, 1, 1);

  subsidy =
      utils::ProcessSubsidyForPark(account, service_contracts, {}, deps.cities,
                                   netting_subsidy_countries_config, true);
  EXPECT_EQ(false, subsidy.value);
}

TEST(ParkActivator, TestProcessSubsidyNotCheckContracts) {
  auto deps_wrapper = MockDeps();
  auto& deps = deps_wrapper.deps;

  auto park1 = models::Park{
      "park1", false, std::nullopt, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
      {},      {},    {},           0,  {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
  };

  auto account = models::Account{
      "park1",      "city1",      std::nullopt, 0.0, std::nullopt, {},
      std::nullopt, std::nullopt, false,        {},  {},           {},
      {},           true,         10000,        {},  std::nullopt,
  };

  auto subsidy = utils::ProcessSubsidyForPark(
      account, {}, {}, deps.cities, deps.config.netting_subsidy_countries,
      false);
  EXPECT_EQ(true, subsidy.value);
}

template <class ObjectWithParkId>
bool ListContainsPark(const std::vector<ObjectWithParkId>& objects,
                      const std::string& park_id) {
  return std::any_of(objects.begin(), objects.end(),
                     [&park_id](const ObjectWithParkId& obj) {
                       return obj.park_id == park_id;
                     });
}

template <class ObjectWithParkId>
const ObjectWithParkId& GetObjectByParkId(
    const std::vector<ObjectWithParkId>& objects, const std::string& park_id) {
  auto iter = std::find_if(objects.begin(), objects.end(),
                           [&park_id](const ObjectWithParkId& obj) {
                             return obj.park_id == park_id;
                           });
  if (iter == objects.end())
    throw std::runtime_error("object with park_id " + park_id + " not found");
  return *iter;
}

TEST(ParkActivator, TestFilterParks) {
  auto deps_wrapper = MockDeps();

  EXPECT_EQ(4, deps_wrapper.parks.size());

  std::unordered_set<std::string> not_processed_park_ids;
  auto& deps = deps_wrapper.deps;
  auto park = deps.parks.front();
  deps.accounts[park.park_id].contracts_revision = 2;

  EXPECT_THROW(utils::FilterNotProcessedParks(
                   deps.parks, deps.accounts, deps.billing, deps.cities,
                   deps.countries, not_processed_park_ids),
               std::runtime_error);

  deps.accounts[park.park_id].contracts_revision = 0;
  deps.accounts[park.park_id].balances_revision = 2;

  EXPECT_THROW(utils::FilterNotProcessedParks(
                   deps.parks, deps.accounts, deps.billing, deps.cities,
                   deps.countries, not_processed_park_ids),
               std::runtime_error);

  deps.accounts[park.park_id].balances_revision = 1;

  EXPECT_NO_THROW(utils::FilterNotProcessedParks(
      deps.parks, deps.accounts, deps.billing, deps.cities, deps.countries,
      not_processed_park_ids));

  EXPECT_EQ(1, not_processed_park_ids.size());
  // here park_nocontracts is in not_processed_park_ids
  // because its city is disabled
  EXPECT_TRUE(not_processed_park_ids.count("park_nocontracts") != 0);
  EXPECT_EQ(3, deps.parks.size());
  EXPECT_TRUE(ListContainsPark(deps.parks, "park1"));
  EXPECT_TRUE(ListContainsPark(deps.parks, "park2"));

  auto deps_wrapper2 = MockDeps();
  auto& deps2 = deps_wrapper2.deps;
  not_processed_park_ids.clear();

  deps2.cities.erase("city2");
  utils::FilterNotProcessedParks(deps2.parks, deps2.accounts, deps2.billing,
                                 deps2.cities, deps2.countries,
                                 not_processed_park_ids);

  EXPECT_EQ(2, not_processed_park_ids.size());
  EXPECT_TRUE(not_processed_park_ids.count("park_nocontracts") != 0);
  EXPECT_TRUE(not_processed_park_ids.count("park2") != 0);
  EXPECT_EQ(2, deps2.parks.size());
  EXPECT_TRUE(ListContainsPark(deps2.parks, "park1"));
  EXPECT_TRUE(ListContainsPark(deps2.parks, "park_logistic"));

  auto deps_wrapper3 = MockDeps();
  auto& deps3 = deps_wrapper3.deps;
  not_processed_park_ids.clear();

  deps_wrapper3.countries.erase("country1");
  utils::FilterNotProcessedParks(deps3.parks, deps3.accounts, deps3.billing,
                                 deps3.cities, deps3.countries,
                                 not_processed_park_ids);

  EXPECT_EQ(2, not_processed_park_ids.size());
  EXPECT_TRUE(not_processed_park_ids.count("park_nocontracts") != 0);
  EXPECT_TRUE(not_processed_park_ids.count("park1") != 0);
  EXPECT_EQ(2, deps3.parks.size());
  EXPECT_TRUE(ListContainsPark(deps3.parks, "park2"));
  EXPECT_TRUE(ListContainsPark(deps3.parks, "park_logistic"));
}

TEST(ParkActivator, TestNettings) {
  auto deps_wrapper = MockDeps();
  models::NettingsForParks nettings;
  models::CurrenciesForParks currencies;

  EXPECT_TRUE(bool(deps_wrapper.billing.Contracts().at(1).netting));

  EXPECT_EQ("park1", deps_wrapper.parks.front().park_id);
  EXPECT_TRUE(bool(deps_wrapper.contracts_for_parks.count("park1")));
  EXPECT_TRUE(bool(
      deps_wrapper.contracts_for_parks.at("park1").at(1).contract.netting));

  components::ParkActivator::GetNettingsAndCurrencies(deps_wrapper.deps,
                                                      nettings, currencies);

  EXPECT_EQ(3, nettings.size());
  EXPECT_TRUE(nettings.count("park1"));
  EXPECT_TRUE(nettings.count("park_logistic"));
  EXPECT_EQ(components::detail::MoscowToUtc(kSampleTimePoint2),
            nettings.at("park1").taxi);

  EXPECT_EQ(3, currencies.size());
  EXPECT_TRUE(currencies.count("park1"));
  EXPECT_TRUE(currencies.count("park2"));
  EXPECT_TRUE(currencies.count("park_logistic"));

  EXPECT_EQ("RUB", currencies.at("park1"));
  EXPECT_EQ("USD", currencies.at("park2"));
  EXPECT_EQ("RUB", currencies.at("park_logistic"));
}

TEST(ParkActivator, TestDynamicThresholds) {
  auto deps_wrapper = MockDeps();
  models::NettingsForParks nettings;
  models::CurrenciesForParks currencies;

  components::ParkActivator::GetNettingsAndCurrencies(deps_wrapper.deps,
                                                      nettings, currencies);
  // here we multiply 10 (our mock payments value) by 10000 (inner2cost coeff)
  auto clid_to_payments =
      models::CashlessPaymentsForParks{{"park1", {10 * 10000, 0l}}};
  components::ParkActivator::SetDynamicThresholds(deps_wrapper.deps,
                                                  clid_to_payments);

  const auto& park1 = deps_wrapper.deps.parks.front();
  const auto& account = deps_wrapper.deps.accounts[park1.park_id];
  EXPECT_EQ("park1", park1.park_id);
  ASSERT_TRUE(bool(account.threshold_dynamic));
  EXPECT_DOUBLE_EQ(-10.0, *account.threshold_dynamic);

  EXPECT_EQ(0, deps_wrapper.deps.field_changes.size());

  // this is already multiplied by 10000
  long long_number = 1000000000000l;

  clid_to_payments =
      models::CashlessPaymentsForParks{{"park1", {long_number, 0l}}};
  components::ParkActivator::SetDynamicThresholds(deps_wrapper.deps,
                                                  clid_to_payments);

  EXPECT_DOUBLE_EQ(-double(long_number / 10000l), *account.threshold_dynamic);
}

TEST(ParkActivator, TestDynamicThresholdsExtra) {
  auto deps_wrapper = MockDeps(true);
  models::NettingsForParks nettings;
  models::CurrenciesForParks currencies;

  components::ParkActivator::GetNettingsAndCurrencies(deps_wrapper.deps,
                                                      nettings, currencies);
  // here we multiply 10 (our mock payments value) by 10000 (inner2cost coeff)
  auto clid_to_payments =
      models::CashlessPaymentsForParks{{"park1", {10 * 10000, 0l}}};
  components::ParkActivator::SetDynamicThresholds(deps_wrapper.deps,
                                                  clid_to_payments);

  const auto& park1 = deps_wrapper.deps.parks.front();
  const auto& account = deps_wrapper.deps.accounts[park1.park_id];
  EXPECT_EQ("park1", park1.park_id);
  ASSERT_TRUE(bool(account.threshold_dynamic));
  EXPECT_DOUBLE_EQ(-2010.0, *account.threshold_dynamic);

  EXPECT_EQ(0, deps_wrapper.deps.field_changes.size());

  deps_wrapper.deps.cities[account.city_id].country = "country2";

  components::ParkActivator::SetDynamicThresholds(deps_wrapper.deps,
                                                  clid_to_payments);

  ASSERT_TRUE(bool(account.threshold_dynamic));
  // for default country, -1000 should be used
  EXPECT_DOUBLE_EQ(-1010.0, *account.threshold_dynamic);
}

TEST(ParkActivator, TestRecommendedPayment) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");

  auto balance =
      models::Balance{1, {}, 10.0, 5000.0, kSampleTimePoint1, 0, "ЛСТ-пример"};

  double payment = utils::GetRecommendedPayment(balance, now);
  // expected value computed with corresponding python function
  EXPECT_DOUBLE_EQ(26990.0, payment);
}

TEST(ParkActivator, TestProcessPark) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  auto& park1 = deps_wrapper.parks[0];
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  auto& park2 = deps_wrapper.parks[1];
  auto& account2 = deps_wrapper.accounts[park2.park_id];
  auto& park3 = deps_wrapper.parks[2];
  auto& account3 = deps_wrapper.accounts[park3.park_id];

  EXPECT_EQ("park1", park1.park_id);
  EXPECT_EQ("park2", park2.park_id);
  EXPECT_EQ("park_nocontracts", park3.park_id);

  account1.threshold_dynamic = -20.0;
  // both balances are above threshold
  EXPECT_GE(
      *deps_wrapper.contracts_for_parks.at("park1").at(1).balance->balance,
      *account1.threshold_dynamic);
  EXPECT_GE(
      *deps_wrapper.contracts_for_parks.at("park1").at(2).balance->balance,
      *account1.threshold_dynamic);

  bool check_contracts =
      deps_wrapper.countries
          .at(deps_wrapper.cities.at(account1.city_id).country)
          .check_contracts;
  utils::ProcessPark(park1, account1, deps_wrapper.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts,
                     deps_wrapper.deps.config);

  // park should not be deactivated by taxi
  EXPECT_FALSE(park1.deactivated);
  // deactivate logistics
  EXPECT_EQ(deps_wrapper.deps.field_changes.at("park1").size(), 1);
  EXPECT_EQ(1, deps_wrapper.deps.field_changes.size());

  account2.threshold_dynamic = 0.0;
  // balance for contract 4 for park2 is lower than threshold
  EXPECT_LT(
      *deps_wrapper.contracts_for_parks.at("park2").at(4).balance->balance,
      *account2.threshold_dynamic);
  // but we don't check contracts in country2
  EXPECT_FALSE(deps_wrapper.countries.at("country2").check_contracts);
  check_contracts = deps_wrapper.countries
                        .at(deps_wrapper.cities.at(account2.city_id).country)
                        .check_contracts;
  utils::ProcessPark(park2, account2, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts,
                     deps_wrapper.deps.config);

  // should be false because we don't check contracts in country2
  EXPECT_FALSE(park2.deactivated);
  // deactivate logistics
  EXPECT_EQ(deps_wrapper.deps.field_changes.at("park2").size(), 1);
  EXPECT_EQ(2, deps_wrapper.deps.field_changes.size());

  check_contracts = deps_wrapper.countries
                        .at(deps_wrapper.cities.at(account3.city_id).country)
                        .check_contracts;
  utils::ProcessPark(park3, account3, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts,
                     deps_wrapper.deps.config);

  EXPECT_TRUE(park3.deactivated);
  EXPECT_EQ(deactivation_reasons::kNoActiveContracts, park3.deactivated_reason);
  // we did not change recommended payments because there are no contracts
  EXPECT_EQ(deps_wrapper.deps.field_changes.at("park_nocontracts").size(), 2);
  EXPECT_EQ(3, deps_wrapper.deps.field_changes.size());
}

TEST(ParkActivator, TestProcessParkLowBalance) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  auto& park1 = deps_wrapper.parks.front();
  park1.can_cash = true;
  park1.can_card = true;
  park1.can_corp = false;
  park1.can_coupon = true;
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  configs::ParksActivationConfig config(
      DocsMapForTest(true, true, {"card", "corp"}));

  account1.threshold_dynamic = 0.0;
  auto check_contracts = true;

  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_FALSE(park1.deactivated);
  EXPECT_FALSE(park1.can_cash);
  EXPECT_FALSE(park1.can_coupon);
  EXPECT_FALSE(park1.can_corp);
  EXPECT_TRUE(park1.can_card);
}

void FillParkLogisticTest(parks_activation::models::Park& park_logistic) {
  park_logistic.can_corp = true;
  park_logistic.can_corp_reason = {};
  park_logistic.can_cash = true;
  park_logistic.can_cash_reason = {};
  park_logistic.can_card = true;
  park_logistic.can_card_reason = {};
  park_logistic.can_subsidy = true;
  park_logistic.can_subsidy_reason = {};

  park_logistic.can_coupon = true;
  park_logistic.can_coupon_reason = {};

  park_logistic.can_logistic = true;
  park_logistic.can_logistic_reason = {};
  park_logistic.logistic_can_cash = true;
  park_logistic.logistic_can_cash_reason = {};
  park_logistic.logistic_can_card = true;
  park_logistic.logistic_can_card_reason = {};
  park_logistic.logistic_can_subsidy = true;
  park_logistic.logistic_can_subsidy_reason = {};

  park_logistic.logistic_deactivated = false;
  park_logistic.logistic_deactivated_reason = {};
}

TEST(ParkActivator, TestProcessParkLowLogisticAndTaxiBalances) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  auto& park_logistic = *(deps_wrapper.parks.begin() + 3);
  EXPECT_EQ("park_logistic", park_logistic.park_id);

  auto& account_logistic = deps_wrapper.accounts[park_logistic.park_id];
  auto check_contracts = true;

  configs::ParksActivationConfig config(
      DocsMapForTest(true, true, {"card", "corp"}, false, {}, {}, true));

  // When logistic contract is underpaid, but taxi contract is norm
  FillParkLogisticTest(park_logistic);
  account_logistic.threshold_dynamic = -1000.0;
  account_logistic.logistic_threshold_dynamic = 0.0;

  utils::ProcessPark(park_logistic, account_logistic,
                     deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_TRUE(park_logistic.can_corp);
  EXPECT_TRUE(park_logistic.can_cash);
  EXPECT_TRUE(park_logistic.can_card);
  EXPECT_TRUE(park_logistic.can_subsidy);
  EXPECT_TRUE(park_logistic.can_coupon);

  EXPECT_TRUE(park_logistic.can_logistic);
  EXPECT_FALSE(park_logistic.logistic_can_cash);
  EXPECT_TRUE(park_logistic.logistic_can_card);
  EXPECT_FALSE(park_logistic.logistic_can_subsidy);
  EXPECT_FALSE(park_logistic.logistic_deactivated);

  // When taxi contract is underpaid, but logistic contract is norm
  FillParkLogisticTest(park_logistic);
  account_logistic.threshold_dynamic = 0.0;
  account_logistic.logistic_threshold_dynamic = -1000.0;

  utils::ProcessPark(park_logistic, account_logistic,
                     deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_TRUE(park_logistic.can_corp);
  EXPECT_FALSE(park_logistic.can_cash);
  EXPECT_TRUE(park_logistic.can_card);
  EXPECT_FALSE(park_logistic.can_subsidy);
  EXPECT_FALSE(park_logistic.can_coupon);

  EXPECT_TRUE(park_logistic.can_logistic);
  EXPECT_TRUE(park_logistic.logistic_can_cash);
  EXPECT_TRUE(park_logistic.logistic_can_card);
  EXPECT_TRUE(park_logistic.logistic_can_subsidy);
  EXPECT_FALSE(park_logistic.logistic_deactivated);

  // When both contracts are underpaid
  FillParkLogisticTest(park_logistic);
  account_logistic.threshold_dynamic = 0.0;
  account_logistic.logistic_threshold_dynamic = 0.0;

  utils::ProcessPark(park_logistic, account_logistic,
                     deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_TRUE(park_logistic.can_corp);
  EXPECT_FALSE(park_logistic.can_cash);
  EXPECT_TRUE(park_logistic.can_card);
  EXPECT_FALSE(park_logistic.can_subsidy);
  EXPECT_FALSE(park_logistic.can_coupon);

  EXPECT_TRUE(park_logistic.can_logistic);
  EXPECT_FALSE(park_logistic.logistic_can_cash);
  EXPECT_TRUE(park_logistic.logistic_can_card);
  EXPECT_FALSE(park_logistic.logistic_can_subsidy);
  EXPECT_FALSE(park_logistic.logistic_deactivated);
}

TEST(ParkActivator, TestProcessParkLowLogisticBalancesEnabled) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  auto& park_logistic = *(deps_wrapper.parks.begin() + 3);
  EXPECT_EQ("park_logistic", park_logistic.park_id);

  auto& account_logistic = deps_wrapper.accounts[park_logistic.park_id];
  auto check_contracts = true;

  configs::ParksActivationConfig config(
      DocsMapForTest(true, true, {"card", "corp"}, false, {},
                     {{"park_logistic", false}}, true));

  // When logistic contract is underpaid, but taxi contract is norm
  FillParkLogisticTest(park_logistic);
  account_logistic.threshold_dynamic = -1000.0;
  account_logistic.logistic_threshold_dynamic = 0.0;

  utils::ProcessPark(park_logistic, account_logistic,
                     deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_TRUE(park_logistic.can_corp);
  EXPECT_TRUE(park_logistic.can_cash);
  EXPECT_TRUE(park_logistic.can_card);
  EXPECT_TRUE(park_logistic.can_subsidy);
  EXPECT_TRUE(park_logistic.can_coupon);

  EXPECT_TRUE(park_logistic.can_logistic);
  EXPECT_TRUE(park_logistic.logistic_can_cash);
  EXPECT_TRUE(park_logistic.logistic_can_card);
  EXPECT_TRUE(park_logistic.logistic_can_subsidy);
  EXPECT_FALSE(park_logistic.logistic_deactivated);
}

TEST(ParkActivator, TestProcessPark2) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  auto& park1 = deps_wrapper.parks.front();
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  EXPECT_EQ("park1", park1.park_id);

  account1.threshold_dynamic = 0.0;

  EXPECT_GE(
      *deps_wrapper.contracts_for_parks.at("park1").at(1).balance->balance,
      *account1.threshold_dynamic);
  EXPECT_LT(
      *deps_wrapper.contracts_for_parks.at("park1").at(2).balance->balance,
      *account1.threshold_dynamic);
  EXPECT_FALSE(park1.deactivated);
  auto check_contracts =
      deps_wrapper.countries
          .at(deps_wrapper.cities.at(account1.city_id).country)
          .check_contracts;
  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts,
                     deps_wrapper.deps.config);

  // park should be deactivated because its balance is lower than threshold
  EXPECT_TRUE(park1.deactivated);
  EXPECT_EQ(deactivation_reasons::kLowBalance, park1.deactivated_reason);
  EXPECT_EQ(1, deps_wrapper.deps.field_changes.size());
}

TEST(ParkActivator, TestProcessParkFinishedContracts) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto deps_wrapper = MockDeps();
  ::utils::datetime::MockSleep(std::chrono::seconds(10));
  auto& park1 = deps_wrapper.parks.front();
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  configs::ParksActivationConfig config(
      DocsMapForTest(true, true, {"card", "corp"}, true));

  auto check_contracts = true;

  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_TRUE(park1.deactivated);
  EXPECT_EQ(park1.deactivated_reason.value(), "all contracts are finished");

  ::utils::datetime::MockNowSet(now);
  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_FALSE(park1.deactivated);

  check_contracts = false;
  ::utils::datetime::MockSleep(std::chrono::seconds(10));

  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts, config);

  EXPECT_FALSE(park1.deactivated);
  check_contracts = true;
  configs::ParksActivationConfig dont_check_contract_lifetime(
      DocsMapForTest(true, true, {"card", "corp"}, false));

  utils::ProcessPark(park1, account1, deps_wrapper.deps.contracts_for_parks,
                     deps_wrapper.deps.billing_clients,
                     deps_wrapper.deps.field_changes, check_contracts,
                     dont_check_contract_lifetime);
  EXPECT_FALSE(park1.deactivated);
}

TEST(ParkActivator, TestProcessPark400000000588) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto park400000000588 = models::Park{
      "400000000588",
      false,
      std::nullopt,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      0,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
  };
  auto account = models::Account{
      "400000000588",
      "city1",
      std::nullopt,
      -5000.0,
      -5000.0,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  };

  auto deps_wrapper = MockDeps();
  deps_wrapper.deps.parks.push_back(park400000000588);

  models::BalanceList new_balances{models::Balance{
      296806, {}, -12635.24, 0.0, std::nullopt, 0, "ЛСТ-пример"}};

  models::ContractList new_contracts{
      models::Contract{296806,
                       "client_400000000588",
                       models::ContractType::General,
                       models::ContractStatus::Active,
                       std::string("RUB"),
                       0,
                       std::string(""),
                       {},
                       {111, 124},
                       2,
                       1,
                       0,
                       {},
                       {},
                       {},
                       {},
                       {},
                       {},
                       {},
                       {}},
      models::Contract{296807,
                       "client_400000000588",
                       models::ContractType::Spendable,
                       models::ContractStatus::Active,
                       std::string("RUR"),
                       0,
                       std::string(""),
                       {},
                       {125},
                       2,
                       1,
                       0,
                       {},
                       {},
                       {},
                       {},
                       {},
                       {},
                       {},
                       {}}};

  deps_wrapper.deps.billing.Update(true, new_contracts, new_balances, {});

  //  deps_wrapper.billing.client_to_contract_ids_.emplace(
  //      "client_400000000588", std::set<int>{296806, 296807, 297586});

  deps_wrapper.deps.billing_clients.insert(
      {"400000000588",
       {"client_400000000588", "400000000588", kSampleTimePoint1}});

  deps_wrapper.deps.contracts_for_parks = utils::GetActiveGeneralContracts(
      GetParkIds(deps_wrapper.deps.parks), deps_wrapper.deps.billing,
      deps_wrapper.deps.billing_clients);

  EXPECT_TRUE(
      !deps_wrapper.deps.contracts_for_parks.at(park400000000588.park_id)
           .empty());
  auto check_contracts =
      deps_wrapper.deps.countries
          .at(deps_wrapper.deps.cities.at(account.city_id).country)
          .check_contracts;
  utils::ProcessPark(
      park400000000588, account, deps_wrapper.deps.contracts_for_parks,
      deps_wrapper.deps.billing_clients, deps_wrapper.deps.field_changes,
      check_contracts, deps_wrapper.deps.config);

  EXPECT_TRUE(park400000000588.deactivated);
  ASSERT_TRUE(bool(park400000000588.deactivated_reason));
  EXPECT_EQ(deactivation_reasons::kLowBalance,
            *park400000000588.deactivated_reason);
}

TEST(ParkActivator, TestProcessParkUnregistered) {
  auto now = ::utils::datetime::Stringtime("2015-3-22", "UTC", "%Y-%m-%d");
  ::utils::datetime::MockNowSet(now);
  auto park_unregistered = models::Park{
      "park_unregistered",
      false,
      std::nullopt,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      0,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
  };
  auto account = models::Account{
      "park_unregistered",
      "city1",
      std::nullopt,
      -5000.0,
      -5000.0,
      {},
      std::nullopt,
      std::nullopt,
      false,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      std::nullopt,
  };
  auto deps_wrapper = MockDeps();
  deps_wrapper.parks.push_back(park_unregistered);
  auto check_contracts =
      deps_wrapper.countries.at(deps_wrapper.cities.at(account.city_id).country)
          .check_contracts;
  utils::ProcessPark(
      park_unregistered, account, deps_wrapper.deps.contracts_for_parks,
      deps_wrapper.deps.billing_clients, deps_wrapper.deps.field_changes,
      check_contracts, deps_wrapper.deps.config);

  EXPECT_TRUE(park_unregistered.deactivated);
  ASSERT_TRUE(bool(park_unregistered.deactivated_reason));
  EXPECT_EQ(deactivation_reasons::kNotRegistered,
            *park_unregistered.deactivated_reason);
}

TEST(ParkActivator, TestChangeFieldValueAndRecord) {
  auto deps_wrapper = MockDeps();
  auto& park1 = deps_wrapper.parks.front();
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  account1.threshold_dynamic = 0.0;

  EXPECT_TRUE(deps_wrapper.deps.field_changes.empty());

  utils::ChangeFieldValueAndRecord(
      deps_wrapper.deps.field_changes, park1, &models::Park::deactivated,
      &models::Park::deactivated_reason, "deactivated", false);

  EXPECT_TRUE(deps_wrapper.deps.field_changes.empty());

  utils::ChangeFieldValueAndRecord(
      deps_wrapper.deps.field_changes, park1, &models::Park::deactivated,
      &models::Park::deactivated_reason, "threshold_dynamic", true);

  ASSERT_EQ(1u, deps_wrapper.deps.field_changes.size());

  const auto& field_change =
      deps_wrapper.deps.field_changes[park1.park_id]["threshold_dynamic"];

  EXPECT_EQ(park1.park_id, field_change.park_id);
  EXPECT_EQ("threshold_dynamic", field_change.field_name);
  ASSERT_TRUE(bool(field_change.before));
  EXPECT_EQ("false", *field_change.before);
  ASSERT_TRUE(bool(field_change.after));
  EXPECT_EQ("true", *field_change.after);
}

TEST(ParkActivator, TestActivateAndRecord) {
  auto deps_wrapper = MockDeps();
  auto& park1 = deps_wrapper.parks.front();
  auto& account1 = deps_wrapper.accounts[park1.park_id];
  park1.deactivated = false;

  EXPECT_TRUE(deps_wrapper.deps.field_changes.empty());

  utils::ActivateAndRecord(park1, account1, false, {}, false, {}, {},
                           deps_wrapper.deps.field_changes);

  EXPECT_TRUE(deps_wrapper.deps.field_changes.empty());
  EXPECT_FALSE(park1.deactivated);
  EXPECT_FALSE(bool(park1.deactivated_reason));

  utils::ActivateAndRecord(
      park1, account1, true, deactivation_reasons::kLowBalance, true,
      deactivation_reasons::kLowBalance, {}, deps_wrapper.deps.field_changes);
  EXPECT_TRUE(park1.deactivated);
  EXPECT_TRUE(bool(park1.deactivated_reason));
  EXPECT_EQ(deactivation_reasons::kLowBalance, *park1.deactivated_reason);
  EXPECT_EQ(2u, deps_wrapper.deps.field_changes[park1.park_id].size());

  park1.park_id = "park_id_1_1";
  utils::ActivateAndRecord(
      park1, account1, true, deactivation_reasons::kLowBalance, true,
      deactivation_reasons::kLowBalance, {}, deps_wrapper.deps.field_changes);
  EXPECT_TRUE(park1.deactivated);
  EXPECT_TRUE(bool(park1.deactivated_reason));
  EXPECT_EQ(deactivation_reasons::kLowBalance, *park1.deactivated_reason);
  EXPECT_TRUE(deps_wrapper.deps.field_changes[park1.park_id].empty());

  park1.park_id = "park_id_1_2";
  utils::ActivateAndRecord(park1, account1, true,
                           deactivation_reasons::kNoActiveContracts, true,
                           deactivation_reasons::kNoActiveContracts, {},
                           deps_wrapper.deps.field_changes);
  EXPECT_TRUE(park1.deactivated);
  EXPECT_TRUE(bool(park1.deactivated_reason));
  EXPECT_EQ(deactivation_reasons::kNoActiveContracts,
            *park1.deactivated_reason);
  EXPECT_EQ(2u, deps_wrapper.deps.field_changes[park1.park_id].size());

  park1.park_id = "park_id_1_3";
  utils::ActivateAndRecord(park1, account1, false, {}, false, {}, {},
                           deps_wrapper.deps.field_changes);
  EXPECT_FALSE(park1.deactivated);
  EXPECT_FALSE(bool(park1.deactivated_reason));
  EXPECT_EQ(2u, deps_wrapper.deps.field_changes[park1.park_id].size());
}

TEST(ParkActivator, TestMoscowToUtc) {
  auto input =
      ::utils::datetime::Stringtime("2015-3-22T12:00:00", "UTC", kTimeFormat);
  auto expected =
      ::utils::datetime::Stringtime("2015-3-22T9:00:00", "UTC", kTimeFormat);
  auto test = components::detail::MoscowToUtc(input);
  EXPECT_EQ(expected, test)
      << "Actual: " << ::utils::datetime::Timestring(test);
}

}  // namespace parks_activation
