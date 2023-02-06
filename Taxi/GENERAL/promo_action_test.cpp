#include "promo_action.hpp"

#include <memory>
#include <optional>

#include <optional>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace handlers::internal_v1_catalog_for_layout::post::render {

namespace {

namespace models = eats_catalog::models;
namespace edapp = eats_discounts_applicator;
namespace keys = eats_catalog::localization::keys;

const std::vector<ThemedColorA> kDefaultColor{
    {
        Theme::kDark,  // theme
        "#5AC31A",     // value
    },
    {
        Theme::kLight,  // theme
        "#5AC31A",      // value
    },
};

const std::unordered_map<eats_catalog::localization::TankerKey, std::string>
    kTranslations = {
        {keys::c4l::actions::promo::kButtonTitle, "Посмотреть всё"},
};

const models::Context& MakeContext() {
  const auto localizer =
      eats_catalog::localization::MakeTestLocalizer(kTranslations);
  static const models::Context context{
      {},            // request
      std::nullopt,  // offer
      localizer,     // localizer
  };
  return context;
}

models::Place CreatePlace(models::PlaceInfo& place_info, int id, bool surge) {
  place_info.id = models::PlaceId(id);
  models::Place place{place_info};
  place.surge.level = surge ? 1 : 0;

  return place;
}

void AssertEqual(const PromoAction& lhs, const PromoAction& rhs) {
  ASSERT_EQ(lhs.icon_url, rhs.icon_url);
  ASSERT_EQ(lhs.title, rhs.title);
  ASSERT_EQ(lhs.description, rhs.description);
  ASSERT_EQ(lhs.accent_color, rhs.accent_color);
  ASSERT_EQ(lhs.extended.has_value(), rhs.extended.has_value());

  if (lhs.extended.has_value()) {
    ASSERT_EQ(lhs.extended->title, rhs.extended->title);
    ASSERT_EQ(lhs.extended->content, rhs.extended->content);
    ASSERT_EQ(lhs.extended->button, rhs.extended->button);
  }
}

}  // namespace

TEST(PromoAction, Simple) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();

  const Context context{
      models::ShippingType::kDelivery,  // shipping_type
      models::CustomFilterType::kAny,   // block_type
  };

  ::caches::PlacePromos promos{
      {
          models::PlaceId(1),
          std::vector<models::Promo>{
              {
                  1,             // id
                  "test1",       // title
                  std::nullopt,  // description
                  {
                      1,             // id
                      "test promo",  // title
                      std::nullopt,  // picture
                      std::nullopt,  // detailed_picture
                  },                 // type
                  false,             // disabled_by_surge
                  500,               // score
                  std::nullopt,      // discount_threshold
              },
              {
                  2,                    // id
                  "test2",              // title
                  "promo description",  // description
                  {
                      2,                         // id
                      "test",                    // title
                      "http://picture",          // picture
                      "http://detaild_picture",  // detailed_picture
                  },                             // type
                  false,                         // disabled_by_surge
                  600,                           // score
                  std::nullopt,                  // discount_threshold
              },
              {
                  3,                               // id
                  "test-with-surge",               // title
                  "promo description with surge",  // description
                  {
                      3,                                    // id
                      "test",                               // title
                      "http://picture-with-surge",          // picture
                      "http://detaild_picture_with_surge",  // detailed_picture
                  },                                        // type
                  true,                                     // disabled_by_surge
                  400,                                      // score
                  std::nullopt,  // discount_threshold
              },
          },
      },
  };
  std::unordered_map<int64_t, std::vector<models::Promo>> new_discounts{
      {
          1,
          std::vector<models::Promo>{
              {
                  101,                                // id
                  "subway_free_delivery",             // title
                  "free delivery promo description",  // description
                  {
                      101,                       // id
                      "free_delivery_discount",  // title
                      "http://picture",          // picture
                      "http://picture",          // detailed_picture
                  },                             // type
                  false,                         // disabled_by_surge
                  300,                           // score
                  std::nullopt,                  // discount_threshold
              },
          },
      },
  };

  eats_catalog::models::NewPromos new_discounts_pickup{};

  const auto modifier = PromoActionModifier(
      MakeContext(), config,
      eats_catalog::models::AllPromos{
          std::make_shared<::caches::PlacePromos>(promos),  // promo_cache
          std::make_shared<eats_catalog::models::NewPromos>(
              new_discounts),  // new_discounts_delivery
          std::make_shared<eats_catalog::models::NewPromos>(
              new_discounts_pickup),  // new_discounts_pickup
          std::nullopt,               // exp_old_discounts_filter
          {},                         // map_promo_types
          {},
          std::nullopt,   // free delivery_badge
          std::nullopt,   // excluded_tag
          std::nullopt},  // context
      [](auto&) {});      // promo_sorter

  std::vector<PromoAction> expected{};
  {
    InfoActionExtended extended{};
    extended.title = "subway_free_delivery";
    extended.content = "free delivery promo description";
    extended.button = {"Посмотреть всё"};

    auto& action = expected.emplace_back();
    action.icon_url = "http://picture";
    action.title = "subway_free_delivery";
    action.description = "free delivery promo description";
    action.accent_color = kDefaultColor;
    action.extended = std::move(extended);
  }
  {
    InfoActionExtended extended{};
    extended.title = "test1";
    extended.content = "";
    extended.button = {"Посмотреть всё"};

    auto& action = expected.emplace_back();
    action.icon_url = "";
    action.title = "test1";
    action.description = "";
    action.accent_color = kDefaultColor;
    action.extended = std::move(extended);
  }
  {
    InfoActionExtended extended{};
    extended.title = "test2";
    extended.content = "promo description";
    extended.button = {"Посмотреть всё"};

    auto& action = expected.emplace_back();
    action.icon_url = "http://picture";
    action.title = "test2";
    action.description = "promo description";
    action.accent_color = kDefaultColor;
    action.extended = std::move(extended);
  }

  PlaceListItem target{};
  models::PlaceInfo place_info;
  const auto place = CreatePlace(place_info, 1, true);
  modifier.Modify(target, place, context);

  ASSERT_EQ(expected.size(), target.payload.data.actions.size());

  for (size_t i = 0; i < expected.size(); ++i) {
    const auto& actual = target.payload.data.actions[i].payload;
    ASSERT_TRUE(std::holds_alternative<PromoAction>(actual));
    AssertEqual(expected[i], std::get<PromoAction>(actual));
  }
}

}  // namespace handlers::internal_v1_catalog_for_layout::post::render
