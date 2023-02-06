#include <gtest/gtest.h>

#include "utils.hpp"

namespace {

using eats_layout_constructor::models::DeliveryTimeFilterValue;
using eats_layout_constructor::models::FilterSlug;
using eats_layout_constructor::models::FilterType;
using eats_layout_constructor::models::RequestParams;
using eats_layout_constructor::utils::filters::GetFiltersKwarg;

}  // namespace

TEST(GetFiltersKwarg, FillDeliveryTimeValue) {
  // Проверяет, что кварг фильтров заполняется
  // как фильтров времени доставки, так и конкретным его значением
  RequestParams request_params{};
  auto& filter_v2 = request_params.filters_v2.emplace_back();
  filter_v2.type = FilterType{"delivery_time"};
  filter_v2.slug = FilterSlug{"delivery_time"};
  auto& filter_payload = filter_v2.payload.emplace();
  filter_payload.value = DeliveryTimeFilterValue{"thirty"};
  const auto filters_kwarg = GetFiltersKwarg(request_params);

  ASSERT_GT(filters_kwarg.count("delivery_time:delivery_time"), 0);
  ASSERT_GT(filters_kwarg.count("delivery_time:delivery_time:thirty"), 0);
}
