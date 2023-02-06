#include "driver_profile_builder_test.hpp"

#include <mongo/names/dbdrivers.hpp>

namespace names = utils::mongo::db::drivers;

DriverProfileBuilder::DriverProfileBuilder(const std::string& park_id,
                                           const std::string& driver_id) {
  builder.append(names::kParkId, park_id);
  builder.append(names::kDriverId, driver_id);
}

DriverProfileBuilder& DriverProfileBuilder::LastName(
    const std::string& last_name) {
  builder.append(names::kLastName, last_name);
  return *this;
}

DriverProfileBuilder& DriverProfileBuilder::FirstName(
    const std::string& first_name) {
  builder.append(names::kFirstName, first_name);
  return *this;
}

DriverProfileBuilder& DriverProfileBuilder::MiddleName(
    const std::string& middle_name) {
  builder.append(names::kMiddleName, middle_name);
  return *this;
}

DriverProfileBuilder& DriverProfileBuilder::License(
    const std::string& license) {
  builder.append(names::kLicense, license);
  return *this;
}
DriverProfileBuilder& DriverProfileBuilder::LicenseNormalized(
    const std::string& license) {
  builder.append(names::kLicenseNormalized, license);
  return *this;
}
DriverProfileBuilder& DriverProfileBuilder::Phones(
    std::initializer_list<std::string> phones) {
  mongo::BSONArrayBuilder phones_builder;
  for (const auto& phone : phones) {
    phones_builder.append(phone);
  }
  builder.append(names::kPhones, phones_builder.arr());
  return *this;
}

models::DriverProfile DriverProfileBuilder::Build() {
  return models::DriverProfile{builder.obj()};
}
