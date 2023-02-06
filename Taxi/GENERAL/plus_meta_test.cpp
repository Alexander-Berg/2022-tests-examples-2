#include "plus_meta.hpp"

#include <variant>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace handlers::internal_v1_catalog_for_layout::post::render {

namespace {

namespace models = eats_catalog::models;
using Cashback = std::unordered_map<eats_catalog::models::PlaceId, double>;
using Tooltip = std::unordered_map<eats_catalog::models::PlaceId,
                                   external::EatsPlusTooltip>;

models::Place CreatePlace(models::PlaceInfo& place_info, int id) {
  place_info.id = models::PlaceId(id);
  models::Place place{place_info};

  return place;
}

void AssertEqual(const YandexPlusMeta& lhs, const YandexPlusMeta& rhs) {
  ASSERT_EQ(lhs.text, rhs.text);
  ASSERT_EQ(lhs.icon_url, rhs.icon_url);
  ASSERT_EQ(lhs.styles.border, rhs.styles.border);
  ASSERT_EQ(lhs.styles.rainbow, rhs.styles.rainbow);
}

}  // namespace

TEST(PlusMeta, Simple) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();

  const Context context{
      models::ShippingType::kDelivery,  // shipping_type
      models::CustomFilterType::kAny,   // block_type
  };

  const auto modifier = PlusMeta(config,
                                 Cashback{
                                     {models::PlaceId(1), 27.5232},
                                     {models::PlaceId(2), 2.2},
                                     {models::PlaceId(3), 0},
                                     {models::PlaceId(5), -12012},
                                 },
                                 {});

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 1);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "27.5232%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 2);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "2.2%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 3);
    modifier.Modify(target, place, context);

    ASSERT_TRUE(target.payload.data.meta.empty());
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 4);
    modifier.Modify(target, place, context);

    ASSERT_TRUE(target.payload.data.meta.empty());
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 5);
    modifier.Modify(target, place, context);

    ASSERT_TRUE(target.payload.data.meta.empty());
  }
}

TEST(PlusMeta, WithTooltip) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();

  const Context context{
      models::ShippingType::kDelivery,  // shipping_type
      models::CustomFilterType::kAny,   // block_type
  };

  const auto modifier =
      PlusMeta(config,
               Cashback{{models::PlaceId(1), 27.5232},
                        {models::PlaceId(2), 2.2},
                        {models::PlaceId(3), 0},
                        {models::PlaceId(5), -12012}},
               {},
               Tooltip{{models::PlaceId(1), {"1_title", "1_description"}},
                       {models::PlaceId(2), {"2_title", "2_description"}},
                       {models::PlaceId(3), {"3_title", "3_description"}},
                       {models::PlaceId(5), {"5_title", "5_description"}}});

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 1);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "27.5232%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;
    expected.details_form =
        YandexPlusMetaDetailsform{"1_title", "1_description"};

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 2);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "2.2%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;
    expected.details_form =
        YandexPlusMetaDetailsform{"2_title", "2_description"};

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }
}

TEST(PlusMeta, Empty) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();

  const Context context{
      models::ShippingType::kDelivery,  // shipping_type
      models::CustomFilterType::kAny,   // block_type
  };

  const auto modifier = PlusMeta(config, {}, {});
  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 1);
    ASSERT_NO_THROW(modifier.Modify(target, place, context));

    ASSERT_TRUE(target.payload.data.meta.empty());
  }
}

TEST(PlusMeta, Limits) {
  GTEST_SKIP();

  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();

  const Context context{
      models::ShippingType::kDelivery,  // shipping_type
      models::CustomFilterType::kAny,   // block_type
  };

  const auto modifier = PlusMeta(
      config,
      Cashback{
          {models::PlaceId(1), std::numeric_limits<double>::infinity()},
          {models::PlaceId(2), std::numeric_limits<double>::max()},
          {models::PlaceId(3), std::numeric_limits<double>::min()},
      },
      {});

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 1);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "inf%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 2);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "1.79769e+308%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }

  {
    PlaceListItem target{};
    models::PlaceInfo place_info;
    const auto place = CreatePlace(place_info, 3);
    modifier.Modify(target, place, context);

    ASSERT_EQ(1, target.payload.data.meta.size());

    const auto& actual = target.payload.data.meta.front().payload;
    ASSERT_TRUE(std::holds_alternative<YandexPlusMeta>(actual));

    YandexPlusMeta expected{};
    expected.text = "2.22507e-308%";
    expected.icon_url = "asset://yandex-plus";
    expected.styles.border = true;
    expected.styles.rainbow = true;

    AssertEqual(expected, std::get<YandexPlusMeta>(actual));
  }
}

}  // namespace handlers::internal_v1_catalog_for_layout::post::render
