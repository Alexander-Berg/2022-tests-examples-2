#include "views/taxiontheway.cpp"
#include "utils/taximeter_version.hpp"

#include <common/test_config.hpp>

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <json/json.h>

#include <models/api_over_data/car_info.hpp>
#include <models/api_over_data/driver_info.hpp>
#include <models/tariffs.hpp>
#include <mongo/shard_processing.hpp>
#include <utils/translation_mock.hpp>

namespace {
class IdShardProcessor : public utils::mongo::ShardProcessor {
  bool enabled() const override final { return false; }

  ::mongo::BSONObj DoModifySearchQuery(
      const ::mongo::BSONObj& query) const override final {
    return query;
  }

  ::mongo::BSONObj DoModifyUpdateQuery(
      const ::mongo::BSONObj& query) const override final {
    return query;
  }
};
}  // namespace

class TaxiOnTheWayTest : public ::testing::Test {
 public:
  TaxiOnTheWayTest()
      : translations_(new MockTranslations(true)),
        config_(new config::Config(config::DocsMapForTest())) {}

 protected:
  std::shared_ptr<MockTranslations> translations_;
  std::shared_ptr<const config::Config> config_;
};

boost::optional<Json::Value> ExpectedCostMessage(
    const std::string& final_cost_with_currency,
    const std::string& waiting_cost, int waiting_time,
    const l10n::Translations& translations) {
  ff::ArgsList args{
      {"final_cost_with_currency", final_cost_with_currency},
      {"waiting_cost", waiting_cost},
      {"waiting_time", std::to_string(waiting_time)},
  };
  boost::optional<Json::Value> response;
  response = translations
                 .getTemplate("client_messages",
                              "taxiontheway.paid_waiting_cost_message", "en")
                 .SubstituteArgs(args);
  return response;
}

using testing::ReturnRef;

namespace test_access {
class MockData : public views::taxiontheway::Data {
 public:
  MockData(TimeStorage& prof_ts, const views::taxiontheway::Input& input,
           const utils::mongo::Collections& collections,
           const RedisClientPtr& redis, const utils::Async& async,
           const common::Experiments& experiments,
           const models::tariff_settings_dict& tariff_settings_dict,
           const tariff::tariff_dict_t& tariffs,
           const models::CitiesMap& cities, const DataComponent& data,
           const models::UniqueDriversByLicenses& unique_drivers_by_licenses,
           const std::shared_ptr<clients::archive::Client>& archive,
           const std::shared_ptr<clients::order_core::Client>& order_core,
           const std::shared_ptr<clients::feedback::Client>& feedback,
           const user_api_facade::components::UserApiFacadeComponent&
               user_api_facade,
           const views::taxiontheway::ApiOverDataDeps& api_over_data_deps,
           handlers::ProtocolContext& context)
      : Data(prof_ts, input, collections, redis, async, experiments,
             tariff_settings_dict, tariffs, cities, data,
             unique_drivers_by_licenses, archive, order_core, feedback,
             user_api_facade, context,
             views::taxiontheway::ReadPreferenceConfig(), 0,
             api_over_data_deps) {}
  virtual ~MockData() {}
  MOCK_CONST_METHOD0(GetDriver, const views::taxiontheway::OrderDriver&());
  MOCK_CONST_METHOD0(GetOrder, const models::Order&());
};
}  // namespace test_access

using test_access::MockData;

