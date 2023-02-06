#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/starts_ends.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const auto kOldStarts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
const auto kNewStarts = ::utils::datetime::Stringtime("2001-03-02T00:00:00Z");
const auto kOldEnds = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
const auto kNewEnds = ::utils::datetime::Stringtime("2001-05-02T00:00:00Z");

const auto kNowBefore = ::utils::datetime::Stringtime("2001-01-01T00:00:00Z");
const auto kNowWithin = ::utils::datetime::Stringtime("2001-04-20T00:00:00Z");

const auto kValidateShift = std::chrono::seconds(600);
const auto kStartShift = std::chrono::seconds(600);

const handlers::StartsEnds kOldStartsEnds = {kOldStarts, kOldEnds};
const handlers::StartsEnds kNewStartsEnds = {kNewStarts, kNewEnds};
const handlers::StartsEnds kStartsEndsFromNow = {
    kNowWithin + kValidateShift + kStartShift, kNewEnds};

::defs::internal::discount_data::ActivePeriod kOldDiscountActivePeriod = {
    kOldStarts, kOldEnds, true, false};
::defs::internal::discount_data::ActivePeriod kNewDiscountActivePeriod = {
    kNewStarts, kNewEnds, true, true};
::defs::internal::discount_data::ActivePeriod kDiscountActivePeriodFromNow = {
    kNowWithin + kValidateShift + kStartShift, kNewEnds, true, true};

template <typename T>
T MakePromo(const handlers::StartsEnds& starts_ends) {
  T result;
  result.starts_at = starts_ends.starts;
  result.ends_at = starts_ends.ends;
  return result;
}

inline types::DiscountDataRaw MakeDiscount(
    const ::defs::internal::discount_data::ActivePeriod& active) {
  types::DiscountDataRaw discount;
  discount.active_period = active;
  return discount;
}

}  // namespace

struct StartsEndsData {
  std::chrono::system_clock::time_point mocked_now;

  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

StartsEndsData MakeStartsEndsData(
    const std::chrono::system_clock::time_point& mocked_now) {
  return {
      mocked_now,
      MakePromo<handlers::PromoRequest>(kNewStartsEnds),
      MakePromo<handlers::Promo>(kOldStartsEnds),
      MakePromo<handlers::Promo>(mocked_now == kNowBefore ? kNewStartsEnds
                                                          : kStartsEndsFromNow),
      MakePromo<types::StoredDataRaw>(kOldStartsEnds),
      MakePromo<types::StoredDataRaw>(
          mocked_now == kNowBefore ? kNewStartsEnds : kStartsEndsFromNow),
      MakeDiscount(kOldDiscountActivePeriod),
      MakeDiscount(mocked_now == kNowBefore ? kNewDiscountActivePeriod
                                            : kDiscountActivePeriodFromNow)};
}

class StartsEndsDataFull : public ::testing::TestWithParam<StartsEndsData> {};

const std::vector<StartsEndsData> kStartsEndsData{
    MakeStartsEndsData(kNowBefore), MakeStartsEndsData(kNowWithin)};

INSTANTIATE_TEST_SUITE_P(StartsEndsData, StartsEndsDataFull,
                         ::testing::ValuesIn(kStartsEndsData));

TEST_P(StartsEndsDataFull, check_starts_ends_feature) {
  auto param = GetParam();
  ::utils::datetime::MockNowSet(param.mocked_now);

  models::PromoSettings settings;
  settings.common.validate_shift = kValidateShift;
  settings.common.start_shift = kStartShift;
  auto starts_ends = StartsEnds(Validator(), settings, {}, param.data);

  starts_ends.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  starts_ends.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  starts_ends.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
