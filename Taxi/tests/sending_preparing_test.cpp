#include <userver/utest/utest.hpp>

#include <clients/eats-core-restapp/client_gmock.hpp>
#include <components/sending_preparing.hpp>

namespace testing {

using ::eats_restapp_communications::components::sending_preparing::
    ComponentImpl;

struct SendingPreparingTest : public Test {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_restapp_core_mock;

  ComponentImpl component;
  eats_restapp_communications::types::Recipient recipient{
      {}, {}, {}, {1, 2}, {}};

  static clients::eats_core_restapp::Item PlaceMenuItem(
      const std::string& id, const std::string& name, bool available,
      std::optional<std::string> reactivated_at) {
    clients::eats_core_restapp::Item item;
    item.id = id;
    item.name = name;
    item.available = available;
    if (reactivated_at.has_value()) {
      item.reactivatedat = ::utils::datetime::Stringtime(*reactivated_at);
    }
    return item;
  }

  static clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::
      Response
      BuildCoreResponse(std::vector<clients::eats_core_restapp::Item> items) {
    clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
        response;
    response.is_success = true;
    response.payload.menu.items = items;
    return response;
  }

  static formats::json::Value BuildNewArgs(
      std::vector<clients::eats_core_restapp::Item> new_items,
      std::vector<clients::eats_core_restapp::Item> old_items) {
    formats::json::ValueBuilder new_items_builder(formats::json::Type::kArray);
    for (const auto& item : new_items) {
      formats::json::ValueBuilder item_builder;
      item_builder["name"] = item.name;
      if (item.reactivatedat.has_value()) {
        item_builder["reactivated_at"] = *item.reactivatedat;
      }
      new_items_builder.PushBack(item_builder.ExtractValue());
    }
    formats::json::ValueBuilder old_items_builder(formats::json::Type::kArray);
    for (const auto& item : old_items) {
      formats::json::ValueBuilder item_builder;
      item_builder["name"] = item.name;
      if (item.reactivatedat.has_value()) {
        item_builder["reactivated_at"] = *item.reactivatedat;
      }
      old_items_builder.PushBack(item_builder.ExtractValue());
    }
    formats::json::ValueBuilder result;
    result["new_stoped_items"] = new_items_builder.ExtractValue();
    result["old_stoped_items"] = old_items_builder.ExtractValue();
    return result.ExtractValue();
  }

  static formats::json::Value BuildOldArgs(
      std::vector<clients::eats_core_restapp::Item> items) {
    formats::json::ValueBuilder items_builder(formats::json::Type::kArray);
    for (const auto& item : items) {
      items_builder.PushBack(item.id);
    }
    formats::json::ValueBuilder result;
    result["stoped_items"] = items_builder.ExtractValue();
    return result.ExtractValue();
  }

  clients::eats_core_restapp::Item i1 = PlaceMenuItem("1", "name_1", true, {});
  clients::eats_core_restapp::Item i2 = PlaceMenuItem("2", "name_2", false, {});
  clients::eats_core_restapp::Item i3 =
      PlaceMenuItem("3", "name_3", true, "2022-04-14T09:00:00+0000");
  clients::eats_core_restapp::Item i4 =
      PlaceMenuItem("4", "name_4", false, "2022-04-14T09:00:00+0000");
  clients::eats_core_restapp::Item i5 = PlaceMenuItem("5", "name_5", true, {});
  clients::eats_core_restapp::Item i6 = PlaceMenuItem("6", "name_6", false, {});
  clients::eats_core_restapp::Item i7 =
      PlaceMenuItem("7", "name_7", true, "2022-04-14T09:00:00+0000");
  clients::eats_core_restapp::Item i8 =
      PlaceMenuItem("8", "name_8", false, "2022-04-14T09:00:00+0000");

  SendingPreparingTest() : component(eats_restapp_core_mock) {}
};

TEST_F(SendingPreparingTest, other_event_type) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(0);
  formats::json::Value args;
  formats::json::Value expected_args;
  component.BeforeSend("other_event_type", recipient, args);
  ASSERT_EQ(args, expected_args);
}

TEST_F(SendingPreparingTest, empty_place_ids) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .Times(0);
  formats::json::Value args;
  ASSERT_THROW(
      component.BeforeSend(
          "stop-menu-items",
          eats_restapp_communications::types::Recipient{"", {}, {}}, args),
      eats_restapp_communications::components::sending_preparing::
          PlaceMenuError);
}

TEST_F(SendingPreparingTest, error_from_eats_restapp_core) {
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  response.is_success = false;
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  formats::json::Value args;
  ASSERT_THROW(component.BeforeSend("stop-menu-items", recipient, args),
               eats_restapp_communications::components::sending_preparing::
                   PlaceMenuError);
}

TEST_F(SendingPreparingTest, wrong_arg_format) {
  clients::eats_core_restapp::v1_eats_restapp_menu_place_menu::get::Response
      response;
  response.is_success = false;
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(response));
  formats::json::ValueBuilder args_builder;
  formats::json::ValueBuilder stoped_items(formats::json::Type::kArray);
  args_builder["stoped_items"] = stoped_items.ExtractValue();
  formats::json::Value args = args_builder.ExtractValue();
  ASSERT_THROW(component.BeforeSend("stop-menu-items", recipient, args),
               eats_restapp_communications::components::sending_preparing::
                   PlaceMenuError);
}

TEST_F(SendingPreparingTest, empty_args) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(BuildCoreResponse({i1, i2, i3, i4, i5, i6, i7, i8})));
  formats::json::Value args = BuildOldArgs({});
  ASSERT_THROW(component.BeforeSend("stop-menu-items", recipient, args),
               eats_restapp_communications::components::sending_preparing::
                   CancellSending);
}

TEST_F(SendingPreparingTest, empty_response) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(BuildCoreResponse({})));
  formats::json::Value args = BuildOldArgs({i2, i4, i6, i8});
  ASSERT_THROW(component.BeforeSend("stop-menu-items", recipient, args),
               eats_restapp_communications::components::sending_preparing::
                   CancellSending);
}

TEST_F(SendingPreparingTest, dont_return_available_items) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(BuildCoreResponse({i4, i5, i8})));
  formats::json::Value args = BuildOldArgs({i4, i5, i8});
  formats::json::Value new_args = BuildNewArgs({i4, i8}, {});
  component.BeforeSend("stop-menu-items", recipient, args);
  ASSERT_EQ(args, new_args);
}

TEST_F(SendingPreparingTest, firstly_items_from_arg) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(BuildCoreResponse({i1, i2, i3, i4, i5, i6, i7, i8})));
  formats::json::Value args = BuildOldArgs({i4, i5, i8});
  formats::json::Value new_args = BuildNewArgs({i4, i8}, {i2, i6});
  component.BeforeSend("stop-menu-items", recipient, args);
  ASSERT_EQ(args, new_args);
}

TEST_F(SendingPreparingTest, common_case) {
  EXPECT_CALL(eats_restapp_core_mock, V1EatsRestappMenuPlaceMenu(_, _))
      .WillOnce(Return(BuildCoreResponse({i1, i2, i3, i4, i5, i6, i7})));
  formats::json::Value args = BuildOldArgs({i4, i5, i8});
  formats::json::Value new_args = BuildNewArgs({i4}, {i2, i6});
  component.BeforeSend("stop-menu-items", recipient, args);
  ASSERT_EQ(args, new_args);
}

}  // namespace testing
