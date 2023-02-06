#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark.hpp>

#include "aggregated_park_balance.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(AggregatedParkBalanceTest, BalanceAboveLimit) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();
  balance_limit_cache->emplace("agg0", 20000.);

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();
  models::ParkBalancesMap balances{{"dbid0", 30000.}};
  models::AggregatorEntry data{{}, std::move(balances)};
  balance_cache->emplace("agg0", std::move(data));

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST(AggregatedParkBalanceTest, BalanceEqualToLimit) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();
  balance_limit_cache->emplace("agg0", 20000.);

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();
  models::ParkBalancesMap balances{{"dbid0", 20000.}};
  models::AggregatorEntry data{{}, std::move(balances)};
  balance_cache->emplace("agg0", std::move(data));

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}

TEST(AggregatedParkBalanceTest, BalanceBelowLimit) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();
  balance_limit_cache->emplace("agg0", 20000.);

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();
  models::ParkBalancesMap balances{{"dbid0", 10000.}};
  models::AggregatorEntry data{{}, std::move(balances)};
  balance_cache->emplace("agg0", std::move(data));

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}

TEST(AggregatedParkBalanceTest, AggregatorDisabled) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();
  disabled_aggregators_cache->emplace("agg0");

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();
  balance_limit_cache->emplace("agg0", 20000.);

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();
  models::ParkBalancesMap balances{{"dbid0", 30000.}};
  models::AggregatorEntry data{{}, std::move(balances)};
  balance_cache->emplace("agg0", std::move(data));

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}

TEST(AggregatedParkBalanceTest, NotAggregated) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kIgnore);
}

TEST(AggregatedParkBalanceTest, LimitMissingInCache) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();
  models::ParkBalancesMap balances{{"dbid0", 30000.}};
  models::AggregatorEntry data{{}, std::move(balances)};
  balance_cache->emplace("agg0", std::move(data));

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST(AggregatedParkBalanceTest, BalanceMissingInCache) {
  auto aggregator_ids_cache = std::make_shared<models::AggregatorIds>();
  aggregator_ids_cache->emplace("clid0", "agg0");

  auto disabled_aggregators_cache =
      std::make_shared<models::DisabledAggregators>();

  auto balance_limit_cache = std::make_shared<models::AggregatorBalanceLimit>();
  balance_limit_cache->emplace("agg0", 20000.);

  auto balance_cache = std::make_shared<models::AggregatedParkBalance>();

  cf::partners::AggregatedParkBalance filter(
      kEmptyInfo, aggregator_ids_cache, disabled_aggregators_cache,
      balance_limit_cache, balance_cache);

  cf::Context context;
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow", {}});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}
