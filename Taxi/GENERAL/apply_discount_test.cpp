#include <gtest/gtest.h>

#include "apply_discount.hpp"

TEST(ApplyDiscount, NoDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(1000));

  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, HasDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(600));

  services[0].cost = 100;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, WithoutTotal) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(services, std::nullopt);

  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, ProductsCostIsZero) {
  std::vector<handlers::Service> services{{
      ::handlers::ServiceType::kDelivery,  // service_type
      ::grocery_pricing::Numeric(1),       // quantity
      ::grocery_pricing::Numeric(500),     // cost
  }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(500));
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, ProductsCostIsZero2) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(500));

  services[0].cost = 0;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, TotalCostLessDeliveryCost) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(499));

  services[0].cost = 0;
  services[1].cost = 499;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, TotalCostLessDeliveryCost2) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(400),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(499));

  services[0].cost = 0;
  services[1].cost = 0;
  services[2].cost = 499;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, TotalCostLessDeliveryCost3) {
  std::vector<handlers::Service> services{{
      ::handlers::ServiceType::kDelivery,  // service_type
      ::grocery_pricing::Numeric(1),       // quantity
      ::grocery_pricing::Numeric(500),     // cost
  }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(499));

  services[0].cost = 499;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, FullProductsDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(1000));

  services[0].cost = 0;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, FullDeliveryDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(500));

  services[0].cost = 0;
  services[1].cost = 0;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, FullServiceFeeDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result =
      eats_plus::utils::ApplyDiscount(services, ::grocery_pricing::Numeric(0));

  services[0].cost = 0;
  services[1].cost = 0;
  services[2].cost = 0;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, PartialProductsDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(1100));

  services[0].cost = 100;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, PartialDeliveryDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(600));

  services[0].cost = 0;
  services[1].cost = 100;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, PartialServiceFeeDiscount) {
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(500),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(500),     // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(500),       // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric(100));

  services[0].cost = 0;
  services[1].cost = 0;
  services[2].cost = 100;
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, WithoutDeliveryFee) {
  // Products cost is 1050
  // Total cost of products without fees is 892.5
  // Decreasing products cost coefficient should be 892.5/1050 = 0.85
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(270),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(370),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(410),    // cost
      },
      {
          ::handlers::ServiceType::kServiceFee,  // service_type
          ::grocery_pricing::Numeric(1),         // quantity
          ::grocery_pricing::Numeric(44),        // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric::FromFloatInexact(936.5));

  services[0].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[0].cost.ToDoubleInexact() * 0.85);
  services[1].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[1].cost.ToDoubleInexact() * 0.85);
  services[2].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[2].cost.ToDoubleInexact() * 0.85);
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, WithoutServiceFee) {
  // Products cost is 1050
  // Total cost of products without fees is 892.5
  // Decreasing products cost coefficient should be 892.5/1050 = 0.85
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(270),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(370),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(410),    // cost
      },
      {
          ::handlers::ServiceType::kDelivery,  // service_type
          ::grocery_pricing::Numeric(1),       // quantity
          ::grocery_pricing::Numeric(44),      // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric::FromFloatInexact(936.5));

  services[0].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[0].cost.ToDoubleInexact() * 0.85);
  services[1].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[1].cost.ToDoubleInexact() * 0.85);
  services[2].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[2].cost.ToDoubleInexact() * 0.85);
  ASSERT_EQ(result, services);
}

TEST(ApplyDiscount, WithoutServiceAndDeliveryFees) {
  // Total cart cost is 892.5
  // Products cost is 1050
  // Total cost of products without fees is 892.5
  // Decreasing products cost coefficient should be 892.5/1050 = 0.85
  std::vector<handlers::Service> services{
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(270),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(370),    // cost
      },
      {
          ::handlers::ServiceType::kProduct,  // service_type
          ::grocery_pricing::Numeric(1),      // quantity
          ::grocery_pricing::Numeric(410),    // cost
      }};
  auto result = eats_plus::utils::ApplyDiscount(
      services, ::grocery_pricing::Numeric::FromFloatInexact(892.5));

  services[0].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[0].cost.ToDoubleInexact() * 0.85);
  services[1].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[1].cost.ToDoubleInexact() * 0.85);
  services[2].cost = ::grocery_pricing::Numeric::FromFloatInexact(
      services[2].cost.ToDoubleInexact() * 0.85);
  ASSERT_EQ(result, services);
}
