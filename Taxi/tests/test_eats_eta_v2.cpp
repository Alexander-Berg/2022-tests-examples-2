#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/eats/eta/resources/v2.hpp>
#include <ml/eats/eta/views/v2/features_extractor.hpp>
#include <ml/eats/eta/views/v2/predictor.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats_eta_v2");
}  // namespace

TEST(EatsEtaResourcesV0, load_static_resources) {
  auto storage = ml::eats::eta::resources::v2::LoadStaticResourcesFromDir(
      kTestDataDir + "/static_resources");

  // place taken target stats
  auto tp = ml::common::datetime::Stringtime("2020-12-01T15:38:06+03:00", "UTC",
                                             "%Y-%m-%dT%H:%M:%E*S%Ez");
  auto stats = storage.GetPlaceStatsTaken(34621, tp);
  ASSERT_TRUE(stats.has_value());
  ASSERT_DOUBLE_EQ(stats->ml_const_time, 32.775);
  ASSERT_DOUBLE_EQ(stats->hour_of_day.mean_time, 32.57631578947369);

  // place taken target stats no slice
  tp = ml::common::datetime::Stringtime("2020-12-01T10:38:06+03:00", "UTC",
                                        "%Y-%m-%dT%H:%M:%E*S%Ez");
  stats = storage.GetPlaceStatsTaken(34621, tp);
  ASSERT_TRUE(stats.has_value());
  ASSERT_DOUBLE_EQ(stats->hour_of_day.mean_time, 0);

  // place taken target stats no place
  stats = storage.GetPlaceStatsTaken(215, tp);
  ASSERT_FALSE(stats.has_value());

  // brand taken target stats
  tp = ml::common::datetime::Stringtime("2020-12-01T15:38:06+03:00", "UTC",
                                        "%Y-%m-%dT%H:%M:%E*S%Ez");
  stats = storage.GetBrandStatsTaken(2865, tp);
  ASSERT_TRUE(stats.has_value());
  ASSERT_DOUBLE_EQ(stats->ml_const_time, 32.775);
  ASSERT_DOUBLE_EQ(stats->hour_of_day.mean_time, 32.57631578947369);
  ASSERT_DOUBLE_EQ(stats->round_hour_of_week.median_time, 24.366666666666667);

  // place ready target stats
  tp = ml::common::datetime::Stringtime("2020-12-01T15:38:06+03:00", "UTC",
                                        "%Y-%m-%dT%H:%M:%E*S%Ez");
  stats = storage.GetPlaceStatsReady(34621, tp);
  ASSERT_TRUE(stats.has_value());
  ASSERT_DOUBLE_EQ(stats->hour_of_day.mean_time, 31.57631578947369);

  // brand ready target stats
  tp = ml::common::datetime::Stringtime("2020-12-01T15:38:06+03:00", "UTC",
                                        "%Y-%m-%dT%H:%M:%E*S%Ez");
  stats = storage.GetBrandStatsReady(2865, tp);
  ASSERT_TRUE(stats.has_value());
  ASSERT_DOUBLE_EQ(stats->hour_of_day.mean_time, 30.57631578947369);
}

