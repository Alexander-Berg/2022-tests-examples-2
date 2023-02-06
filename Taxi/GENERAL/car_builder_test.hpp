#pragma once

#include <models/car.hpp>

const std::string kTestParkId = "test_park_id";
const std::string kTestCarId = "test_car_id";

class CarBuilder {
 public:
  explicit CarBuilder(const std::string& park_id = kTestParkId,
                      const std::string& car_id = kTestCarId);
  CarBuilder(const CarBuilder&) = delete;
  CarBuilder& operator=(const CarBuilder&) = delete;

  CarBuilder& VIN(const std::string& vin);
  CarBuilder& LicenseType(const std::string& license_type);
  CarBuilder& Brand(const std::string& brand);
  CarBuilder& Model(const std::string& model);
  CarBuilder& NormalizedNumber(const std::string& number);
  CarBuilder& CallSign(const std::string& call_sign);
  CarBuilder& PermitDoc(const std::string& doc);
  CarBuilder& PermitNum(const std::string& num);
  CarBuilder& PermitSeries(const std::string& series);
  CarBuilder& RegistrationCertificate(const std::string& certificate);

  models::Car Build();

 private:
  mongo::BSONObjBuilder builder;
};
