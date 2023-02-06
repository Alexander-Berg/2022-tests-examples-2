#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/schedule.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>
#include <utils/schedule_converter.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoSchedule> kOldResponseSchedules = {
    handlers::PromoSchedule{1, 10, 20},
};

const std::vector<handlers::PromoSchedule> kNewResponseSchedules = {
    handlers::PromoSchedule{1, 1, 2},    handlers::PromoSchedule{2, 1, 2},
    handlers::PromoSchedule{3, 0, 5},    handlers::PromoSchedule{4, 5, 1440},
    handlers::PromoSchedule{5, 0, 1440}, handlers::PromoSchedule{6, 10, 12},
};

std::vector<schedule::Schedule> MakeDiscountSchedulesAllDays() {
  return {formats::json::FromString(R"(
    {
    "timezone": "LOCAL",
    "intervals": [
        {
        "exclude": false,
        "day": [1,2,3,4,5,6,7]
        }
    ]
    }
    )")
              .As<schedule::Schedule>()};
}

std::vector<schedule::Schedule> MakeOldDiscountSchedules() {
  return {formats::json::FromString(R"(
    {
    "timezone": "LOCAL",
    "intervals": [
        {
        "exclude": false,
        "day": [1]
        },
        {
        "exclude": false,
        "daytime": [{"from": "00:10:00", "to": "00:20:00"}]
        }
    ]
    }
    )")
              .As<schedule::Schedule>()};
}

std::vector<schedule::Schedule> MakeDiscountSchedules(
    const std::vector<handlers::PromoSchedule>& res) {
  return utils::ConvertScheduleToSchedule(res);
}

formats::json::ValueBuilder MakeStorageSchedules(
    const std::vector<handlers::PromoSchedule>& res) {
  formats::json::ValueBuilder schedules;
  schedules["schedule"] = res;
  return schedules;
}

}  // namespace

TEST(Schedule, check_feature_empty_old_values) {
  handlers::PromoRequest data;
  models::PromoSettings settings;
  Schedule schedule(Validator(), settings, {}, data);

  handlers::Promo response;
  handlers::Promo new_response;
  schedule.UpdateResponse(response);
  ASSERT_EQ(response, new_response);

  types::StoredDataRaw stored_data;
  types::StoredDataRaw new_stored_data;
  schedule.UpdateStoredData(stored_data);
  ASSERT_EQ(stored_data, new_stored_data);

  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw new_discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeDiscountSchedulesAllDays(),
      {}, {}, {}, {}, {}, {}, {}, {}};
  schedule.UpdateDiscountData(discount_data);
  ASSERT_EQ(discount_data, new_discount_data);
}

TEST(Schedule, check_feature_with_old_values) {
  handlers::PromoRequest data;
  models::PromoSettings settings;
  Schedule schedule(Validator(), settings, {}, data);

  handlers::Promo response = {
      1, {}, "name", {}, {}, {}, {}, {}, kOldResponseSchedules, {}, {}};
  handlers::Promo new_response = {1,  {}, "name", {}, {}, {},
                                  {}, {}, {},     {}, {}};
  schedule.UpdateResponse(response);
  ASSERT_EQ(response, new_response);

  types::StoredDataRaw stored_data = {
      {1, 2}, {}, {}, {}, {}, MakeStorageSchedules(kOldResponseSchedules)};
  types::StoredDataRaw new_stored_data = {
      {1, 2}, {}, {}, {}, {}, MakeStorageSchedules(kOldResponseSchedules)};
  schedule.UpdateStoredData(stored_data);
  ASSERT_EQ(stored_data, new_stored_data);

  types::DiscountDataRaw discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeOldDiscountSchedules(),
      {}, {}, {}, {}, {}, {}, {}, {}};
  types::DiscountDataRaw new_discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeDiscountSchedulesAllDays(),
      {}, {}, {}, {}, {}, {}, {}, {}};
  schedule.UpdateDiscountData(discount_data);
  ASSERT_EQ(discount_data, new_discount_data);
}

TEST(Schedule, check_feature_with_schedule_empty_old_values) {
  handlers::PromoRequest data = {{}, {}, {}, {}, {},
                                 {}, {}, {}, {}, kNewResponseSchedules};
  models::PromoSettings settings;
  Schedule schedule(Validator(), settings, {}, data);

  handlers::Promo response;
  handlers::Promo new_response = {
      {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseSchedules, {}, {}};
  ;
  schedule.UpdateResponse(response);
  ASSERT_EQ(response, new_response);

  types::StoredDataRaw stored_data;
  types::StoredDataRaw new_stored_data = {
      {}, {}, {}, {}, {}, MakeStorageSchedules(kNewResponseSchedules)};
  schedule.UpdateStoredData(stored_data);
  ASSERT_EQ(stored_data, new_stored_data);

  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw new_discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeDiscountSchedules(kNewResponseSchedules),
      {}, {}, {}, {}, {}, {}, {}, {}};
  schedule.UpdateDiscountData(discount_data);
  ASSERT_EQ(discount_data, new_discount_data);
}

TEST(Schedule, check_feature_with_schedule_with_old_values) {
  handlers::PromoRequest data = {{}, {}, {}, {}, {},
                                 {}, {}, {}, {}, kNewResponseSchedules};
  models::PromoSettings settings;
  Schedule schedule(Validator(), settings, {}, data);

  handlers::Promo response = {
      1, {}, "name", {}, {}, {}, {}, {}, kOldResponseSchedules, {}, {}};
  handlers::Promo new_response = {
      1, {}, "name", {}, {}, {}, {}, {}, kNewResponseSchedules, {}, {}};
  schedule.UpdateResponse(response);
  ASSERT_EQ(response, new_response);

  types::StoredDataRaw stored_data = {
      {1, 2}, {}, {}, {}, {}, MakeStorageSchedules(kOldResponseSchedules)};
  types::StoredDataRaw new_stored_data = {
      {1, 2}, {}, {}, {}, {}, MakeStorageSchedules(kNewResponseSchedules)};
  schedule.UpdateStoredData(stored_data);
  ASSERT_EQ(stored_data, new_stored_data);

  types::DiscountDataRaw discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeOldDiscountSchedules(),
      {}, {}, {}, {}, {}, {}, {}, {}};
  types::DiscountDataRaw new_discount_data = {
      {}, {}, {}, {}, {}, {}, {}, MakeDiscountSchedules(kNewResponseSchedules),
      {}, {}, {}, {}, {}, {}, {}, {}};
  schedule.UpdateDiscountData(discount_data);
  ASSERT_EQ(discount_data, new_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
