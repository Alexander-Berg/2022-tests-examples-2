#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>
#include <utils/json_serializers.hpp>
#include <utils/unique_ptr.hpp>
#include "constructor.hpp"

TEST(ConstructorTest, SerializeSimple) {
  models::constructor::Screen sc;
  sc.title = "Test title";

  auto item1 = std::make_unique<models::constructor::DefaultItem>();
  item1->center = false;
  item1->title = "Item 1 title";
  item1->subtitle = "Item 1 subtitle";
  sc.items.push_back(std::move(item1));

  auto item2 = std::make_unique<models::constructor::DetailItem>();
  item2->title = "Item 2 title";
  item2->subtitle = "Item 2 subtitle";
  item2->detail = "Item 2 detail";
  item2->subdetail = "Item 2 subdetail";

  sc.items.push_back(std::move(item2));

  auto json = serializers::Serialize(sc, true);
  EXPECT_EQ(
      json,
      "{\"actions\":[],\"items\":[{\"center\":false,\"subtitle\":\"Item 1 "
      "subtitle\",\"title\":\"Item 1 "
      "title\",\"type\":\"default\"},{\"detail\":\"Item 2 "
      "detail\",\"subdetail\":\"Item 2 subdetail\",\"subtitle\":\"Item 2 "
      "subtitle\",\"title\":\"Item 2 "
      "title\",\"type\":\"detail\"}],\"title\":\"Test title\"}");
}

TEST(ConstructorTest, SerializeDoubleSection) {
  models::constructor::Screen sc;
  sc.title = "Test title";

  auto left_item = std::make_unique<models::constructor::DefaultItem>();
  left_item->center = false;
  left_item->title = "Item 1 title";
  left_item->subtitle = "Item 1 subtitle";

  auto right_item = std::make_unique<models::constructor::DetailItem>();
  right_item->title = "Item 2 title";
  right_item->subtitle = "Item 2 subtitle";
  right_item->detail = "Item 2 detail";
  right_item->subdetail = "Item 2 subdetail";

  auto item = std::make_unique<models::constructor::DoubleSectionItem>();
  item->left = std::move(left_item);
  item->right = std::move(right_item);

  sc.items.push_back(std::move(item));

  auto json = serializers::Serialize(sc, true);

  EXPECT_EQ(json,
            "{\"actions\":[],\"items\":[{\"left\":{\"center\":false,"
            "\"subtitle\":\"Item 1 "
            "subtitle\",\"title\":\"Item 1 "
            "title\",\"type\":\"default\"},\"right\":{\"detail\":\"Item 2 "
            "detail\",\"subdetail\":\"Item 2 subdetail\",\"subtitle\":\"Item 2 "
            "subtitle\",\"title\":\"Item 2 "
            "title\",\"type\":\"detail\"},\"type\":\"double_section\","
            "\"vertical_divider_type\":\"full\"}],\"title\":\"Test title\"}");
}

TEST(ConstructorTest, SerializeCarDetailsPayload) {
  models::constructor::Screen sc;
  sc.title = "Test title";

  auto main_item = std::make_unique<models::constructor::DefaultItem>();
  main_item->center = false;
  main_item->title = "Main title";
  main_item->subtitle = "Main subtitle";

  auto payload = std::make_unique<models::constructor::CarDetailsPayload>();
  payload->title = "Payload title";
  payload->subtitle = "Payload subtitle";

  auto car_item = std::make_unique<models::constructor::IconDetailItem>();
  car_item->title = "Car title";
  car_item->subtitle = "Car subtitle";
  car_item->left_icon = models::constructor::LeftIcon();
  car_item->left_icon->icon_type = models::constructor::LeftIconType::TaxiLogo;

  payload->items.push_back(std::move(car_item));
  main_item->payload = std::move(payload);

  sc.items.push_back(std::move(main_item));

  auto json = serializers::Serialize(sc, true);

  EXPECT_EQ(json,
            "{\"actions\":[],\"items\":[{\"center\":false,\"payload\":{"
            "\"items\":[{\"left_icon\":{"
            "\"icon_type\":\"taxi_logo\"},\"subtitle\":\"Car "
            "subtitle\",\"title\":\"Car "
            "title\",\"type\":\"icon_detail\"}],\"subtitle\":\"Payload "
            "subtitle\",\"title\":\"Payload "
            "title\",\"type\":\"navigate_car_details\"},\"subtitle\":\"Main "
            "subtitle\",\"title\":\"Main "
            "title\",\"type\":\"default\"}],\"title\":\"Test title\"}");
}
