#include <gtest/gtest.h>

#include <chrono>

#include <classification/models/vehicles_first_order_date.hpp>

TEST(VehiclesFirstOrderDateCheck, Serializer) {
  using namespace classification::models;
  using namespace std::chrono_literals;

  const std::string kNumber1 = "number_1", kNumber2 = "number_2";
  VehiclesFirstOrderDateMap model{};
  model[kNumber1] = std::chrono::system_clock::now();
  model[kNumber2] = std::chrono::system_clock::now() + 10h;

  const auto model_restored =
      Parse(Serialize(model, formats::serialize::To<std::string>{}),
            formats::parse::To<VehiclesFirstOrderDateMap>{});
  EXPECT_EQ(model.size(), model_restored.size());

  EXPECT_EQ(std::chrono::duration_cast<std::chrono::seconds>(
                model.at(kNumber1) - model_restored.at(kNumber1))
                .count(),
            0);

  EXPECT_EQ(std::chrono::duration_cast<std::chrono::seconds>(
                model.at(kNumber2) - model_restored.at(kNumber2))
                .count(),
            0);
}
