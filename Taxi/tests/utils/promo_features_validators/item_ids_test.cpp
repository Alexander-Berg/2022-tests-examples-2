#include <clients/eats-core-restapp/client_gmock.hpp>
#include <userver/utest/utest.hpp>

#include <types/settings.hpp>
#include <utils/promo_features_validators/item_ids.hpp>

namespace eats_restapp_promo::utils {
using namespace ::testing;

TEST(GetMenuItems, core_return_unsuccess_response) {
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  response.is_success = false;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  ASSERT_THROW(GetMenuItems(eats_core_restapp, {1, {1, 2}}),
               models::ValidationError);
}

TEST(GetMenuItems, core_return_success_response) {
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  response.is_success = true;
  clients::eats_core_restapp::Item item1, item2, item5;
  item1.id = "item1";
  item1.name = "name1";
  item1.categoryid = "category_id1";
  item1.menuitemid = 1;
  item2.id = "item2";
  item2.name = "name2";
  item2.categoryid = "category_id2";
  item2.menuitemid = 2;
  item5.id = "item5";
  item5.name = "name5";
  item5.categoryid = "category_id5";
  item5.menuitemid = 5;
  response.payload.menu.items = {item1, item2, item5};
  clients::eats_core_restapp::MenuCategory menu_category1, menu_category2,
      menu_category5;
  menu_category1.id = "category_id1";
  menu_category1.name = "category1";
  menu_category2.id = "category_i2";
  menu_category2.name = "category2";
  menu_category5.id = "category_id5";
  menu_category5.name = "category5";
  response.payload.menu.categories = {menu_category1, menu_category2,
                                      menu_category5};
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  types::ItemsMap expected_result = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item2", {2, "name2", "category_id2", "category2"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  ASSERT_EQ(GetMenuItems(eats_core_restapp, {1, {1, 2}}), expected_result);
}

TEST(GetItemsByOriginItemsIds,
     thow_exception_if_origin_item_ids_not_in_core_items) {
  types::ItemsMap core_items = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item2", {2, "name2", "category_id2", "category2"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  types::ItemIds item_ids = {"item3", "item4"};
  ASSERT_THROW(GetItemsByOriginItemsIds(core_items, item_ids),
               models::ValidationError);
}

TEST(GetItemsByOriginItemsIds, thow_exception_if_menu_item_id_is_nullopt) {
  types::ItemsMap core_items = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item2", {{}, "name2", "category_id2", "category2"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  types::ItemIds item_ids = {"item2"};
  ASSERT_THROW(GetItemsByOriginItemsIds(core_items, item_ids),
               models::ValidationError);
}

TEST(GetItemsByOriginItemsIds, thow_exception_if_origin_item_ids_is_empty) {
  types::ItemsMap core_items = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item2", {{}, "name2", "category_id2", "category2"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  types::ItemIds item_ids;
  ASSERT_THROW(GetItemsByOriginItemsIds(core_items, item_ids),
               models::ValidationError);
}

TEST(GetItemsByOriginItemsIds, return_items_for_origin_item_ids) {
  types::ItemsMap core_items = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item2", {{}, "name2", "category_id2", "category2"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  types::ItemsMap expexted_result = {
      {"item1", {1, "name1", "category_id1", "category1"}},
      {"item5", {5, "name5", "category_id5", "category5"}}};
  types::ItemIds item_ids = {"item1", "item2", "item5", "item6"};
  ASSERT_EQ(GetItemsByOriginItemsIds(core_items, item_ids), expexted_result);
}

struct ValidatationItemIdsData {
  models::PromoInfo configuration;
};

class ValivatationItemIdsWithoutFeatureDataFull
    : public ::testing::TestWithParam<ValidatationItemIdsData> {};

const std::vector<ValidatationItemIdsData>
    kValivatationItemIdsWithoutFeatureData{
        {models::SettingsPromoType::kPlusFirstOrders},
        {models::SettingsPromoType::kPlusHappyHours},
        {models::SettingsPromoType::kFreeDelivery}};

INSTANTIATE_TEST_SUITE_P(
    ValidatationItemIdsData, ValivatationItemIdsWithoutFeatureDataFull,
    ::testing::ValuesIn(kValivatationItemIdsWithoutFeatureData));

TEST_P(ValivatationItemIdsWithoutFeatureDataFull,
       DontThrowExceptionForOtherPromos) {
  auto param = GetParam();
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids;
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, param.configuration, {},
                                  item_ids, items));
  item_ids = types::ItemIds{"1", "2"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, param.configuration, {},
                                  item_ids, items));
}

struct ValidationTest : public Test {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  types::RequestInfo request_info;
  ValidationTest() {
    response.is_success = true;
    clients::eats_core_restapp::Item item1, item2, item5;
    item1.id = "item1";
    item1.name = "name1";
    item1.categoryid = "category_id1";
    item1.menuitemid = 1;
    item2.id = "item2";
    item2.name = "name2";
    item2.categoryid = "category_id2";
    item2.menuitemid = {};
    item5.id = "item5";
    item5.name = "name5";
    item5.categoryid = "category_id5";
    item5.menuitemid = 5;
    response.payload.menu.items = {item1, item2, item5};
    clients::eats_core_restapp::MenuCategory menu_category1, menu_category2,
        menu_category5;
    menu_category1.id = "category_id1";
    menu_category1.name = "category1";
    menu_category2.id = "category_i2";
    menu_category2.name = "category2";
    menu_category5.id = "category_id5";
    menu_category5.name = "category5";
    response.payload.menu.categories = {menu_category1, menu_category2,
                                        menu_category5};
    request_info.place_ids = {1, 2};
  }
};