TEST_F(TaxiOnTheWayTest, BuildResponse4CostMessage) {
  views::taxiontheway::Input input;
  input.locale = "en";
  input.need_format_currency = false;

  auto pool = std::make_shared<utils::mongo::Pool>(
      "mongodb://dummy/", std::chrono::seconds(10), 0, 0, 0);
  static const std::shared_ptr<utils::mongo::ShardProcessor> shard_processor =
      std::make_shared<IdShardProcessor>();
  utils::mongo::Collections empty_collections(
      pool, pool, pool, pool, pool, pool, pool, pool, pool, pool, pool,
      shard_processor, shard_processor);
  const RedisClientPtr redis;

  const utils::Async* async = nullptr;
  const common::Experiments* experiments = nullptr;
  const models::tariff_settings_dict* tariff_settings_dict = nullptr;
  const tariff::tariff_dict_t* tariffs = nullptr;
  const models::CitiesMap* cities = nullptr;
  const models::CountryMap* countries = nullptr;
  LogExtra log_extra;
  const DataComponent* data_component = nullptr;
  const models::UniqueDriversByLicenses* unique_drivers_by_licenses = nullptr;
  clients::Graphite graphite;
  std::shared_ptr<clients::archive::Client> archive = nullptr;
  std::shared_ptr<clients::order_core::Client> order_core = nullptr;
  std::shared_ptr<clients::feedback::Client> feedback = nullptr;
  user_api_facade::components::UserApiFacadeComponent* user_api_facade =
      nullptr;
  api_over_data::models::protocol::DriverInfo* driver_info = nullptr;
  api_over_data::models::protocol::ParkInfo* all_parks = nullptr;
  api_over_data::models::protocol::CarInfo* car_info = nullptr;
  models::ColorsMap* colors = nullptr;
  models::BrandModelsMap* brand_models = nullptr;
  models::PricesMap* prices = nullptr;
  handlers::ProtocolContext context(views::Args(), *config_, graphite,
                                    log_extra);

  SCOPE_TIME_PREPARE("totw", context.log_extra);

  views::taxiontheway::ApiOverDataDeps api_over_data_deps{
      *driver_info, *car_info,     *all_parks, *countries, *cities,
      *colors,      *brand_models, *prices,    *config_,
  };

  MockData data(prof_ts, input, empty_collections, redis, *async, *experiments,
                *tariff_settings_dict, *tariffs, *cities, *data_component,
                *unique_drivers_by_licenses, archive, order_core, feedback,
                *user_api_facade, api_over_data_deps,
                context);  //-V522
  views::taxiontheway::RestData rdata;
  rdata.status_for_client = "complete";

  models::Order order;
  order.calc_info.waiting_time = 714.;
  order.calc_info.waiting_cost = 20.3;

  EXPECT_CALL(data, GetOrder()).WillRepeatedly(ReturnRef(order));

  rdata.currency = "RUB";

  rdata.ride_cost_for_client = 296.6;
  rdata.cost_precision = 0;

  auto response_rub1 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  rdata.ride_cost_for_client = 296.3;
  auto response_rub2 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  ASSERT_EQ(
      utils::helpers::WriteJson(response_rub1.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("277rub", "20rub", 12, *translations_).get()));
  ASSERT_EQ(
      utils::helpers::WriteJson(response_rub2.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("276rub", "20rub", 12, *translations_).get()));

  rdata.currency = "BYN";
  rdata.ride_cost_for_client = 9.666;
  rdata.cost_precision = 2;

  order.calc_info.waiting_cost = 1.332;

  auto response_byn1 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  rdata.ride_cost_for_client = 9.663;
  auto response_byn2 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  ASSERT_EQ(
      utils::helpers::WriteJson(response_byn1.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("8.3 byn", "1.3 byn", 12, *translations_).get()));
  ASSERT_EQ(
      utils::helpers::WriteJson(response_byn2.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("8.3 byn", "1.3 byn", 12, *translations_).get()));

  rdata.currency = "UAH";
  rdata.ride_cost_for_client = 26.66;
  rdata.cost_precision = 1;
  order.calc_info.waiting_cost = 2.33;

  auto response_uah1 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  rdata.ride_cost_for_client = 26.64;
  auto response_uah2 = views::taxiontheway::BuildResponse4CostMessage(
      experiments3::models::CacheManager(), input, *translations_, data, rdata,
      context.args.app_vars, context.log_extra);

  ASSERT_EQ(
      utils::helpers::WriteJson(response_uah1.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("24.4uah", "2.3uah", 12, *translations_).get()));
  ASSERT_EQ(
      utils::helpers::WriteJson(response_uah2.get()),
      utils::helpers::WriteJson(
          ExpectedCostMessage("24.3uah", "2.3uah", 12, *translations_).get()));
}