TEST(EatsEtaFeatureExtractorV0, feature_extractor) {
  auto request =
      ml::common::FromJsonString<ml::eats::eta::views::v2::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  // config with courier_features disabled
  auto config =
      ml::common::FromJsonString<ml::eats::eta::views::v2::FeaturesConfig>(
          ml::common::ReadFileContents(kTestDataDir + "/features_config.json"));
  auto features_extractor = ml::eats::eta::views::v2::FeaturesExtractor(config);
  auto storage = ml::eats::eta::resources::v2::LoadStaticResourcesFromDir(
      kTestDataDir + "/static_resources");

  auto features = features_extractor.Apply(request, storage, "total");
  auto categorical = features.categorical;
  auto numerical = features.numerical;
  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();

  ASSERT_EQ(categorical_size, 17ul);
  ASSERT_EQ(numerical_size, 149ul);
  ASSERT_EQ(categorical.size(), categorical_size);
  ASSERT_EQ(numerical.size(), numerical_size);

  ASSERT_EQ(categorical.at(0), "34621");  // place id
  ASSERT_EQ(categorical.at(3), "2");      // price category id
  ASSERT_EQ(categorical.at(4), "ucft");   // geohash 4
  ASSERT_EQ(categorical.at(15), "1");     // weekday

  ASSERT_FLOAT_EQ(numerical.at(0), 32.775);      // base time
  ASSERT_FLOAT_EQ(numerical.at(14), 2334.3735);  // distance place-user
  // (27.7 * 12 + 32.775 * 10) / (12 + 10) = 30.006818...
  ASSERT_FLOAT_EQ(numerical.at(30), 30.006818);  // place median by weekday
  // (27.7 * 12 + 32.775 * 50) / (12 + 50) = 31.792741...
  ASSERT_FLOAT_EQ(numerical.at(80), 31.792741);  // brand median by weekday
  ASSERT_FLOAT_EQ(numerical.at(130), 2);         // len of ids in cart

  // config with courier_features enabled
  config.use_courier_features = true;
  features_extractor = ml::eats::eta::views::v2::FeaturesExtractor(config);

  features = features_extractor.Apply(request, storage, "total");
  categorical = features.categorical;
  numerical = features.numerical;
  categorical_size = features_extractor.GetCatFeaturesSize();
  numerical_size = features_extractor.GetNumFeaturesSize();

  ASSERT_EQ(categorical_size, 17ul);
  // 35 courier features is added to numerical  features
  ASSERT_EQ(numerical_size, size_t(149 + 35));
  ASSERT_EQ(categorical.size(), categorical_size);
  ASSERT_EQ(numerical.size(), numerical_size);
  // old features
  ASSERT_FLOAT_EQ(numerical.at(0), 32.775);      // base time
  ASSERT_FLOAT_EQ(numerical.at(14), 2334.3735);  // distance place-user
  ASSERT_FLOAT_EQ(numerical.at(30), 30.006818);  // place median by weekday
  ASSERT_FLOAT_EQ(numerical.at(80), 31.792741);  // brand median by weekday
  ASSERT_FLOAT_EQ(numerical.at(130), 2);         // len of ids in cart
  // new courier features
  ASSERT_FLOAT_EQ(numerical.at(149), 3.0);        // number of couriers
  ASSERT_FLOAT_EQ(numerical.at(149 + 5), 3.0);    // couriers without orders
  ASSERT_FLOAT_EQ(numerical.at(149 + 15), -1.0);  // equal logistic group true

  config.use_courier_features = false;
  features_extractor = ml::eats::eta::views::v2::FeaturesExtractor(config);

  // also ready target features
  features = features_extractor.Apply(request, storage, "ready");

  categorical = features.categorical;
  numerical = features.numerical;
  categorical_size = features_extractor.GetCatFeaturesSize();
  numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 17ul);
  ASSERT_EQ(numerical_size, 149ul);
  ASSERT_EQ(categorical.size(), categorical_size);
  ASSERT_EQ(numerical.size(), numerical_size);

  // also taken target features (taken is default)
  features = features_extractor.Apply(request, storage);

  categorical = features.categorical;
  numerical = features.numerical;
  categorical_size = features_extractor.GetCatFeaturesSize();
  numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 17ul);
  ASSERT_EQ(numerical_size, 149ul);
  ASSERT_EQ(categorical.size(), categorical_size);
  ASSERT_EQ(numerical.size(), numerical_size);

  // config with zone_features enabled
  config.use_courier_features = true;
  config.use_zone_features = true;
  features_extractor = ml::eats::eta::views::v2::FeaturesExtractor(config);

  features = features_extractor.Apply(request, storage, "total");
  categorical = features.categorical;
  numerical = features.numerical;
  categorical_size = features_extractor.GetCatFeaturesSize();
  numerical_size = features_extractor.GetNumFeaturesSize();

  ASSERT_EQ(categorical_size, 19ul);
  ASSERT_EQ(numerical_size, size_t(149 + 35 + 2));
  ASSERT_EQ(categorical.size(), categorical_size);
  ASSERT_EQ(numerical.size(), numerical_size);
  // old courier features
  ASSERT_FLOAT_EQ(numerical.at(149), 3.0);        // number of couriers
  ASSERT_FLOAT_EQ(numerical.at(149 + 5), 3.0);    // couriers without orders
  ASSERT_FLOAT_EQ(numerical.at(149 + 15), -1.0);  // equal logistic group true
  // new features
  ASSERT_FLOAT_EQ(numerical.at(149 + 35 + 0), 31.0);
  ASSERT_FLOAT_EQ(numerical.at(149 + 35 + 1), 21.0);
  ASSERT_EQ(categorical.at(17), "pedestrian");
  ASSERT_EQ(categorical.at(18), "1308413");
}

