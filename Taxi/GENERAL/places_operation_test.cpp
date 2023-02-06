#include "places_operation.hpp"

#include "models/catalog.hpp"

#include <gtest/gtest.h>
namespace {
namespace utils = eats_restapp_marketing::utils;
namespace catalog = eats_restapp_marketing::models::catalog;
using Place = catalog::Place;

TEST(IsDuplicate, IsDuplicate) {
  ASSERT_FALSE(catalog::IsDuplicate(Place{}, Place{}));
  // дубликат, т. к. разные типы доставки, одинаковая локация и бренд
  ASSERT_TRUE(catalog::IsDuplicate(
      Place{
          1,                                    // id
          catalog::DeliveryType::kMarketplace,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          2,                               // id
          catalog::DeliveryType::kNative,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      }));
  // НЕ дубликат, т. к. одинаковый тип
  // доставки, не смотря на одинаковую локация и бренд
  ASSERT_FALSE(catalog::IsDuplicate(
      Place{
          1,                                    // id
          catalog::DeliveryType::kMarketplace,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          2,                                    // id
          catalog::DeliveryType::kMarketplace,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      }));
  // не дубликат, разные точки
  ASSERT_FALSE(catalog::IsDuplicate(
      Place{
          1,                                    // id
          catalog::DeliveryType::kMarketplace,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          2,                               // id
          catalog::DeliveryType::kNative,  // type
          geometry::Position{geometry::Longitude{4.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      }));
  // не дубликат, разный бренд
  ASSERT_FALSE(catalog::IsDuplicate(
      Place{
          1,                                    // id
          catalog::DeliveryType::kMarketplace,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          2,                               // id
          catalog::DeliveryType::kNative,  // type
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {2, "two"},                                   // brand
      }));
}

TEST(PlacesOperation, FilteringDuplicatePlaces_Emptylist) {
  // два сета пустых
  ASSERT_TRUE(utils::FilteringDuplicatePlaces({}, {}).empty());
  // один из сетов пустой
  ASSERT_TRUE(utils::FilteringDuplicatePlaces({Place{}}, {}).empty());
  ASSERT_TRUE(utils::FilteringDuplicatePlaces({}, {Place{}}).empty());
  //
}

TEST(PlacesOperation, FilteringDuplicatePlaces_No_intersections) {
  // два сета пустых
  auto first = std::unordered_set<Place>{
      Place{
          1,  // id
          catalog::DeliveryType::kMarketplace,
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          2,  // id
          catalog::DeliveryType::kMarketplace,
          geometry::Position{geometry::Longitude{13.0},
                             geometry::Latitude{14.0}},  // point
          {2, "two"},                                    // brand
      }};
  auto second = std::unordered_set<Place>{
      Place{
          3,  // id
          catalog::DeliveryType::kMarketplace,
          geometry::Position{geometry::Longitude{3.0},
                             geometry::Latitude{4.0}},  // point
          {1, "one"},                                   // brand
      },
      Place{
          4,  // id
          catalog::DeliveryType::kMarketplace,
          geometry::Position{geometry::Longitude{13.0},
                             geometry::Latitude{14.0}},  // point
          {2, "two"},                                    // brand
      }};
  // сеты одинаковые
  ASSERT_TRUE(utils::FilteringDuplicatePlaces(first, first).empty());
  // сеты не пересекаются
  ASSERT_TRUE(utils::FilteringDuplicatePlaces(first, second).empty());
}

TEST(PlacesOperation, FilteringDuplicatePlaces_intersections) {
  // два сета пустых
  auto p1 = Place{
      1,  // id
      catalog::DeliveryType::kMarketplace,
      geometry::Position{geometry::Longitude{3.0},
                         geometry::Latitude{4.0}},  // point
      {1, "one"},                                   // brand
  };
  auto p2 = Place{
      2,  // id
      catalog::DeliveryType::kMarketplace,
      geometry::Position{geometry::Longitude{13.0},
                         geometry::Latitude{14.0}},  // point
      {2, "two"},                                    // brand
  };
  auto p3 = Place{
      3,  // id
      catalog::DeliveryType::kNative,
      geometry::Position{geometry::Longitude{3.0},
                         geometry::Latitude{4.0}},  // point
      {1, "one"},                                   // brand
  };
  auto p4 = Place{
      4,  // id
      catalog::DeliveryType::kMarketplace,
      geometry::Position{geometry::Longitude{13.0},
                         geometry::Latitude{14.0}},  // point
      {2, "two"},                                    // brand
  };
  auto first = std::unordered_set<Place>{p1, p2};
  auto second = std::unordered_set<Place>{p3, p4};
  // сеты пересекаются в одном месте
  auto res = utils::FilteringDuplicatePlaces(first, second);
  ASSERT_FALSE(res.empty());
  ASSERT_EQ(res[p1], p3);
}

}  // namespace