TEST_F(ValidationTest, gift_throw_exception_for_invalis_size) {
  models::PromoInfo settings = {models::SettingsPromoType::kGift};
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"1", "2"};
  ASSERT_THROW(
      ValidateItemIds(eats_core_restapp, settings, {}, item_ids, items),
      models::ValidationError);
  item_ids = types::ItemIds{};
  ASSERT_THROW(
      ValidateItemIds(eats_core_restapp, settings, {}, item_ids, items),
      models::ValidationError);
}

TEST_F(ValidationTest, gift_throw_exception_for_unknown_item) {
  models::PromoInfo settings = {models::SettingsPromoType::kGift};
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item3"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, settings, request_info,
                               item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, gift_throw_exception_if_menu_item_id_is_nullopt) {
  models::PromoInfo settings = {models::SettingsPromoType::kGift};
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item2"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, settings, request_info,
                               item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, gift_throw_exception_for_invalid_category) {
  models::PromoInfo settings = {models::SettingsPromoType::kGift};
  types::ValueItemIdConfiguration value_settings;
  value_settings.disabled_categories = {"category10", "category5"};
  settings.configuration.item_id = value_settings;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item5"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, settings, request_info,
                               item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, gift_dont_throw_exception) {
  models::PromoInfo settings = {models::SettingsPromoType::kGift};
  types::ValueItemIdConfiguration value_settings;
  value_settings.disabled_categories = {"category1", "category10"};
  settings.configuration.item_id = value_settings;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemsMap> expectes_items =
      types::ItemsMap{{"item5", {5, "name5", "category_id5", "category5"}}};
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item5"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, settings, request_info,
                                  item_ids, items));
  ASSERT_EQ(items, expectes_items);
}

TEST_F(ValidationTest,
       gift_dont_throw_exception_for_empty_disabled_categories) {
  models::PromoInfo gift_settings = {models::SettingsPromoType::kGift};
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemsMap> expectes_items =
      types::ItemsMap{{"item5", {5, "name5", "category_id5", "category5"}}};
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item5"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, gift_settings,
                                  request_info, item_ids, items));
  ASSERT_EQ(items, expectes_items);
}

TEST(ValidateItemIds, check_one_plus_one_and_discount_for_empty_feature) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids;
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, discount_settings, {},
                                  item_ids, items));
  item_ids = std::nullopt;
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings, {},
                               item_ids, items),
               models::ValidationError);
}

TEST(ValidateItemIds, throw_exception_for_invalid_items_size) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item1"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, discount_settings, {},
                               item_ids, items),
               models::ValidationError);
  item_ids = types::ItemIds{"item1"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings, {},
                               item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, throw_exception_if_core_return_error) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  response.is_success = false;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item1", "item2"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                               request_info, item_ids, items),
               models::ValidationError);
  item_ids = types::ItemIds{"item1", "item2"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                               request_info, item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, throw_exception_for_invalid_item) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item3"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                               request_info, item_ids, items),
               models::ValidationError);
  item_ids = types::ItemIds{"item3"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                               request_info, item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, throw_exception_if_menu_item_id_is_nullopt) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item2"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                               request_info, item_ids, items),
               models::ValidationError);
  item_ids = types::ItemIds{"item2"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                               request_info, item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, throw_exception_for_disables_categories) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  settings.disabled_categories = {"category10", "category5"};
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item1", "item5"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                               request_info, item_ids, items),
               models::ValidationError);
  item_ids = types::ItemIds{"item1", "item5"};
  ASSERT_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                               request_info, item_ids, items),
               models::ValidationError);
}

TEST_F(ValidationTest, dont_throw_exception_for_enough_enables_categories) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 1;
  settings.disabled_categories = {"category10", "category5"};
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<std::unordered_map<std::string, types::MenuItem>> items;
  std::optional<types::ItemIds> item_ids = types::ItemIds{"item1", "item5"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                                  request_info, item_ids, items));
  item_ids = types::ItemIds{"item1", "item5"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                                  request_info, item_ids, items));
}

TEST_F(ValidationTest, dont_throw_exception) {
  models::PromoInfo discount_settings = {models::SettingsPromoType::kDiscount};
  models::PromoInfo one_plus_one_settings = {
      models::SettingsPromoType::kOnePlusOne};
  types::ValueItemIdsConfiguration settings;
  settings.min_items = 2;
  settings.disabled_categories = {"category10", "category2"};
  discount_settings.configuration.item_ids =
      one_plus_one_settings.configuration.item_ids = settings;
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  EXPECT_CALL(eats_core_restapp, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(2)
      .WillOnce(Return(response))
      .WillOnce(Return(response));
  std::optional<types::ItemsMap> discount_items, one_plus_one_items;
  std::optional<types::ItemsMap> expected_items =
      types::ItemsMap{{"item1", {1, "name1", "category_id1", "category1"}},
                      {"item5", {5, "name5", "category_id5", "category5"}}};
  std::optional<types::ItemIds> item_ids =
      types::ItemIds{"item1", "item2", "item5", "item6"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, discount_settings,
                                  request_info, item_ids, discount_items));
  item_ids = types::ItemIds{"item1", "item2", "item5", "item6"};
  ASSERT_NO_THROW(ValidateItemIds(eats_core_restapp, one_plus_one_settings,
                                  request_info, item_ids, one_plus_one_items));
  ASSERT_EQ(discount_items, expected_items);
  ASSERT_EQ(discount_items, expected_items);
}

}  // namespace eats_restapp_promo::utils