TEST(EatsEtaPredictorV0, predictor) {
  auto config = ml::eats::eta::resources::v2::PredictorLoadConfig();
  config.dir_path = kTestDataDir;
  auto predictor = ml::eats::eta::resources::v2::CreatePredictor(config, true);

  auto request =
      ml::common::FromJsonString<ml::eats::eta::views::v2::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  auto params = ml::eats::eta::views::v2::PredictorParams();

  auto storage = ml::eats::eta::resources::v2::LoadStaticResourcesFromDir(
      kTestDataDir + "/static_resources");

  // test default with mocked catboost
  auto times = predictor->Apply(request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, request.delivery_time + 10.0);
  // 10+21 -> 31 -> 21-31 -> 25-35
  ASSERT_EQ(times.boundaries.min, 25);
  ASSERT_EQ(times.boundaries.max, 35);

  // test place increment
  request.place_info.place_increment = 15;
  times = predictor->Apply(request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 25.0);
  ASSERT_FLOAT_EQ(times.delivery_time, request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, request.delivery_time + 25.0);
  // 10+21+15 -> 46 -> 36-46 -> 40-50
  ASSERT_EQ(times.boundaries.min, 40);
  ASSERT_EQ(times.boundaries.max, 50);
  request.place_info.place_increment = 0;

  // test default with mocked catboost + ready model
  params.ready_predictor_enabled = true;
  times = predictor->Apply(request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, request.delivery_time + 10.0);
  // 10+21 -> 31 -> 21-31 -> 25-35
  ASSERT_EQ(times.boundaries.min, 25);
  ASSERT_EQ(times.boundaries.max, 35);
  params.ready_predictor_enabled = false;

  // test default with mocked catboost + total model
  params.total_predictor_enabled = true;

  times = predictor->Apply(request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.total_time, 10.0);
  // 10 -> 0-10 -> [left boundary >= 10 -> shift] -> 10-20
  ASSERT_EQ(times.boundaries.min, 10);
  ASSERT_EQ(times.boundaries.max, 20);
  params.total_predictor_enabled = false;

  // test shops
  auto new_request = request;
  new_request.place_info.place_type = "shop";
  auto ml_const_time = storage
                           .GetPlaceStatsTaken(request.place_info.place_id,
                                               request.predicting_at)
                           .value()
                           .ml_const_time;

  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, ml_const_time);

  // test slug
  new_request = request;
  new_request.request_type = "slug";
  params.slug = "const";
  params.shift_total_time = 5;
  params.shift_const_cooking_time = 3;
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, ml_const_time + 3);
  ASSERT_FLOAT_EQ(times.total_time,
                  ml_const_time + new_request.delivery_time + 3);
  params.shift_total_time = 0;
  params.shift_const_cooking_time = 0;

  // test min orders num
  // we need different static resources (place taken resources is enough)
  new_request = request;
  ml::eats::eta::resources::v2::StaticResourcesLoadConfig
      static_resource_config;
  static_resource_config.dir_path = kTestDataDir + "/static_resources";
  static_resource_config.places_stats_taken =
      "resource_place_taken_few_orders.txt";

  auto new_storage = ml::eats::eta::resources::v2::LoadStaticResourcesFromDir(
      static_resource_config);

  times = predictor->Apply(new_request, params, new_storage);
  ASSERT_FLOAT_EQ(times.cooking_time,
                  request.place_info.average_preparation_time);

  // test privilege brand
  new_request = request;
  params.custom_params = ml::eats::eta::views::v2::CustomParams{
      request.place_info.brand_id, 0, 1, 0, 0, {}, {}, {}, {}, false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time,
                  request.place_info.average_preparation_time - 1);
  params.custom_params.reset();

  params.custom_params = ml::eats::eta::views::v2::CustomParams{
      request.place_info.brand_id, 0, 0, 15, 0, {}, {}, {}, {}, false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.total_time,
                  request.delivery_time + times.cooking_time + 15);
  params.custom_params.reset();

  params.custom_params = ml::eats::eta::views::v2::CustomParams{
      request.place_info.brand_id, 0, 0, 15, 0, 20, {}, {}, {}, false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.total_time, 20);
  params.custom_params.reset();

  params.custom_params = ml::eats::eta::views::v2::CustomParams{
      request.place_info.brand_id, 0, 0, 0, 10, {}, {}, {}, {}, false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time,
                  request.place_info.average_preparation_time + 10);
  params.custom_params.reset();

  // test couriers heuristics (should increase delivery time)
  new_request = request;
  params.couriers_candidates_parameters =
      ml::eats::eta::views::v2::PredictorParamsCouriersCandidatesParameters{
          true,
          false,
          false,
          "max",
          1000,
          1200,
          500,
          100,
          200,
          300,
          std::vector<std::string>{"created", "accepted", "arrived_to_source"},
          0.5,
          3,
          1800,
          400};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_TRUE(times.delivery_time > request.delivery_time + 1);
  params.couriers_candidates_parameters.reset();

  // test customized region time offset
  params.region_offset = 20;
  times = predictor->Apply(request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, request.delivery_time + 10.0);
  // 10+21 -> 31 -> 31-51 -> 35-55
  ASSERT_EQ(times.boundaries.min, 35);
  ASSERT_EQ(times.boundaries.max, 55);

  // test default rough rounding
  new_request = request;
  params.rounding_params = {{{60, 30}}, false};
  times = predictor->Apply(new_request, params, storage);
  // should work just like with no rounding params
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, request.delivery_time + 10.0);
  // 10+21 -> 31 -> 31-51 -> 35-55
  ASSERT_EQ(times.boundaries.min, 35);
  ASSERT_EQ(times.boundaries.max, 55);

  new_request.delivery_time = 64;
  times = predictor->Apply(new_request, params, storage);
  // round to 60-90 boundaries
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+64 -> 74 -> /min{74,94}/ -> 74 -> 60-90
  ASSERT_EQ(times.boundaries.min, 60);
  ASSERT_EQ(times.boundaries.max, 90);

  params.region_offset = -10;
  new_request.delivery_time = 64;
  times = predictor->Apply(new_request, params, storage);
  // round to 60-90 boundaries
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+64 -> 74 -> /min{74,64}/ -> 64 -> 60-90
  ASSERT_EQ(times.boundaries.min, 60);
  ASSERT_EQ(times.boundaries.max, 90);

  params.region_offset = -10;
  new_request.delivery_time = 54;
  times = predictor->Apply(new_request, params, storage);
  // just like default rounding as lower bound is lower than threshold
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+54 -> 64 -> /min{64,54}/ -> 54 -> 55-65
  ASSERT_EQ(times.boundaries.min, 55);
  ASSERT_EQ(times.boundaries.max, 65);

  // corner case: we don't want 57 -> 60-70 rounding,
  // it should be 60-90 for the sake of consistency
  params.region_offset = -10;
  new_request.delivery_time = 57;
  times = predictor->Apply(new_request, params, storage);
  // just like default rounding as lower bound is lower than threshold
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+57 -> 67 -> /min{67,57}/ -> 57 -> 60-90
  ASSERT_EQ(times.boundaries.min, 60);
  ASSERT_EQ(times.boundaries.max, 90);

  // rounding for 20min < prediction < 60min and 20min step
  // also ensure that default threshold is ignored
  params.region_offset = -10;
  new_request.delivery_time = 27;
  params.rounding_params = {{{60, 30}, {20, 20}}, false};
  times = predictor->Apply(new_request, params, storage);
  // for smaller threshold
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+27 -> 37 -> /min{37,27}/ -> 27 -> 20-40
  ASSERT_EQ(times.boundaries.min, 20);
  ASSERT_EQ(times.boundaries.max, 40);

  new_request.delivery_time = 57;
  times = predictor->Apply(new_request, params, storage);
  // for higher threshold
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+57 -> 67 -> /min{67,57}/ -> 57 -> 60-90
  ASSERT_EQ(times.boundaries.min, 60);
  ASSERT_EQ(times.boundaries.max, 90);

  new_request.delivery_time = 7;
  times = predictor->Apply(new_request, params, storage);
  // for no threshold
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+7 -> 17 -> /min{17,7}/ -> 10-20
  ASSERT_EQ(times.boundaries.min, 10);
  ASSERT_EQ(times.boundaries.max, 20);

  // new offset formula
  new_request.delivery_time = 21;
  params.region_offset = -5;
  params.window = 15;  // unusual value
  params.rounding_params.reset();
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+21 -> 31 -> round{[31-5; 31-5+15]} -> 30-45
  ASSERT_EQ(times.boundaries.min, 30);
  ASSERT_EQ(times.boundaries.max, 45);
  // another test
  params.region_offset = 10;
  params.window = 10;
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+21 -> 31 -> round{[31+10; 31+10+10]} -> 45-55
  ASSERT_EQ(times.boundaries.min, 45);
  ASSERT_EQ(times.boundaries.max, 55);
  // rough rounding still works
  params.rounding_params = {{{60, 30}, {20, 20}}, false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+21 -> 31 -> round{31+10} -> 45 -> 40-60
  ASSERT_EQ(times.boundaries.min, 40);
  ASSERT_EQ(times.boundaries.max, 60);

  // check if custom slots work
  new_request.retail_slot_params = {20, 5};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time,
                  new_request.delivery_time +
                      new_request.retail_slot_params.value().shift +
                      new_request.retail_slot_params.value().time_to_slot);
  // 20+21+5 -> 46 -> +region offset -> round{56} -> 60 -> 60-90
  ASSERT_EQ(times.boundaries.min, 60);
  ASSERT_EQ(times.boundaries.max, 90);
  new_request.retail_slot_params.reset();

  // check custom rounding
  params.custom_params =
      ml::eats::eta::views::v2::CustomParams{request.place_info.brand_id,
                                             100,
                                             100,
                                             0,
                                             0,
                                             {},
                                             {},
                                             {},
                                             {{{30, 30}}},
                                             false};
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+21 -> 31 -> round{31+10} -> 45 -> 30-60
  ASSERT_EQ(times.boundaries.min, 30);
  ASSERT_EQ(times.boundaries.max, 60);

  params.custom_params.reset();

  // check if always_use_last_rule works as assumed
  params.rounding_params = {{{60, 30}, {20, 20}}, true};
  new_request.delivery_time = 5;
  params.region_offset = 0;
  times = predictor->Apply(new_request, params, storage);
  ASSERT_FLOAT_EQ(times.cooking_time, 10.0);
  ASSERT_FLOAT_EQ(times.delivery_time, new_request.delivery_time);
  ASSERT_FLOAT_EQ(times.total_time, new_request.delivery_time + 10.0);
  // 10+5 -> 15 -> round{15+0} -> 15 -> [closest range] -> 20-40
  ASSERT_EQ(times.boundaries.min, 20);
  ASSERT_EQ(times.boundaries.max, 40);

  new_request.delivery_time = 21;
  params.region_offset = -10;
  params.window.reset();
  params.rounding_params.reset();

  // test queue heuristics (old version, but still have to work)
  ml::eats::eta::views::v2::PredictorParamsQueueParams pred_params;
  pred_params.threshold = 10;
  pred_params.shift = 5;
  pred_params.linear_coef = 1.0;
  params.queue_params = pred_params;
  // requested place is a shop but just ignore it
  new_request.orders_queue =
      std::vector<ml::eats::eta::views::v2::ShopActiveOrder>(5);

  // should work as usual
  times = predictor->Apply(new_request, params, storage);
  ASSERT_EQ(times.boundaries.min, 25);
  ASSERT_EQ(times.boundaries.max, 35);

  new_request.orders_queue =
      std::vector<ml::eats::eta::views::v2::ShopActiveOrder>(15);
  // should add 15*1+5=20 min, so boundaries increase 20 min too
  times = predictor->Apply(new_request, params, storage);
  ASSERT_EQ(times.boundaries.min, 45);
  ASSERT_EQ(times.boundaries.max, 55);

  // pickers info with very long waiting time
  new_request.pickers_info =
      ml::eats::eta::views::v2::ShopPickersInfo{24000, 0, 0};
  params.queue_params.value().est_wait_time_coef = 0.5;
  times = predictor->Apply(new_request, params, storage);
  // should add min(15*1+5+0.5*400=220, 150) = 150, so boundaries increase by
  // 150
  ASSERT_EQ(times.boundaries.min, 175);
  ASSERT_EQ(times.boundaries.max, 185);

  // check logging
  std::string logs_test = "";
  std::string logs_expected = fmt::format(
      "Retail orders queue addition: {} min with {} total pickers, {} "
      "free pickers, {} min est_waiting_time and {} orders in queue. ",
      150, 0, 0, 24000 / 60., 15);
  times = predictor->Apply(new_request, params, storage, &logs_test);
  ASSERT_EQ(logs_test, logs_expected);

  // test that there will be no addition for far future predictions
  // as now() may vary, let's check that queue addition has no effect
  auto original_time = new_request.predicting_at;

  new_request.predicting_at =
      std::chrono::system_clock::now() + std::chrono::minutes(120);
  pred_params.threshold = 1000;  // disable heuristics
  auto times_no_queue = predictor->Apply(new_request, params, storage);
  pred_params.threshold = 0;  // enable heuristics
  times = predictor->Apply(new_request, params, storage);

  ASSERT_EQ(times_no_queue.boundaries.min, times.boundaries.min);
  ASSERT_EQ(times_no_queue.boundaries.max, times.boundaries.max);

  new_request.predicting_at = original_time;
  new_request.orders_queue.reset();
  new_request.pickers_info.reset();
  params.queue_params.reset();
}
