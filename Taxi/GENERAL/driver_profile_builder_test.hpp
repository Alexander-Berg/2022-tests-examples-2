#pragma once

#include <string>

#include <helpers/car_builder_test.hpp>
#include <models/driver_profile.hpp>

const std::string kTestDriverId = "test_driver_id";

class DriverProfileBuilder {
 public:
  explicit DriverProfileBuilder(const std::string& park_id = kTestParkId,
                                const std::string& driver_id = kTestDriverId);
  DriverProfileBuilder(const DriverProfileBuilder&) = delete;
  DriverProfileBuilder& operator=(const DriverProfileBuilder&) = delete;

  DriverProfileBuilder& LastName(const std::string& last_name);
  DriverProfileBuilder& FirstName(const std::string& first_name);
  DriverProfileBuilder& MiddleName(const std::string& middle_name);
  DriverProfileBuilder& License(const std::string& license);
  DriverProfileBuilder& LicenseNormalized(const std::string& license);
  DriverProfileBuilder& Phones(std::initializer_list<std::string> phones);

  models::DriverProfile Build();

 private:
  mongo::BSONObjBuilder builder;
};
