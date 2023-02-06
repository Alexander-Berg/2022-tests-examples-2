#include <models/serialization/deserialize.hpp>
#include <models/serialization/serialize.hpp>

#include <random>

#include <gtest/gtest.h>

namespace {

using price_calc::models::CategoryPricesEx;
using price_calc::models::RidePrices;
using price_calc::models::TransferPrices;
using price_calc::models::WaitingPrice;
using price_calc::models::serialization::DeserializeCategoryPricesEx;
using price_calc::models::serialization::DeserializeGeoarea;
using price_calc::models::serialization::Serialize;

double RandDouble(double min, double max) {
  double d = (double)rand() / RAND_MAX;
  return min + d * (max - min);
}

int RandInt(int min, int max) { return rand() % (max - min) + min; }

bool RandBool() { return RandInt(0, 1000000) <= 500000; }

std::string RandString(size_t length = RandInt(2, 20)) {
  std::string result;
  for (size_t i = 0; i < length; ++i) {
    result += static_cast<char>(RandInt('A', 'z' + 1));
  }
  return result;
}

RidePrices RandRidePrices() {
  RidePrices result;
  return result;
}

TransferPrices RandTransferPrices() {
  TransferPrices result;
  result.boarding_price = RandDouble(0.0, 100000.0);
  result.minimum_price = RandDouble(0.0, 100000.0);
  result.ride = RandRidePrices();
  return result;
}

CategoryPricesEx RandCategoryPricesEx() {
  CategoryPricesEx result;
  result.boarding_price = RandDouble(0.0, 1000.0);
  result.minimum_price = RandDouble(0.0, 1000.0);

  for (int i = 0, rides_count = RandInt(2, 15); i < rides_count; ++i) {
    result.rides.emplace(RandString(), RandRidePrices());
  }

  if (RandBool()) {
    result.transfer_prices = RandTransferPrices();
  }

  return result;
}

std::pair<std::string, price_calc::models::Polygon> RandGeoarea() {
  using price_calc::models::Point;
  using price_calc::models::Polygon;

  std::vector<Point> points;
  for (int i = 0, points_count = RandInt(3, 10000); i < points_count; ++i) {
    points.emplace_back(
        Point{RandDouble(-1000.0, 1000.0), RandDouble(-1000.0, 1000.0)});
  }
  return std::make_pair(
      RandString(), Polygon(std::move(points), RandDouble(10.0, 1000000.0)));
}

}  // namespace

namespace price_calc::models {

bool operator==(const WaitingPrice& lhs, const WaitingPrice& rhs) {
  return lhs.free_waiting_time == rhs.free_waiting_time &&
         lhs.price_per_minute == rhs.price_per_minute;
}

bool operator==(const PriceInterval& lhs, const PriceInterval& rhs) {
  return lhs.begin == rhs.begin && lhs.end == rhs.end && lhs.price == rhs.price;
}

bool operator==(const RidePrices& lhs, const RidePrices& rhs) {
  return lhs.dist_price_intervals == rhs.dist_price_intervals &&
         lhs.time_price_intervals == rhs.time_price_intervals;
}

// Comparing only fields which are serialized/deserialized
bool operator==(const TransferPrices& lhs, const TransferPrices& rhs) {
  return lhs.boarding_price == rhs.boarding_price &&
         lhs.minimum_price == rhs.minimum_price && lhs.ride == rhs.ride;
}

// Comparing only fields which are serialized/deserialized
bool operator==(const CategoryPricesEx& lhs, const CategoryPricesEx& rhs) {
  return lhs.boarding_price == rhs.boarding_price &&
         lhs.minimum_price == rhs.minimum_price && lhs.rides == rhs.rides &&
         lhs.transfer_prices == rhs.transfer_prices;
}

bool operator==(const Point& lhs, const Point& rhs) {
  return lhs.lon == rhs.lon && lhs.lat == rhs.lat;
}

bool operator==(const Polygon& lhs, const Polygon& rhs) {
  return lhs.GetPoints() == rhs.GetPoints() && lhs.GetArea() == rhs.GetArea();
}

}  // namespace price_calc::models

TEST(Serialization, CategoryPricesEx) {
  static const int kTestsCount = 1000;

  for (int i = 0; i < kTestsCount; ++i) {
    const auto prices = RandCategoryPricesEx();
    EXPECT_EQ(prices, DeserializeCategoryPricesEx(Serialize(prices)));
  }
}

TEST(Serialization, Geoarea) {
  static const int kTestsCount = 1000;

  for (int i = 0; i < kTestsCount; ++i) {
    const auto geoarea = RandGeoarea();
    EXPECT_EQ(geoarea,
              DeserializeGeoarea(Serialize(geoarea.first, geoarea.second)));
  }
}

TEST(Serialization, DeserializeBadData) {
  price_calc::models::BinaryData data;
  data.push_back(0x44);
  data.push_back(0x33);
  data.push_back(0x22);
  EXPECT_THROW(DeserializeGeoarea(data), std::invalid_argument);
}
