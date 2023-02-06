#include <gtest/gtest.h>

#include <contractor_transport/models/contractor_transport.hpp>

namespace contractor_transport::models {
bool operator==(const TransportActive& left, const TransportActive& right) {
  return left.type == right.type && left.vehicle_id == right.vehicle_id;
}
}  // namespace contractor_transport::models

TEST(ContractorTransportTest, Serializer) {
  using namespace contractor_transport::models;
  ContractorsTransportMap model{};
  auto id1 = std::make_shared<ContractorId>("contractor1");
  auto id2 = std::make_shared<ContractorId>("contractor2");
  model[id1] = std::make_shared<TransportActive>(TransportActive{
      clients::contractor_transport::TransportType::kPedestrian, {}});
  model[id2] = std::make_shared<TransportActive>(
      TransportActive{clients::contractor_transport::TransportType::kCar,
                      VehicleId{"car_id_1"}});

  auto model_restored =
      Parse(Serialize(model, formats::serialize::To<std::string>{}),
            formats::parse::To<ContractorsTransportMap>{});
  EXPECT_EQ(model.size(), model_restored.size());
  EXPECT_EQ(*model[id1], *model_restored[id1]);
  EXPECT_EQ(*model[id2], *model_restored[id2]);
}
